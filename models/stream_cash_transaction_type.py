from odoo import models, fields, api

class TransactionType(models.Model):
    _name = "stream_cash_transaction.type"
    _description = " Stream Cash Transaction Type"
    _rec_name = 'name'
    _order = 'declaration_type_id, sequence, name'

    name = fields.Char(string="Transaction Type Name", required=True)
    declaration_type_id = fields.Many2one('declaration.type', string='Declaration Type', required=True)
    declaration_type_name = fields.Char(related='declaration_type_id.name', string="Declaration Type Name", store=True)
    sequence = fields.Integer(string="Sequence", default=10)
    active = fields.Boolean(string="Active", default=True)
    
    _sql_constraints = [
        ('name_declaration_type_uniq', 'unique(name, declaration_type_id)', 
         'Transaction type name must be unique per declaration type!'),
    ]

    @api.model
    def create_default_transaction_types(self):
        """Create default transaction types for existing declaration types"""
        # Get declaration types
        declaration_types = self.env['declaration.type'].search([])
        
        # Default transaction types mapping
        default_types = {
            'Voucher': ['issued', 'redeemed'],
            'Credit Card': ['EFT - USD', 'OFFLINE - USD', 'EFT - ZiG', 'OFFLINE - ZiG'],
            'Pickup': [f'pickup{i}' for i in range(1, 11)],
        }
        
        for declaration_type in declaration_types:
            if declaration_type.name in default_types:
                existing_types = self.search([
                    ('declaration_type_id', '=', declaration_type.id)
                ])
                
                if not existing_types:
                    sequence = 10
                    for type_name in default_types[declaration_type.name]:
                        self.create({
                            'name': type_name,
                            'declaration_type_id': declaration_type.id,
                            'sequence': sequence,
                        })
                        sequence += 10