from odoo import models, fields, api

class TransactionType(models.Model):
    _name = "stream_cash_transaction.type"
    _description = " Stream Cash Transaction Type"
    _rec_name = 'name'
    _order = 'declaration_type_id, sequence, name'

    name = fields.Char(string="Transaction Type Name", required=True)
    declaration_type_id = fields.Many2one('declaration.type', string='Declaration Type', required=True)
    declaration_type_name = fields.Char(related='declaration_type_id.name', string="Declaration Type Name", store=True)
    applicable_currency_id = fields.Many2one('res.currency', string='Applicable Currency', required=False, help="Leave empty to make this transaction type available for all currencies")
    sequence = fields.Integer(string="Sequence", default=10)
    active = fields.Boolean(string="Active", default=True)
    
    _sql_constraints = [
        ('name_declaration_type_currency_uniq', 'unique(name, declaration_type_id, COALESCE(applicable_currency_id, 0))', 
         'Transaction type name must be unique per declaration type and currency combination!'),
    ]

    # @api.model
    # def create_default_transaction_types(self):
    #     """Create default transaction types for existing declaration types"""
    #     # Get declaration types and currencies
    #     declaration_types = self.env['declaration.type'].search([])
    #     usd_currency = self.env['res.currency'].search([('name', '=', 'USD')], limit=1)
    #     zig_currency = self.env['res.currency'].search([('name', '=', 'ZWG')], limit=1)
        
    #     # Default transaction types mapping with currencies
    #     default_types = {
    #         'Voucher': [
    #             ('Issued', usd_currency.id if usd_currency else False),
    #             ('Redeemed', usd_currency.id if usd_currency else False),
    #         ],
    #         'Credit Card': [
    #             ('EFT', usd_currency.id if usd_currency else False),
    #             ('OFFLINE', usd_currency.id if usd_currency else False),
    #             ('EFT', zig_currency.id if zig_currency else False),
    #             ('OFFLINE', zig_currency.id if zig_currency else False),
    #         ],
    #         'Pickup': [
    #             (f'Pickup{i}', usd_currency.id if usd_currency else False) for i in range(1, 11)
    #         ],
    #     }
        
    #     for declaration_type in declaration_types:
    #         if declaration_type.name in default_types:
    #             existing_types = self.search([
    #                 ('declaration_type_id', '=', declaration_type.id)
    #             ])
                
    #             if not existing_types:
    #                 sequence = 10
    #                 for type_name, currency_id in default_types[declaration_type.name]:
    #                     if currency_id:  # Only create if currency exists
    #                         self.create({
    #                             'name': type_name,
    #                             'declaration_type_id': declaration_type.id,
    #                             'applicable_currency_id': currency_id,
    #                             'sequence': sequence,
    #                         })
    #                         sequence += 10
