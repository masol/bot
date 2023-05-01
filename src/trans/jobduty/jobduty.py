from entity.jobduty import JobDuty as JobDutyEntity

from ..model import Model


class JobDuty(Model):
    def __init__(self):
        self.imname = 'humod'
        self.omname = 'jobduty'
        self.ometype = JobDutyEntity
        pass


    def dotransform(self, store):
        return store
