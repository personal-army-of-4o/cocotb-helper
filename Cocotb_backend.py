from cocotb import RisingEdge, FallingEdge


class Nmigen_backend:
    def __init__(self, clk, valid, data, ack):
        self._clk = clk
        self.__valid = valid
        self.__data = data
        self.__ack = ack

    def decorator(self, func):
        return cocotb.coroutine(func)

    def get_data(self):
        return self.__data

    def set_data(self, val):
        self.__data = val

    def get_valid(self):
        return self.__valid

    def set_valid(self, val):
        self.__valid = val

    def get_ack(self):
        return self.__ack

    def set_ack(self, val):
        self.__ack = val

    def active_edge(self):
        yield RisingEdge(self.clk)

    def inactive_edge(self):
        yield FallingEdge(self.clk)

