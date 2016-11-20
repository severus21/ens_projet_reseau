import sched, time
import logging

from threading import Thread, RLock, Event

from .misc import Task

class Scheduler(Thread):
    def __init__(self, tasks):
        Thread.__init__(self)

        self.tasks = tasks
        self.s = sched.scheduler(time.time, time.sleep)
        
        self.s.enter(30, 1, 
            lambda x=None:self.tasks.appendleft((Task.contact_u_n,)))
        self.s.enter(90, 1, 
            lambda x=None:self.tasks.appendleft((Task.ihu_s_n,)))
        self.s.enter(60, 1, 
            lambda x=None:self.tasks.appendleft((Task.check_neighborgs,)))
        self.s.enter(10, 1, 
            lambda x=None:self.tasks.appendleft((Task.prune_neighborgs,)))
        self.s.enter(25*60, 1, 
            lambda x=None:self.tasks.appendleft((Task.update_data,)))
        self.s.enter(5*60, 1, 
            lambda x=None:self.tasks.appendleft((Task.prune_data,)))
   
    def run(self):
        logging.debug("Scheduler started")
        self.s.run()
