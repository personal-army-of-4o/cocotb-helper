from nmigen.hdl.dsl import _ModuleBuilderDomain as b


def fix_semantix():
    def mysetattr(self, name, val):
        if name == "_domain":
            self.__dict__[name] = val
        else:
            if name in self._builder.__dict__:
                self.__iadd__(self._builder.__dict__[name].eq(val))
            else:
                raise Exception("couldn't find {} signal on the module".format(name))
    setattr(b, "__setattr__", mysetattr)

