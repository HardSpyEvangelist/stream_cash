from odoo import models, fields, api
from odoo.exceptions import UserError

class StreamCashDeclarationNotesLine(models.Model):
    _name = "stream_cash_declarations_notes.line"
    _description = " Stream Cash Declaration Notes Line"

    declaration_lines_id = fields.Many2one('stream_cash.declaration.line',string="Declaration")
    declaration_type_id = fields.Many2one('declaration.type', string='Declaration Type')

    amount = fields.Monetary(string="Amount")
    currency_id = fields.Many2one('res.currency',string="Currency")
    exchange_rate = fields.Float(string="Exchange Rate",related='currency_id.rate',readonly=True)
    currency_usd = fields.Many2one('res.currency', string="Base Currency",default=lambda self: self.env.company.currency_id)
    company_id = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.company)
    amount_usd = fields.Monetary(string="Amount (USD)",compute="_compute_amount_usd",store=True)
    
    #cash fields
    denomination_id = fields.Many2one('currency.denomination',string="Denomination")
    count = fields.Integer(string="Count")
    denomination_value = fields.Float(related='denomination_id.value', string="Denomination Value")
    denomination_name = fields.Char(related='denomination_id.name', string="Denomination Name")
    
    
    # New transaction type field
    transaction_type_id = fields.Many2one('stream_cash_transaction.type', string="Transaction Type")
    
    #credit notes fields
    partner_id = fields.Many2one('res.partner', string='Account Name')

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

    @api.onchange('count')
    def _onchange_count(self):
        for line in self:
            line.amount = line.count * line.denomination_value


    def unlink(self):
        for record in self:
            parent_state = record.declaration_lines_id.declaration_id.state
            if parent_state != 'Draft':
                raise UserError("You can only delete lines when the declaration is in Draft state.")
        return super().unlink()

    def copy(self, default=None):
        for record in self:
            parent_state = record.declaration_lines_id.declaration_id.state
            if parent_state != 'Draft':
                raise UserError("You can only duplicate lines when the declaration is in Draft state.")
        return super().copy(default)
    
    def write(self, vals):
        for record in self:
            if record.declaration_lines_id.declaration_id.state != 'Draft':
                raise UserError("You can only modify records when the declaration is in Draft state.")
        return super(StreamCashDeclarationNotesLine, self).write(vals)