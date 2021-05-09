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
    def __init__(self, cfg, verbose = False):
        for i in cfg:
            back = Nmigen_backend(cfg[i][0], cfg[i][1], cfg[i][2], cfg[i][3])
            setattr(self, i, Data_interface(back, verbose = verbose))

#depends on self.ui.w and self.ui.r which are Data_interface instances
class helper:
    def __init__(self, tm = 1000):
        self.timeout = tm
    def get_sim_info(self):
        return [[
            self.__class__.__name__,
            self.get_test_processes()
        ]]
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
    def ticks(self, n = 1):
        for i in range(0, n):
            yield Tick()
    def wr(self, pkg, ch = "w"):
        obj = getattr(self.ui, ch)
        yield from obj.Write(pkg)
    def rd(self, pkg, len = 0, fail_on_mismatch = True, ch = "r"):
        obj = getattr(self.ui, ch)
        yield from obj.Read(pkg, len, fail_on_mismatch)
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
                with sim.write_vcd(name+".vcd", name+".gtkw", traces=si[1][0][0].ports()):
                    sim.run()
            else:
                sim.run()
            print("test", name, "passed")
        except:
            print("test", name, "failed")
            fail |= True

    tl = []
    def setup_sim(tt):
        for si in tt:
            print("setting up sim environment for test", si[0])
            uut = si[1][0]
            si[1][0] = (uut, Simulator(si[1][0]))
            sim = si[1][0][1]
            try:
                sim.add_clock(1e-6, domain="sync")
                for sp in si[1][1]:
                    sim.add_sync_process(sp)
            except:
                print('failed to set up clock')
                for sp in si[1][1]:
                    sim.add_process(sp)

    sim_arg_ar = []
    tmp = []
    for tt in tests:
        tmp = []
        for si in tt.get_sim_info():
            tmp.append(si)
        sim_arg_ar.append(tmp)
    for tt in sim_arg_ar:
        th = threading.Thread(target = partial(setup_sim, tt))
        tl.append(th)
    for i in tl:
        i.start()
    for t in tl:
        t.join()

    tl = []
    print("running simulations")
    for tt in sim_arg_ar:
        for si in tt:
            sim = si[1][0][1]
            if parallel:
                th = threading.Thread(target = partial(runtest, si[0], sim))
                th.start()
                tl.append(th)
            else:
                print("running test", si[0])
                if dump_waveform:
                    with sim.write_vcd(si[0]+".vcd", si[0]+".gtkw", traces=si[1][0][0].ports()):
                        sim.run()
                else:
                    sim.run()
    if parallel:
        for t in tl:
            t.join()
        if fail:
            raise Exception("sim failed")

