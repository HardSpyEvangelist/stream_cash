from odoo import models, fields

class DeclarationType(models.Model):
    _name = "declaration.type"
    _description = "Declaration Type"

    name = fields.Char(string="Name", required=True)
    is_partner = fields.Boolean(string="Is Partner")
    is_cash = fields.Boolean(string="Is Cash")
    is_negate = fields.Boolean(string="Is Negate")
