import sched, time

from threading import Thread, RLock, Event

class Scheduler(Thread):
    def __init__(self, tasks):
        Thread.__init__(self)

        self.tasks = tasks
        self.s = sched.scheduler(time.time, time.sleep)
        
        self.s.enter(30, 1, lambda x=None:self.tasks.append_left(Task.contact_u_n))
        self.s.enter(90, 1, lambda x=None:self.tasks.append_left(Task.ihu_s_n))
        self.s.enter(60, 1, lambda x=None:self.tasks.append_left(Task.check_neighborgs))
        self.s.enter(30*60, lambda x=None:self.tasks.append_left(Task.update_data))
        self.s.enter(35*60, lambda x=None:self.tasks.append_left(Task.prune_data))
        #innondation todo
   
   def      
   def run(self):
        self.s.run()
