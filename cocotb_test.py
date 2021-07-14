import cocotb
from cocotb.clock import Clock
from cocotb.triggers import Timer
from cocotb.triggers import FallingEdge
from cocotb.triggers import RisingEdge
from cocotb.triggers import ClockCycles
from cocotb.result import TestFailure
from threading import Thread
from functools import partial


p = []

async def run_task(t):
    t = Thread(target = t)
    t.start()

    i = 0
    print("looping sim to allow the test run")
    while t.is_alive():
        i += 1
        await Timer(10000000, 'step')

    print("waiting for test thread")
    t.join()

def start(l):
    if isinstance(l, list):
        for i in l:
            start(i)
    else:
        for j in l.get_test_processes():
            p.append(cocotb.fork(j()))

def stop():
    print("waiting for uart processes")
    for  i in p:
        i.join()

async def run(pr, *args, **kwargs):
    for i in args:
        start(i)
    for i in kwargs:
        start(kwargs[i])
    await run_task(partial(pr, *args, **kwargs))
    stop()

