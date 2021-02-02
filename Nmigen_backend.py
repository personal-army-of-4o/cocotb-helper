from nmigen.sim import *


class Nmigen_backend:
    def __init__(self, clk, valid, data, ack):
        self._clk = clk
        self.__valid = valid
        self.__data = data
        self.__ack = ack

    def decorator(self, func):
        return func

    def get_data(self):
        return (yield self.__data)

    def set_data(self, val):
        yield self.__data.eq(val)

    def get_valid(self):
        return (yield self.__valid)

    def set_valid(self, val):
        yield self.__valid.eq(val)

    def get_ack(self):
        return (yield self.__ack)

    def set_ack(self, val):
        yield self.__ack.eq(val)

    def active_edge(self):
        yield Tick()

    def inactive_edge(self):
        yield InactiveEdge()

