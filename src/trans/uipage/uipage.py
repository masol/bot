from entity.uipage import UIpage as UIpageEntity

from ..model import Model


class UIpage(Model):
    def __init__(self):
        self.imname = 'jobduty'
        self.omname = 'uipage'
        self.ometype = UIpageEntity
        pass

    #def chooseStyle(self):选择界面风格
    def chooseStyle(self, style_type):
        if style_type == "serious":
            # 设置为严肃风格
            self.setStyleSheet("background-color: #f5f5f5; color: #333333;")
        elif style_type == "relaxed":
            # 设置为轻松风格
            self.setStyleSheet("background-color: #333333; color: #f5f5f5;")
        else:
            # 设置为默认风格
            self.setStyleSheet("")

    #def genUserAction(self,struct):
    #识别并选择界面风格chooseStyle
    #     for遍历使用流程，识别用户listUser
    #           for对于每个用户，识别行为listAction
    #       生成最终数据结构
    #
    #     两层循环,输出m×n组数据结构struct,m,n
    def genUserAction(text):
        # 使用正则表达式提取用户和行为，text是已经被nlp处理过的文本
        user_pattern = r"\[([\w\s]+)\]\s"
        action_pattern = r"\(([\w\s]+)\)"
        users = re.findall(user_pattern, text)
        actions = re.findall(action_pattern, text)

        # 生成二维数组，第一维是用户，第二维是行为
        user_action_matrix = np.empty((len(users), len(actions)), dtype=object)
        for i, user in enumerate(users):
            for j, action in enumerate(actions):
                user_action_matrix[i, j] = f"{user} {action}"

        return user_action_matrix
    # 这个函数接受一个文本参数text，其中包含了一些用户和行为的信息。函数使用正则表达式来提取用户和行为，并将它们存储在两个列表中。然后，函数使用 NumPy 库生成一个二维数组，其中第一维是用户，第二维是行为，数组中的每个元素是一个字符串，表示一个用户和一个行为的组合。最后，函数返回这个二维数组。
    # 请注意，这个函数假设文本中包含了用户和行为的信息，并且用户和行为之间用空格分隔。如果文本中包含了其他的分隔符，你需要相应地修改正则表达式。
    
    #def listUser(self):识别用户
    #def listAction(self):识别行为

    #def genTitle(self):生成标题
    def genTitle(title):
        return f"<h1>{title}</h1>"
    #def genBar(self):生成导航栏
    # ！提取用户的全部一级行为，作为导航栏
    def genBar(description):
        # 使用正则表达式提取导航栏内容
        item_pattern = r"\* (\w+) - (\w+)"
        items = re.findall(item_pattern, description)

        # 生成 HTML 代码
        html = "<ul>"
        for item in items:
            html += f"<li><a href='#{item[0]}'>{item[1]}</a></li>"
        html += "</ul>"

        return html
    #def genInput(self):生成输入框
    def genInput(name, value=None):
        return f"<input type='text' name='{name}' value='{value}'>"
    #def genSelect(self):生成选择器
    def genSelect(name, options, selected=None):
        html = f"<select name='{name}'>"
        for option in options:
            if option == selected:
                html += f"<option value='{option}' selected>{option}</option>"
            else:
                html += f"<option value='{option}'>{option}</option>"
        html += "</select>"
        return html
    #def genButton(self):生成按钮
    def genButton(text, onclick=None):
        return f"<button onclick='{onclick}'>{text}</button>"
    #def genText(self):生成文本展示
    def genText(text):
        return f"<div>{text}</div>"

    #def ChangeUser(self):切换身份
    #def ChangeStatePre(self):切换上一状态
    #def ChangeStateNext(self):切换下一状态
 
    #def genUI(self,struct):生成界面
    #   userAmount=m, actionAmount=n[m]
    #

    def dotransform(self, store):
        return store
    
   
    
    



