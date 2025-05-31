from odoo import models, fields, api
from odoo.exceptions import ValidationError


class CashDeclarationWizard(models.TransientModel):
    _name = "stream_cash_declarations_popup.wizard"
    _description = "Stream Cash Declaration Popup Wizard"

    declaration_type_name = fields.Char(string="Declaration Type",related="declaration_type_ids.name",store=True)
    declaration_type_ids = fields.Many2one('declaration.type', string='Declaration Type', required=True)
    declaration_id = fields.Many2one('stream_cash.declarations', string="Declaration", required=True)
    currency_id = fields.Many2one('res.currency', string="Currency", required=True)
    line_ids = fields.One2many('stream_cash_declarations_popup_wizard.line', 'wizard_id', string="Lines")

    related_is_partner = fields.Boolean(related='declaration_type_ids.is_partner', store=True)
    related_is_cash = fields.Boolean(related='declaration_type_ids.is_cash', store=True)
    related_is_negate = fields.Boolean(related='declaration_type_ids.is_negate', store=True)


    
    

    
    total_amount = fields.Float(string="Total Amount", compute="_compute_total_amount", store=True)
    total_amount_usd = fields.Float(string="Total Amount (USD)", store=True)

   
    @api.onchange('currency_id', 'declaration_type_ids')
    def _onchange_currency_id(self):
        if self.currency_id:
            self.line_ids = [(5, 0, 0)]  # Clear existing lines
            if self.related_is_cash:
                denominations = self.env['currency.denomination'].search([
                    ('currency_id', '=', self.currency_id.id),
                    ('active', '=', True)
                ], order='value desc')
                line_vals = []
                for denomination in denominations:
                    line_vals.append((0, 0, {
                        'denomination_id': denomination.id,
                        'count': 0,
                        'exchange_rate': self.currency_id.rate or 1.0
                    }))
                self.line_ids = line_vals

    def action_save(self):
        declaration_notes = []
        cash_amount = 0

        # Special handling for vouchers - calculate net amount
        if self.declaration_type_name == 'Voucher':
            vouchers_issued = 0
            vouchers_redeemed = 0
            
            for rec in self.line_ids:
                # Store voucher note lines with correct cash impact amounts
                if rec.transaction_type_id and rec.transaction_type_id.name == 'Issued':
                    vouchers_issued += rec.amount
                    # Issued vouchers reduce cash, so store as negative
                    amount = -rec.amount
                elif rec.transaction_type_id and rec.transaction_type_id.name == 'Redeemed':
                    vouchers_redeemed += rec.amount
                    # Redeemed vouchers increase cash, so store as positive
                    amount = rec.amount
                else:
                    amount = rec.amount
                
                # Apply negate logic if needed
                if self.related_is_negate:
                    amount = -amount
                
                # Create the note line with the correct cash impact amount
                line_note = {
                    'amount': amount,
                    'currency_id': rec.currency_id.id,
                    'count': rec.count,
                    'denomination_id': rec.denomination_id.id if rec.denomination_id else False,
                    'transaction_type_id': rec.transaction_type_id.id if rec.transaction_type_id else False,
                    'partner_id': rec.partner_id.id if rec.partner_id else False,
                }
                declaration_notes.append((0, 0, line_note))
            
            # For vouchers, the net amount is redeemed minus issued
            cash_amount = vouchers_redeemed - vouchers_issued
            if self.related_is_negate:
                cash_amount = -cash_amount
        else:
            # Regular handling for non-voucher declaration types
            for rec in self.line_ids:
                line_note = {}  # Always define fresh

                amount = -rec.amount if self.related_is_negate else rec.amount  #  Apply negate logic

                if rec.wizard_id.related_is_cash:
                    if rec.count > 0:
                        line_note = {
                            'amount': amount,  #  Store the possibly negative amount
                            'currency_id': rec.currency_id.id,
                            'count': rec.count,
                            'denomination_id': rec.denomination_id.id,
                            'transaction_type_id': rec.transaction_type_id.id if rec.transaction_type_id else False,
                            'partner_id': rec.partner_id.id if rec.partner_id else False,
                        }
                        declaration_notes.append((0, 0, line_note))
                        cash_amount += amount  #  Add possibly negative amount
                else:
                    line_note = {
                        'amount': amount,  #  Same for non-cash
                        'currency_id': rec.currency_id.id,
                        'count': rec.count,
                        'denomination_id': rec.denomination_id.id if rec.denomination_id else False,
                        'transaction_type_id': rec.transaction_type_id.id if rec.transaction_type_id else False,
                        'partner_id': rec.partner_id.id if rec.partner_id else False,
                    }
                    declaration_notes.append((0, 0, line_note))
                    cash_amount += amount  #  Again, add possibly negative

        print(declaration_notes)

        self.env['stream_cash.declaration.line'].create({
            'declaration_id': self.declaration_id.id,
            'declaration_type_ids': self.declaration_type_ids.id,
            'currency_id': self.currency_id.id,
            'amount': cash_amount,
            'declaration_notes_line_ids': declaration_notes,
        })

        return {'type': 'ir.actions.act_window_close'}