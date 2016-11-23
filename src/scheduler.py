import sched, time
import logging

from threading import Thread, RLock, Event

from .misc import Task

class Scheduler(Thread):
    def __init__(self, tasks):
        Thread.__init__(self)

        self.tasks = tasks
        self.s = sched.scheduler(time.time, time.sleep)
        
    
       # self.s.enter(30, 1, 
        #    lambda x=None:self.tasks.appendleft((Task.contact_u_n,None)))
        #self.s.enter(90, 1, 
        #    lambda x=None:self.tasks.appendleft((Task.ihu_s_n,None)))
        #self.s.enter(60, 1, 
        #    lambda x=None:self.tasks.appendleft((Task.check_neighborgs,None)))
        #self.s.enter(10, 1, 
        #    lambda x=None:self.tasks.appendleft((Task.prune_neighborgs,None)))
        #self.s.enter(25*60, 1, 
        #    lambda x=None:self.tasks.appendleft((Task.update_data,None)))
        #self.s.enter(5*60, 1, 
        #    lambda x=None:self.tasks.appendleft((Task.prune_data,None)))
    
    def contact_u_n(self):
        self.tasks.appendleft((Task.contact_u_n,None))
        self.s.enter(30, 1, self.contact_u_n)
    
    def ihu_s_n(self):
        self.tasks.appendleft((Task.ihu_s_n,None))
        self.s.enter(90, 1, self.ihu_s_n)
    
    def check_neighborgs(self):
        self.s.enter(60, 1, self.check_neighborgs)
        self.tasks.appendleft((Task.check_neighborgs,None))
     
    def prune_neighborgs(self):
        self.s.enter(10, 1, self.prune_neighborgs) 
        self.tasks.appendleft((Task.prune_neighborgs,None))
        
    def update_data(self):      
        self.s.enter(30, 1, self.update_data)
        #self.s.enter(25*60, 1, self.update_data)
        self.tasks.appendleft((Task.update_data,None))
    
    def prune_data(self):    
        self.s.enter(5*60, 1, self.prune_data)
        self.tasks.appendleft((Task.prune_data,None))

    def refresh_ihm(self):
        self.s.enter(1, 1, self.refresh_ihm)
        self.tasks.appendleft((Task.refresh_ihm, None))

    def run(self):
        self.contact_u_n()
        self.ihu_s_n()
        self.check_neighborgs()
        self.prune_neighborgs()
        self.update_data()
        self.prune_data()
        self.refresh_ihm()

        logging.debug("Scheduler started")
        self.s.run()
