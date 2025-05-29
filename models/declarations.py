from odoo import models, fields, api
from odoo.exceptions import UserError

class StreamCashAppModel(models.Model):
    _name = "stream_cash.declarations"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Stream Cash App Declarations"
    _rec_name='cashier_name'
    
    # Declaration Type Selection - we're keeping the field but not showing it in the UI
    # It will be updated based on the lines added
    declaration_type_ids = fields.Many2one('declaration.type', string='Declaration Type', required=True)
    
    # Employee and Cashier Info
    

    cashier_name = fields.Many2one('hr.employee', string='Cashier')

    cashier_number = fields.Char(string="Cashier Number",related='cashier_name.employee_cashier_number',store=True)

    # Supervisor and Manager Info
    supervisor_name = fields.Many2one('hr.employee', string="Supervisor")
    manager_name = fields.Many2one('hr.employee', string="Manager")
    
    # Date and other financial data
    date = fields.Datetime(string='Date', default=fields.Datetime.now)
    total_declared = fields.Float(string="Total Declared")
    #x_report = fields.Float(string="X Report")
    
    # Wrong tenders or comments field
    wrong_tenders_or_comments = fields.Text(string="Wrong Tenders / Comments")

    # Amounts for different categories (USD, Credit Notes, etc.)
    cashup_z_reading = fields.Float(string="Cashup Z Reading")    #is also the x_report_reading
    #actual_day_total = fields.Float(string="ACTUAL DAY TOTAL")
    variance = fields.Float(string="Variance",compute='_compute_variance')
    cash_floats = fields.Integer(compute='_compute_all_totals')
    cash_excl_floats = fields.Integer(compute='_compute_all_totals' , string='Cash Excl Floats (USD)')
    accounts = fields.Float(compute='_compute_all_totals',string='Accounts (USD)')
    credit_notes = fields.Float(compute='_compute_all_totals', string='Credit Notes (USD)')
    usd_eft = fields.Float(string="Eft - USD", compute="_compute_all_totals", store=True)
    usd_offline = fields.Float(string="Offline - USD", compute="_compute_all_totals", store=True)
    zig_eft = fields.Float(string="Eft - ZiG", compute="_compute_all_totals", store=True)
    zig_offline = fields.Float(string="Offline ZiG", compute="_compute_all_totals", store=True)
    zar_eft = fields.Float(string="Eft - ZAR", compute="_compute_all_totals", store=True)
    zar_offline = fields.Float(string="Offline - ZAR", compute="_compute_all_totals", store=True)
    total_cards_total = fields.Float(compute='_compute_all_totals',string="Total Cards Total")
    vouchers_issued = fields.Float(string="Vouchers Issued", compute="_compute_all_totals", store=True)
    vouchers_redeemed = fields.Float(string="Vouchers Redeemed", compute="_compute_all_totals", store=True)
    pickups_cash = fields.Float(compute='_compute_all_totals' ,string="Pickup Cash (USD)")
    total = fields.Float(string="Total (USD)", compute="_compute_all_totals", store=True)

    state = fields.Selection(
    string='Status', 
    selection=[('Draft', 'Draft'), ('Verified', 'Verified'), ('Closed', 'Closed')],
    default='Draft')  # Add this line
    
    # Dynamic fields for declaration types (used in lines)
    declaration_lines = fields.One2many('stream_cash.declaration.line','declaration_id', string="Declaration Lines")
    

    # Optional (legacy?) fields
    currency = fields.Many2one('res.currency', string="Currency")
    exchange_rate = fields.Float(string="Exchange Rate")
    amount_usd = fields.Float(string="Amount (USD)")
    amount = fields.Float()

    # Fields for Cash declaration type (e.g., denominations)
    cash_denomination = fields.Many2one('currency.denomination', string="Denomination")
    count = fields.Integer(string="Count")

    def action_open_type_selector(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'add_declarations_popup.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_declaration_id': self.id,
            },
        }  

    @api.depends('declaration_lines.amount_usd','declaration_lines.declaration_type_ids','declaration_lines.declaration_line_ids.amount_usd',
        'declaration_lines.declaration_line_ids.transaction_type_id','declaration_lines.declaration_line_ids.currency_id')
    def _compute_all_totals(self):
        for record in self:
            # Totals by declaration type
            total = pickups_cash = accounts = credit_notes = 0.0
            cash_excl_floats = total_cards_total = vouchers_issued = vouchers_redeemed = 0.0
            cash_floats = 0.0

            # Credit card sub-totals
            usd_eft = usd_offline = zig_eft = zig_offline = 0.0
            zar_eft = zar_offline = 0.0

            for line in record.declaration_lines:
                amount = line.amount_usd
                dtype = line.declaration_type
                total += amount

                if dtype == 'Pickup':
                    pickups_cash += amount
                elif dtype == 'Accounts':
                    accounts += amount
                elif dtype == 'Credit Note':
                    credit_notes += amount
                elif dtype == 'Cash':
                    cash_excl_floats += amount
                elif dtype == 'Floats':
                    cash_floats += amount
                elif dtype == 'Credit Card':
                    total_cards_total += amount

                for note_line in line.declaration_line_ids:
                    note_amount = note_line.amount_usd
                    currency = note_line.currency_id.name.upper() if note_line.currency_id else ''
                    transaction_type_name = note_line.transaction_type_id.name if note_line.transaction_type_id else ''

                    if dtype == 'Voucher':
                        if transaction_type_name == 'Issued':
                            vouchers_issued += note_amount
                        elif transaction_type_name == 'Redeemed':
                            vouchers_redeemed += note_amount

                    elif dtype == 'Credit Card':
                        if transaction_type_name == 'EFT - USD':
                            usd_eft += note_amount
                        elif transaction_type_name == 'OFFLINE - USD':
                            usd_offline += note_amount
                        elif transaction_type_name == 'EFT - ZiG':
                            zig_eft += note_amount
                        elif transaction_type_name == 'OFFLINE - ZiG':
                            zig_offline += note_amount
                        elif transaction_type_name == 'EFT - ZAR':
                            zar_eft += note_amount
                        elif transaction_type_name == 'OFFLINE - ZAR':
                            zar_offline += note_amount

            # Set values
            record.total = total
            record.pickups_cash = pickups_cash
            record.accounts = accounts
            record.credit_notes = credit_notes
            record.cash_floats = cash_floats
            record.cash_excl_floats = cash_excl_floats
            record.total_cards_total = total_cards_total
            record.vouchers_issued = vouchers_issued
            record.vouchers_redeemed = vouchers_redeemed

            record.usd_eft = usd_eft
            record.usd_offline = usd_offline
            record.zig_eft = zig_eft
            record.zig_offline = zig_offline
            record.zar_eft = zar_eft
            record.zar_offline = zar_offline

    
    @api.depends('total', 'cashup_z_reading')
    def _compute_variance(self):
        for record in self:
            record.variance = record.total - record.cashup_z_reading

        
    
    def action_verify(self):
        """Move from Draft to Verified"""
        self.ensure_one()
        if self.state != 'Draft':
            raise UserError("Can only verify declarations in Draft state")
        self.state = 'Verified'

    def action_close(self):
        """Move from Verified to Closed"""
        self.ensure_one()
        if self.state != 'Verified':
            raise UserError("Can only close declarations in Verified state")
        self.state = 'Closed'

    def action_reset_to_draft(self):
        """Reset back to Draft (for corrections)"""
        self.ensure_one()
        self.state = 'Draft'

    def action_reset_to_draft(self):
        """Reset back to Draft (for corrections)"""
        self.ensure_one()
        self.state = 'Draft'

    def action_bulk_close(self):
        for record in self:
            if record.state.lower() == 'verified':
                record.write({'state': 'Closed'})
            else:
                raise UserError(f"Declaration {record._name or record.id} is not in 'Verified' state.")