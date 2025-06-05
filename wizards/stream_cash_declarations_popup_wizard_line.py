from odoo import fields, models, api


class CashDeclarationWizardLine(models.TransientModel):
    _name = "stream_cash_declarations_popup_wizard.line"
    _description = "Stream Cash Declaration Popup Wizard Line"

    stream_cash_declarations_popup_wizard_id = fields.Many2one('stream_cash_declarations_popup.wizard', string="Wizard", required=True, ondelete='cascade')
    amount = fields.Monetary(string="Amount")
    currency_id = fields.Many2one(string="Currency", related='stream_cash_declarations_popup_wizard_id.currency_id')
    exchange_rate = fields.Float(string="Exchange Rate", related='stream_cash_declarations_popup_wizard_id.currency_id.rate', readonly=True,digits=(12,6))
    currency_usd = fields.Many2one('res.currency', string="Base Currency", default=lambda self: self.env.company.currency_id)
    company_id = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.company)
    amount_usd = fields.Monetary(string="Amount (USD)", compute="_compute_amount_usd", store=True)

    declaration_type = fields.Integer(string='Declaration Type')

    # cash fields
    count = fields.Integer(string="Count")
    denomination_value = fields.Float(related='denomination_id.value', string="Value", readonly=True)
    denomination_name = fields.Char(related='denomination_id.name', string="Denomination Name", readonly=True)
    denomination_id = fields.Many2one('currency.denomination', string="Denomination", readonly=True)

    # New transaction type field
    transaction_type_id = fields.Many2one('stream_cash_transaction.type', string="Transaction Type")

    
    
    # credit notes fields
    partner_id = fields.Many2one('res.partner', string='Account Name')
    
    
    

    @api.depends('count', 'stream_cash_declarations_popup_wizard_id', 'amount')
    def _compute_amount_usd(self):
        for record in self:
            if record.stream_cash_declarations_popup_wizard_id.currency_id and record.currency_usd:
                record.amount_usd = record.stream_cash_declarations_popup_wizard_id.currency_id._convert(
                    record.amount,
                    record.currency_usd,
                    record.company_id,
                    record.create_date,
                )
            else:
                record.amount_usd = 0.0

            if record.stream_cash_declarations_popup_wizard_id.related_is_negate == True:
                record.amount_usd = record.amount_usd * -1

            print(record.stream_cash_declarations_popup_wizard_id.related_is_negate) 

    @api.onchange('amount')
    def _onchange_amount(self):
        for record in self:
            record._compute_amount_usd()

    @api.onchange('count')
    def _onchange_count(self):
        for line in self:
            if line.stream_cash_declarations_popup_wizard_id.related_is_cash:
                line.amount = line.count * line.denomination_value