from entity.database import Database as DatabaseEntity

from ..model import Model
from jinja2 import Template


class Database(Model):
    def __init__(self):
        self.imname = "inthumod"
        self.omname = "database"
        self.ometype = DatabaseEntity
        self.order = 0
        pass

    def digitToLetter(self, digit):
        alphabet = "abcdefghijklmnopqrstuvwxyz"
        return alphabet[digit]
    
    def designTable(self):
        for dtd in self.imodel.dtds.values():
            table = {"name": "", "correspondence": ""}

            table["name"] = dtd.name
            table["correspondence"] = self.digitToLetter(self.order)
            self.order += 1

            self.omodel.table.append(table)
    
    def designAttributeName(self):
        for dtd in self.imodel.dtds.values():
            attributes = {"table": dtd.name, "attributes": []}
            for field in dtd.fields.items():
                if isinstance(field[1], dict):
                    for item in field[1].keys():
                        attributes["attributes"].append({
                            "name": item,
                            "correspondence": self.digitToLetter(self.order),
                        })
                        self.order += 1
                
                else:
                    attributes["attributes"].append({
                        "name": field[0],
                        "correspondence": self.digitToLetter(self.order),
                    })
                    self.order += 1
            
            self.omodel.attributeName.append(attributes)

    def designAttributeType(self):
        for dtd in self.imodel.dtds.values():
            attributes = {"table": dtd.name, "attributes": []}
            for field in dtd.fields.items():
                if isinstance(field[1], dict):
                    for item in field[1].items():
                        if item[1] == "bool":
                            attributes["attributes"].append({
                                "name": item[0],
                                "type": "boolean",
                            })
                        else:
                            attributes["attributes"].append({
                                "name": item[0],
                                "type": "string",
                            })
                
                else:
                    if field[1] == "bool":
                        attributes["attributes"].append({
                            "name": field[0],
                            "type": "boolean",
                        })
                    else:
                        attributes["attributes"].append({
                            "name": field[0],
                            "type": "string",
                        })
            
            self.omodel.attributeType.append(attributes)
    
    def merge(self):
        for i in range(len(self.omodel.table)):
            table = {"name": "", "correspondence": "", "attribute": []}

            table["name"] = self.omodel.table[i]["name"]
            table["correspondence"] = self.omodel.table[i]["correspondence"]

            for j in range(len(self.omodel.attributeName[i]["attributes"])):
                attribute = {"name": "", "correspondence": "", "type": ""}
                
                attribute["name"] = self.omodel.attributeName[i]["attributes"][j]["name"]
                attribute["correspondence"] = self.omodel.attributeName[i]["attributes"][j]["correspondence"]
                
                attribute["type"] = self.omodel.attributeType[i]["attributes"][j]["type"]

                table["attribute"].append(attribute)

            self.omodel.context["tables"].append(table)
            
    def formTemplate(self):
        self.omodel.template = Template('''
module.exports = function (fastify, opts) {
    return {
        async up (knex) {
            {% for table in tables %}
            await knex.schema
            // {{ table.name }}表
            .createTable('{{ table.correspondence }}', function (table) {
                // 主键
                table.uuid('id', { primaryKey: true }).defaultTo(knex.raw('gen_random_uuid()'))
                {% for attribute in table.attribute %}
                // {{ attribute.name }}
                table.{{ attribute.type }}('{{ attribute.correspondence }}')
                {% endfor %}
            })
            {% endfor %}
        }
    }
}''')

    def dotransform(self, store):
        self.designTable()
        self.designAttributeName()
        self.designAttributeType()
        self.merge()
        self.formTemplate()
        self.omodel.template = self.omodel.template.render(self.omodel.context)
        return store
