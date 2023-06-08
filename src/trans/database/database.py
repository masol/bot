from entity.database import Database as DatabaseEntity

from ..model import Model
from jinja2 import Template


class Database(Model):
    def __init__(self):
        self.imname = "inthumod"
        self.omname = "database"
        self.ometype = DatabaseEntity
        pass

    def digitToLetter(self, digit):
        alphabet = "abcdefghijklmnopqrstuvwxyz"
        return alphabet[digit]
    
    def extractContext(self):
        self.omodel.context = {"tables": []}

        order = 0

        for dtd in self.imodel.dtds.values():
            table_detail = {"name": "", "correspondence": "", "attributes": []}

            table_detail["name"] = dtd.name
            table_detail["correspondence"] = self.digitToLetter(order)
            order += 1

            for field in dtd.fields.items():
                if isinstance(field[1], dict):
                    for item in field[1].keys():
                        table_detail["attributes"].append({
                            "name": item,
                            "type": "str",
                            "correspondence": self.digitToLetter(order)})
                        order += 1
                
                elif field[1] == "bool":
                    table_detail["attributes"].append({
                        "name": field[0],
                        "type": "bool",
                        "correspondence": self.digitToLetter(order)})
                    order += 1
                
                else:
                    table_detail["attributes"].append({
                        "name": field[0],
                        "type": "str",
                        "correspondence": self.digitToLetter(order)})
                    order += 1
            
            self.omodel.context["tables"].append(table_detail)

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
                {% for attribute in table.attributes %}
                // {{ attribute.name }}
                {% if attribute.type == "str" %}
                table.string('{{ attribute.correspondence }}', 32).nullable()
                {% elif attribute.type == "bool" %}
                table.boolean('{{ attribute.correspondence }}').defaultTo(false)
                {% endif %}
                {% endfor %}
            })
            {% endfor %}
        }
    }
}''')

    def dotransform(self, store):
        self.extractContext()
        self.formTemplate()
        self.omodel.template.render(self.omodel.context)
        return store
