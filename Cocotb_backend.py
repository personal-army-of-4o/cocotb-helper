import cocotb
from cocotb.triggers import RisingEdge, FallingEdge


def gen():
    yield 4

class Cocotb_backend:
    def __init__(self, clk, valid, data, ack):
        self.__clk = clk
        self.__valid = valid
        self.__data = data
        self.__ack = ack

    def decorator(self, func):
        return cocotb.coroutine(func)

    @cocotb.coroutine
    def get_data(self):
        yield gen()
        return self.__data

    def set_data(self, val):
        yield gen()
        self.__data = val

    @cocotb.coroutine
    def get_valid(self):
        yield gen()
        return self.__valid

    @cocotb.coroutine
    def set_valid(self, val):
        yield gen()
        self.__valid = val

    @cocotb.coroutine
    def get_ack(self):
        yield gen()
        return self.__ack

    @cocotb.coroutine
    def set_ack(self, val):
        yield gen()
        self.__ack = val

    def active_edge(self):
        yield RisingEdge(self.__clk)

    def inactive_edge(self):
        yield FallingEdge(self.__clk)

