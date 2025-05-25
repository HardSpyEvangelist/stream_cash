from odoo import models, fields

class DeclarationType(models.Model):
    _name = "declaration.type"
    _description = "Declaration Type"

    name = fields.Char(string="Name", required=True)
   