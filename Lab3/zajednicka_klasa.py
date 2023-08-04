import pyopencl as cl
import os


class Paralelno_izvodenje:
    def __init__(self, path):
        self.memfag = cl.mem_flags
        self.context = cl.create_some_context(interactive=False)
        self.queue = cl.CommandQueue(self.context)
        __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
        self.code = "".join(open(__location__+"\\"+path, 'r').readlines())
        self.program = cl.Program(self.context, self.code).build()

    def getQueue(self):
        return self.queue
    
    def getProgram(self):
        return self.program

    def getFlags(self):
        return self.memfag
    
    def getContext(self):
        return self.context