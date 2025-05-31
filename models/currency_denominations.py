from odoo import models, fields, api

class CurrencyDenomination(models.Model):
    _name = "currency.denomination"
    _description = "Currency Denomination"
    
    name = fields.Char(string="Name", required=True)
    value = fields.Float(string="Value", required=True)
    currency_id = fields.Many2one('res.currency', string="Currency", required=True, ondelete='cascade')
    active = fields.Boolean(default=True)
    
    # This makes sure denomination names include the currency
    @api.depends('name', 'currency_id.name')
    def name_get(self):
        result = []
        for denomination in self:
            name = f"{denomination.name} ({denomination.currency_id.name})" if denomination.currency_id else denomination.name
            result.append((denomination.id, name))
        return result