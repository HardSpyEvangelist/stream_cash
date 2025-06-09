# declarations_line.py - Updated version
from odoo import models, fields, api

class StreamCashDeclarationLine(models.Model):
    _name = "stream_cash.declaration.line"
    _description = " Stream Cash Declaration Line"

    declaration_notes_line_ids = fields.One2many('stream_cash_declarations_notes.line','declaration_lines_id', string="Declaration Notes")
    declaration_id = fields.Many2one('stream_cash.declarations',string="Declaration",required=True,ondelete='cascade')
    
    declaration_type_ids = fields.Many2one('declaration.type', string='Declaration Type', required=True, readonly=True)
    declaration_type_name = fields.Char(string="Declaration Type Name",related="declaration_type_ids.name",store=True )
    declaration_type_state = fields.Selection(related="declaration_id.state")
    currency_id = fields.Many2one('res.currency', string="Currency")
    currency_usd = fields.Many2one('res.currency',string="Base Currency",help="This field ensures compatibility with monetary fields",default=lambda self: self.env.company.currency_id)
    company_id = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.company)
    amount = fields.Monetary(
        string='Amount',
        compute='_compute_total_amount',
        store=True,
        currency_field='currency_usd')    
    exchange_rate = fields.Float(string="Exchange Rate", related='currency_id.rate', digits=(12, 6))
    amount_usd = fields.Monetary(string="Amount (USD)", compute='_compute_amount_usd', store=True)
    denomination_id = fields.Many2one('currency.denomination', string='Denomination')

    related_is_cash = fields.Boolean(related='declaration_type_ids.is_cash', store=True)
    related_is_partner = fields.Boolean(related='declaration_type_ids.is_partner', store=True)
    related_is_negate = fields.Boolean(related='declaration_type_ids.is_negate', store=True)

    

    @api.depends('declaration_notes_line_ids.amount')
    def _compute_total_amount(self):
        for rec in self:
            if rec.declaration_type_ids.name == 'Voucher':
                issued =   sum(l.amount for l in rec.declaration_notes_line_ids
                             if l.transaction_type_id.name == 'Issued')
                redeemed = sum(l.amount for l in rec.declaration_notes_line_ids
                               if l.transaction_type_id.name == 'Redeemed')
                net = redeemed + issued
                rec.amount = -net if rec.related_is_negate else net
            else:
                total = sum(l.amount for l in rec.declaration_notes_line_ids)
                rec.amount = total


    @api.depends('amount', 'currency_id')
    def _compute_amount_usd(self):
        for record in self:
            if record.currency_id and record.currency_usd:
                record.amount_usd = record.currency_id._convert(
                    record.amount,
                    record.currency_usd,
                    record.company_id,
                    record.create_date,
                )
            else:
                record.amount_usd = 0.0

    def action_open_declaration_lines_notes(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'stream_cash.declaration.line',
            'view_mode': 'form',
            'target': 'new',
            'res_id': self.id,

        }
                
    # @api.model
    # def create(self, vals):
    #     """Override create to ensure both currency fields are set"""
    #     if vals.get('currency') and not vals.get('currency_id'):
    #         vals['currency_id'] = vals['currency']
    #     elif vals.get('currency_id') and not vals.get('currency'):
    #         vals['currency'] = vals['currency_id']
    #
    #     # Ensure amount and amount_usd are properly set
    #     if 'amount' in vals and 'exchange_rate' in vals and not vals.get('amount_usd'):
    #         vals['amount_usd'] = vals['amount'] * vals['exchange_rate']
    #
    #     return super(StreamCashDeclarationLine, self).create(vals)

    