from entity.jobduty import JobDuty as JobDutyEntity


from ..model import Model



class JobDuty(Model):
    def __init__(self):
        self.imname = 'inthumod'
        self.omname = 'jobduty'
        self.ometype = JobDutyEntity
        pass



    def dotransform(self, store):

     
        subj_dict = {}
            
        
        for name, wf in self.imodel.wfs.items(): 
           
            for index, bh in enumerate(wf.behaves): 
             role=self.omodel.ensure(bh.subj.name)
             role.append(wf.name,index)
                                                      
                     
            
        return store
   