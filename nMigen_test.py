import random
import itertools
from functools import partial
from nmigen.sim import *
from Nmigen_backend import Nmigen_backend
from Data_interface import Data_interface
import threading


tests = []

def mytest(cls):
    obj = cls()
    tests.append(obj)
    return cls

fail = False

#example init for self.ui for helper child classes
class uut_iface:
    def __init__(self, uut, cfg, verbose = False):
        self.uut = uut
        for i in cfg:
            back = Nmigen_backend(cfg[i][0], cfg[i][1], cfg[i][2], cfg[i][3])
            setattr(self, i, Data_interface(back, verbose = verbose))

#depends on self.ui.w and self.ui.r which are Data_interface instances
class helper:
    def __init__(self, tm = 1000):
        self.timeout = tm
    def get_sim_info(self):
        return [(
            self.__class__.__name__,
            self.get_test_processes()
        )]
    def gen(self, l, end_type="eop"):
        if end_type:
            l = l-1
        seed = 0
        prng = random.Random(seed)
        pkg = (prng.randint(0, 255) for _ in range (l))
        if end_type == "eop":
            pkg = itertools.chain(pkg, iter([256]))
        if end_type == "eep":
            pkg = itertools.chain(pkg, iter([257]))
        return pkg
    def ticks(self, n):
        for i in range(0, n):
            yield Tick()
    def wr(self, pkg, ch = "w"):
        obj = getattr(self.ui, ch)
        yield from obj.Write(pkg)
    def rd(self, pkg, len = 0, ch = "r"):
        obj = getattr(self.ui, ch)
        yield from obj.Read(pkg, len)
    def wait(self, s, v):
        cnt = 0
        while (yield s) == v:
            yield Tick()
            cnt += 1
            if cnt > self.timeout:
                raise Exception("timeout")

def runtests(debug = False):
    parallel = not debug
    dump_waveform = debug
    def runtest(name, sim):
        global fail
        try:
            if dump_waveform:
                with sim.write_vcd(name+".vcd", name+".gtkw", traces=si[1][0].ports()):
                    sim.run()
            else:
                sim.run()
            print("test", name, "passed")
        except:
            print("test", name, "failed")
            fail |= True

    tl = []
    for tt in tests:
        for si in tt.get_sim_info():
            sim = Simulator(si[1][0])
            sim.add_clock(1e-6, domain="sync")
            for sp in si[1][1]:
                sim.add_sync_process(sp)

            if parallel:
                th = threading.Thread(target = partial(runtest, si[0], sim))
                th.start()
                tl.append(th)
            else:
                print("running test", si[0])
                if dump_waveform:
                    with sim.write_vcd(si[0]+".vcd", si[0]+"test.gtkw", traces=si[1][0].ports()):
                        sim.run()
                else:
                    sim.run()
    if parallel:
        for t in tl:
            t.join()
        if fail:
            raise Exception("sim failed")

