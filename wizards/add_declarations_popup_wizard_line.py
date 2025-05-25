from odoo import fields, models, api


class CashDeclarationWizardLine(models.TransientModel):
    _name = "add_declarations_popup_wizard.line"
    _description = "Add Declaration Wizard Line"

    wizard_id = fields.Many2one('add_declarations_popup.wizard', string="Wizard", required=True, ondelete='cascade')
    amount = fields.Monetary(string="Amount")
    currency_id = fields.Many2one(string="Currency", related='wizard_id.currency_id')
    exchange_rate = fields.Float(string="Exchange Rate", related='wizard_id.currency_id.rate', readonly=True)
    currency_usd = fields.Many2one('res.currency', string="Currency", default=lambda self: self.env.company.currency_id)
    company_id = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.company)
    amount_usd = fields.Monetary(string="Amount (USD)", compute="_compute_amount_usd", store=True)

    # cash fields
    count = fields.Integer(string="Count")
    denomination_value = fields.Float(related='denomination_id.value', string="Value", readonly=True)
    denomination_name = fields.Char(related='denomination_id.name', string="Denomination", readonly=True)
    denomination_id = fields.Many2one('currency.denomination', string="Denomination", readonly=True)

    # New transaction type field
    transaction_type_id = fields.Many2one('transaction.type', string="Transaction Type")
    
    # credit notes fields
    partner_id = fields.Many2one('res.partner', string='Account Name')

    @api.depends('count', 'wizard_id', 'amount')
    def _compute_amount_usd(self):
        for record in self:
            if record.wizard_id.currency_id and record.currency_usd:
                record.amount_usd = record.wizard_id.currency_id._convert(
                    record.amount,
                    record.currency_usd,
                    record.company_id,
                    record.create_date,
                )
            else:
                record.amount_usd = 0.0

    @api.onchange('amount')
    def _onchange_amount(self):
        for record in self:
            record._compute_amount_usd()

    @api.onchange('count')
    def _onchange_count(self):
        for line in self:
            if line.wizard_id.declaration_type and line.wizard_id.declaration_type == 'Cash':
                line.amount = line.count * line.denomination_value