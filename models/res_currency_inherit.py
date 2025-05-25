from odoo import models, fields, api

class ResCurrency(models.Model):
    _inherit = 'res.currency'
    
    # Add one-to-many relation to denominations
    denomination_ids = fields.One2many('currency.denomination', 'currency_id', string="Denominations")