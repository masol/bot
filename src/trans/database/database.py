from entity.database import Database as DatabaseEntity
from entity.database import Table as TableEntity
from entity.database import String as StringEntity
from entity.database import Boolean as BooleanEntity

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
            table = TableEntity()
            table.name = dtd.name
            table.correspondence = self.digitToLetter(self.order)
            self.order += 1
            table.strings = []
            table.booleans = []

            for field in dtd.fields.items():
                if isinstance(field[1], dict):
                    for item in field[1].items():
                        if item[1] == "bool":
                            attribute = BooleanEntity()
                            attribute.name = item[0]
                            attribute.correspondence = self.digitToLetter(self.order)
                            self.order += 1
                            table.booleans.append(attribute)
                        elif item[1] == "str":
                            attribute = StringEntity()
                            attribute.name = item[0]
                            attribute.correspondence = self.digitToLetter(self.order)
                            self.order += 1
                            table.strings.append(attribute)
                        else:
                            attribute = StringEntity()
                            attribute.name = item[0]
                            attribute.correspondence = self.digitToLetter(self.order)
                            self.order += 1
                            table.strings.append(attribute)
                else:
                    if field[1] == "bool":
                        attribute = BooleanEntity()
                        attribute.name = field[0]
                        attribute.correspondence = self.digitToLetter(self.order)
                        self.order += 1
                        table.booleans.append(attribute)
                    elif field[1] == "str":
                        attribute = StringEntity()
                        attribute.name = field[0]
                        attribute.correspondence = self.digitToLetter(self.order)
                        self.order += 1
                        table.strings.append(attribute)
                    else:
                        attribute = StringEntity()
                        attribute.name = field[0]
                        attribute.correspondence = self.digitToLetter(self.order)
                        self.order += 1
                        table.strings.append(attribute)
            
            self.omodel.tables.append(table)
            
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
                {% for string in table.strings %}
                // {{ string.name }}
                table.string('{{ string.correspondence }}')
                {% endfor %}
                {% for boolean in table.booleans %}
                // {{ boolean.name }}
                table.string('{{ boolean.correspondence }}')
                {% endfor %}
            })
            {% endfor %}
        }
    }
}''')

    def dotransform(self, store):
        self.designTable()
        self.formTemplate()
        self.omodel.template = self.omodel.template.render({"tables": [self.omodel.tables]})
        return store
