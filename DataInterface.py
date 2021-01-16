import itertools
import cocotb
from types import GeneratorType
from cocotb.triggers import FallingEdge, RisingEdge

class DataInterface:
    def __init__(self, clk, valid, data, ack):
        self.clk = clk
        self.valid = valid
        self.data = data
        self.ack = ack

    @cocotb.coroutine
    def Write(self, data):
        if (not isinstance(data, GeneratorType)) and (not isinstance(data, itertools.chain)):
            raise Exception("generator expected as arg (arg is {})".format(type(arg)))
        while True:
            try:
                d = next(data)
                yield FallingEdge(self.clk)
                self.data <= d
                self.valid <= 1
                print("writing ", hex(d), " at ", cocotb.utils.get_sim_time(units="ns"), "ns")
                yield RisingEdge(self.clk)
                while self.ack != 1:
                    yield RisingEdge(self.clk)
            except StopIteration:
                yield FallingEdge(self.clk)
                self.valid <= 0

    @cocotb.coroutine
    def _read_word(self):
        yield RisingEdge(self.clk)
        while self.valid != 1:
            yield RisingEdge(self.clk)
        return self.data

    @cocotb.coroutine
    def Read(self, arg, length = 0):
        yield FallingEdge(self.clk)
        self.ack <= 1
        if isinstance(arg, int):
            raise Exception("not tested")
            ret = []
            for i in range(arg):
                data = yield self._read_word()
                ret.append(data)
            yield FallingEdge(self.clk)
            self.ack <= 0
            return ret
        elif isinstance(arg, GeneratorType) or isinstance(arg, itertools.chain):
            if length == 0:
                while True:
                    try:
                        data = next(arg)
                        print("reading", " at ", cocotb.utils.get_sim_time(units="ns"), "ns expecting ", hex(data))
                        tdata = yield self._read_word()
                        print("got", hex(tdata.value), " at ", cocotb.utils.get_sim_time(units="ns"), "ns")
                        if data != tdata.value:
                            print(hex(data), " neq ", hex(tdata.value))
                            return True
                    except StopIteration:
                        yield FallingEdge(self.clk)
                        self.ack <= 0
            else:
                for i in range(int(length)):
                    try:
                        data = next(arg)
                        print("reading", " at ", cocotb.utils.get_sim_time(units="ns"), "ns expecting ", hex(data))
                        tdata = yield self._read_word()
                        print("got", hex(tdata.value), " at ", cocotb.utils.get_sim_time(units="ns"), "ns")
                        if data != tdata.value:
                            print(hex(data), " neq ", hex(tdata.value))
                            return True
                    except StopIteration:
                        pass
                yield FallingEdge(self.clk)
                self.ack <= 0
            return False
        else:
            raise Exception("either generator or int is expected as arg")
