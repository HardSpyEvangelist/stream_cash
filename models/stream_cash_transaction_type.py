from odoo import models, fields, api


class StreamCashTransactionType(models.Model):
    _name = 'stream_cash_transaction.type'
    _description = 'Stream Cash Transaction Type'
    _order = 'sequence, name'

    name = fields.Char(string='Transaction Type', required=True)
    declaration_type_id = fields.Many2one('declaration.type', string='Declaration Type', required=True)
    applicable_currency_id = fields.Many2one('res.currency', string='Applicable Currency', 
                                           help='Leave empty to make available for all currencies')
    sequence = fields.Integer(string='Sequence', default=10)
    active = fields.Boolean(string='Active', default=True)
    is_negate = fields.Boolean(string='Is Negate', default=False,
                              help='Check this to subtract amounts for this transaction type')