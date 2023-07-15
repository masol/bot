from entity.jobduty import JobDuty as JobDutyEntity
from entity.jobduty import Role as RoleEntity
from entity.jobduty import Duty as DutyEntity
from entity.jobduty import Workflow as WorkflowEntity

from ..model import Model
from collections import defaultdict

import copy


class JobDuty(Model):
    def __init__(self):
        self.imname = 'inthumod'
        self.omname = 'jobduty'
        self.ometype = JobDutyEntity
        pass



    def dotransform(self, store):

     
        subj_dict = {}

        
            
        
        for name, wf in self.imodel.wfs.items():
            workflow=WorkflowEntity()
            workflow.name=copy.copy(wf.name)
            # print(f"wfs:{workflow.name}") 
            workflow.roles={}            
         
                                                
            for index, bh in enumerate(wf.behaves):            
                 if bh.subj.name in subj_dict: 
                         subj_dict[bh.subj.name].append(index)
                 else:
                  subj_dict[bh.subj.name]=[index]
                  
            for bh.subj.name,indices in subj_dict.items():
                 role=RoleEntity()
                 role.name=copy.copy(bh.subj.name)
                #  print(f"roles:{role.name}") 
                 role.duties=[]       
                                                                        
                 for index in indices:
                     duty=DutyEntity()
                     duty=copy.copy(index)
                    #  print(f"duties:{duty}")
                     role.duties.append(duty)
                     
                 workflow.roles[role.name]=role
                     
            self.omodel.wfs[workflow.name] = workflow                              
                     
            
        return store
   