from entity.uipage import UIpage as UIpageEntity

from ..model import Model


class UIpage(Model):
    def __init__(self):
        self.imname = 'jobduty'
        self.omname = 'uipage'
        self.ometype = UIpageEntity
        pass

    #def chooseStyle(self):选择界面风格

    #def genUserAction(self,struct):
    #识别并选择界面风格chooseStyle
    #     for遍历使用流程，识别用户listUser
    #           for对于每个用户，识别行为listAction
    #       生成最终数据结构
    #
    #     两层循环,输出m×n组数据结构struct,m,n

    #def listUser(self):识别用户
    #def listAction(self):识别行为

    #def genTitle(self):生成标题
    #def genBar(self):生成导航栏
    #def genInput(self):生成输入框
    #def genButton(self):生成按钮
    #def genText(self):生成文本展示

    #def ChangeUser(self):切换身份
    #def ChangeStatePre(self):切换上一状态
    #def ChangeStateNext(self):切换下一状态
 
    #def genUI(self,struct):生成界面
    #   userAmount=m, actionAmount=n[m]
    #

    def dotransform(self, store):
        return store
    
   
    
    



