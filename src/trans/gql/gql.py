from ..model import Model
from jinja2 import Template
from entity.gql import GqlEntity
from attrs import asdict

class Gql(Model):
    def __init__(self):
        self.imname = "inthumod"
        self.omname = "gql"
        self.ometype = GqlEntity
        pass


    def getTpl1(self):
        return Template('''

        type Query {                    
            {% for api in apiQuerys %}
                {{api.name}}({{api.param}}): {{api.ret}}
            {% endfor %}
}
    
        type Mutaion {                    
            {% for api in apiMuts %}
                 {{api.name}}({{api.param}}): {{api.ret}}
            {% endfor %}
}

        {% for queryType in queryTypes %}
        type {{queryType.name}} {
           {% for typeInfo in queryType.types %}
              {{typeInfo.name}}: {{typeInfo.typename}}
           {% endfor %}
        }
        {% endfor %}
''')


    def dotransform(self, store):
        gql = GqlEntity()
        gql.apiQuerys.append({
            "name":"asb",
            "param":"offset:int",
            "ret": "[str]"
        })
        # print(self.imodel)
        tpl = self.getTpl1()
        print(gql)
        result = tpl.render(asdict(gql))
        print("------")
        print(result)
        return store
