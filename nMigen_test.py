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
    def __init__(self, uut, verbose):
        self.uut = uut
        self.back_wr = back_wr = Nmigen_backend(None, uut.iValid, uut.iData, uut.oAck)
        self.di_wr = Data_interface(back_wr, verbose = verbose)
        self.back_rd = back_rd = Nmigen_backend(None, uut.oValid, uut.oData, uut.iAck)
        self.di_rd = Data_interface(back_rd, verbose = verbose)


#depends on self.ui.di_wr and self.ui.di_rd which are Data_interface instances
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
    def wr_pkg(self, pkg):
        yield from self.ui.di_wr.Write(pkg)
        cnt = 0
        while (yield self.ui.uut.oOccupied) == 0:
            yield Tick()
            cnt += 1
            if cnt > self.timeout:
                raise Exception("timeout")
    def wait_empty(self):
        cnt = 0
        while (yield self.ui.uut.oOccupied) == 1:
            yield Tick()
            cnt += 1
            if cnt > self.timeout:
                raise Exception("timeout")
    def wait_sent(self):
        cnt = 0
        while (yield self.ui.uut.oDiscarded) == 0:
            yield Tick()
            cnt += 1
            if cnt > self.timeout:
                raise Exception("timeout")
        yield from self.wait_empty()

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

