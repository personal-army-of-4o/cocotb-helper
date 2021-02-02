import itertools
from types import GeneratorType


DEFAULT_TIMEOUT = 1000

class DataMismatch(Exception):
    pass

class TimeoutException(Exception):
    pass

class Data_interface:
    def __init__(self, back, verbose=False):
        self.back = back
        self.Write = back.decorator(self.Write2)
        self.v = verbose

    def Write2(self, data, timeout = DEFAULT_TIMEOUT):
        if (not isinstance(data, GeneratorType)) and (not isinstance(data, itertools.chain)):
            raise Exception("generator expected as arg (arg is {})".format(type(data)))
        while True:
            try:
                cnt = 0
                d = next(data)
                if (self.v):
                    print("writing ", hex(d))
                yield from self.back.inactive_edge()
                yield from self.back.set_data(d)
                yield from self.back.set_valid(1)
                yield from self.back.active_edge()
                while (yield from self.back.get_ack()) != 1:
                    yield from self.back.active_edge()
                    cnt += 1
                    if cnt > timeout:
                        raise TimeoutException()
            except StopIteration:
                yield from self.back.inactive_edge()
                yield from self.back.set_valid(0)
                return

    def Read(self, arg, length = 0, fail_on_mismatch = True, timeout = DEFAULT_TIMEOUT):
        def exit_ok():
            yield from self.back.inactive_edge()
            yield from self.back.set_ack(0)
            return False
        yield from self.back.inactive_edge()
        yield from self.back.set_ack(1)
        if isinstance(arg, int):
            raise Exception("not tested")
            ret = []
            for i in range(arg):
                data = yield self._read_word()
                ret.append(data)
            yield self.back.inactive_edge()
            self.back.ack = 0
            return ret
        elif isinstance(arg, GeneratorType) or isinstance(arg, itertools.chain):
            words = 0
            while True:
                try:
                    cnt = 0
                    data = next(arg)
                    yield from self.back.active_edge()
                    while (yield from self.back.get_valid()) != 1:
                        yield from self.back.active_edge()
                        cnt += 1
                        if cnt > timeout:
                            raise TimeoutException()
                    tdata = (yield from self.back.get_data())
                    if (self.v):
                        print("got", hex(tdata))
                    if data != tdata:
                        print(hex(data), " neq ", hex(tdata))
                        if fail_on_mismatch:
                            raise DataMismatch()
                        return True
                except StopIteration:
                    return (yield from exit_ok())
                if length > 0:
                    words += 1
                    if words >= length:
                        return (yield from exit_ok())
        else:
            raise Exception("either generator or int is expected as arg")

