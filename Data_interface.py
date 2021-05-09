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
        self.Read = back.decorator(self._read)
        self.Write = back.decorator(self._write)
        self.v = verbose

    def _write(self, data, timeout = DEFAULT_TIMEOUT):
        if (not isinstance(data, GeneratorType)) and (not isinstance(data, itertools.chain)):
            raise Exception("generator expected as arg (arg is {})".format(type(data)))
        while True:
            try:
                cnt = 0
                d = next(data)
                if (self.v):
                    print("writing ", hex(d))
                yield from self.back.inactive_edge()
                try:
                    yield from self.back.set_data(d)
                except:
                    self.back.set_data(d)
                try:
                    yield from self.back.set_valid(1)
                except:
                    self.back.set_valid(1)
                yield from self.back.active_edge()
                try:
                    check = (yield from self.back.get_ack())
                except:
                    check = self.back.get_ack()
                while (check) != 1:
                    yield from self.back.active_edge()
                    try:
                        check = (yield from self.back.get_ack())
                    except:
                        check = self.back.get_ack()
                    cnt += 1
                    if cnt > timeout:
                        raise TimeoutException()
            except StopIteration:
                yield from self.back.inactive_edge()
                try:
                    yield from self.back.set_valid(0)
                except:
                    self.back.set_valid(0)
                return

    def _read(self, arg, length = 0, fail_on_mismatch = True, timeout = DEFAULT_TIMEOUT):
        yield from self.back.inactive_edge()
        try:
            yield from self.back.set_ack(1)
        except:
            self.back.set_ack(1)
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
                    try:
                        check = (yield from self.back.get_valid())
                    except:
                        check = self.back.get_valid()
                    while (check) != 1:
                        yield from self.back.active_edge()
                        try:
                            check = (yield from self.back.get_valid())
                        except:
                            check = self.back.get_valid()
                        cnt += 1
                        if cnt > timeout:
                            raise TimeoutException()
                    try:
                        tdata = (yield from self.back.get_data())
                    except:
                        tdata = self.back.get_data()
                    if (self.v):
                        print("got", hex(tdata))
                    if data != tdata:
                        print("expected", hex(data), " got ", hex(tdata))
                        if fail_on_mismatch:
                            raise DataMismatch()
                except StopIteration:
                    yield from self.back.inactive_edge()
                    try:
                        yield from self.back.set_ack(0)
                    except:
                        self.back.set_ack(0)
                    return False
                if length > 0:
                    words += 1
                    if words >= length:
                        if self.v:
                            print("length limit reached")
                        yield from self.back.inactive_edge()
                        try:
                            yield from self.back.set_ack(0)
                        except:
                            self.back.set_ack(0)
                        return False
        else:
            raise Exception("either generator or int is expected as arg")

