from odoo import models, fields, api
from odoo.exceptions import UserError

class StreamCashAppModel(models.Model):
    _name = "stream_cash.declarations"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Stream Cash Declarations"
    _rec_name = 'cashier_name'

    cashier_name = fields.Many2one('hr.employee',string='Cashier',domain="[('job_id.name', '=', 'Cashier')]", required=True)
    cashier_number = fields.Char(string="Cashier Number", related='cashier_name.employee_cashier_number', store=True)
    supervisor_name = fields.Many2one('hr.employee',string="Supervisor",domain="[('job_id.name', '=', 'Supervisor')]")
    manager_name = fields.Many2one('hr.employee',string="Manager",domain="[('job_id.name', '=', 'Manager')]")

    date = fields.Datetime(string='Date', default=fields.Datetime.now)
    verified_date = fields.Datetime(string='Verified Date')
    cancelled_date = fields.Datetime(string='Cancelled Date')
    deleted_date = fields.Datetime(string='Deleted Date')
    
    total_declared = fields.Float(string="Total Declared")
    wrong_tenders_or_comments = fields.Text(string="Wrong Tenders / Comments")
    cashup_z_reading = fields.Float(string="Cashup Z Reading (USD)", required=True)
    variance = fields.Float(string="Variance (USD)", compute='_compute_variance', store=True)

    # Computed fields - all with consistent compute_sudo and store settings
    cash_floats = fields.Integer(string='Floats (USD)', compute='_compute_all_totals', store=True, compute_sudo=True)
    cash_excl_floats = fields.Float(compute='_compute_all_totals', string='Cash Excl Floats (USD)', store=True, compute_sudo=True)
    accounts = fields.Float(compute='_compute_all_totals', string='Accounts (USD)', store=True, compute_sudo=True)
    credit_notes = fields.Float(compute='_compute_all_totals', string='Credit Notes (USD)', store=True, compute_sudo=True)
    usd_eft = fields.Float(string="Eft - USD", compute="_compute_all_totals", store=True, compute_sudo=True)
    usd_offline = fields.Float(string="Offline - USD", compute="_compute_all_totals", store=True, compute_sudo=True)
    zig_eft = fields.Float(string="Eft - ZiG", compute="_compute_all_totals", store=True, compute_sudo=True)
    zig_offline = fields.Float(string="Offline ZiG", compute="_compute_all_totals", store=True, compute_sudo=True)
    zar_eft = fields.Float(string="Eft - ZAR", compute="_compute_all_totals", store=True, compute_sudo=True)
    zar_offline = fields.Float(string="Offline - ZAR", compute="_compute_all_totals", store=True, compute_sudo=True)
    total_cards_total = fields.Float(compute='_compute_all_totals', string="Total Cards Total", store=True, compute_sudo=True)
    vouchers_issued = fields.Float(string="Vouchers Issued (USD)", compute="_compute_all_totals", store=True, compute_sudo=True)
    vouchers_redeemed = fields.Float(string="Vouchers Redeemed (USD)", compute="_compute_all_totals", store=True, compute_sudo=True)
    pickups_cash = fields.Float(compute='_compute_all_totals', string="Pickup Cash (USD)", store=True, compute_sudo=True)
    payment_out = fields.Integer(compute='_compute_all_totals', store=True, compute_sudo=True)
    total = fields.Float(string="Total (USD)", compute="_compute_all_totals", store=True, compute_sudo=True)
    other_declarations_total = fields.Float(string="Other Declarations Total", compute="_compute_all_totals", store=True, compute_sudo=True)

    currency_usd = fields.Many2one(
        'res.currency',
        string="Base Currency", 
        help="This field ensures compatibility with monetary fields",
        default=lambda self: self.env.company.currency_id
    )

    # State field with new statuses
    state = fields.Selection(
        string='Status',
        selection=[
            ('Draft', 'Draft'), 
            ('Verified', 'Verified'), 
            ('Closed', 'Closed'),
            ('Cancelled', 'Cancelled'),
            ('Deleted', 'Deleted')
        ],
        default='Draft')

    declaration_lines = fields.One2many('stream_cash.declaration.line', 'declaration_id', string="Declaration Lines")

    currency = fields.Many2one('res.currency', string="Currency")
    exchange_rate = fields.Float(string="Exchange Rate")
    amount_usd = fields.Float(string="Amount (USD)")
    amount = fields.Float()

    cash_denomination = fields.Many2one('currency.denomination', string="Denomination")
    count = fields.Integer(string="Count")

    def action_open_type_selector(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'stream_cash_declarations_popup.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_declaration_id': self.id,
            },
        }

    @api.depends('declaration_lines.amount_usd', 'declaration_lines.declaration_type_name')
    def _compute_all_totals(self):
        known_types = {'Pickup', 'Accounts', 'Credit Note', 'Cash', 'Floats', 'Credit Card', 'Voucher', 'Payment Out'}

        for record in self:
            total = pickups_cash = accounts = credit_notes = 0.0
            cash_excl_floats = total_cards_total = vouchers_issued = vouchers_redeemed = 0.0
            cash_floats = payment_out = 0.0

            usd_eft = usd_offline = zig_eft = zig_offline = 0.0
            zar_eft = zar_offline = 0.0
            other_total = 0.0

            total_cash_lines = total_float_lines = 0.0

            for line in record.declaration_lines:
                amount = line.amount_usd or 0.0
                dtype = line.declaration_type_name or ''

                if dtype in known_types:
                    if dtype == 'Pickup':
                        pickups_cash += amount
                    elif dtype == 'Accounts':
                        accounts += amount
                    elif dtype == 'Credit Note':
                        credit_notes += amount
                    elif dtype == 'Cash':
                        total_cash_lines += amount
                    elif dtype == 'Floats':
                        total_float_lines += amount
                    elif dtype == 'Payment Out':
                        payment_out += amount
                    elif dtype == 'Credit Card':
                        total_cards_total += amount
                    elif dtype == 'Voucher':
                        # Voucher line already contains net amount, so add directly to total
                        total += amount
                else:
                    other_total += amount

                # Add to total for all types except Voucher (vouchers are handled above)
                if dtype != 'Voucher':
                    total += amount

                for note_line in line.declaration_notes_line_ids:
                    note_amount = note_line.amount_usd or 0.0
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

            cash_floats = total_float_lines
            cash_excl_floats = total_cash_lines + total_float_lines

            record.total = total
            record.pickups_cash = pickups_cash
            record.accounts = accounts
            record.credit_notes = credit_notes
            record.cash_floats = cash_floats
            record.payment_out = payment_out
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
            record.other_declarations_total = other_total

    @api.depends('total', 'cashup_z_reading')
    def _compute_variance(self):
        for record in self:
            record.variance = record.total - record.cashup_z_reading

    def action_verify(self):
        self.ensure_one()
        if self.state != 'Draft':
            raise UserError("Can only verify declarations in Draft state")
        self.state = 'Verified'
        self.verified_date = fields.Datetime.now()

    def action_close(self):
        self.ensure_one()
        if self.state != 'Verified':
            raise UserError("Can only close declarations in Verified state")
        self.state = 'Closed'

    def action_cancel(self):
        self.ensure_one()
        if self.state in ['Cancelled', 'Deleted']:
            raise UserError("Cannot cancel a declaration that is already cancelled or deleted")
        self.state = 'Cancelled'
        self.cancelled_date = fields.Datetime.now()

    def action_delete(self):
        self.ensure_one()
        if self.state == 'Deleted':
            raise UserError("Declaration is already marked as deleted")
        self.state = 'Deleted'
        self.deleted_date = fields.Datetime.now()

    def action_reset_to_draft(self):
        self.ensure_one()
        self.state = 'Draft'
        self.verified_date = False
        self.cancelled_date = False
        self.deleted_date = False

    def action_bulk_close(self):
        for record in self:
            if record.state.lower() == 'verified':
                record.write({'state': 'Closed'})
            else:
                raise UserError(f"Declaration {record._name or record.id} is not in 'Verified' state.")

    def action_bulk_cancel(self):
        for record in self:
            if record.state not in ['Cancelled', 'Deleted']:
                record.write({
                    'state': 'Cancelled',
                    'cancelled_date': fields.Datetime.now()
                })

    def action_bulk_delete(self):
        for record in self:
            record.write({
                'state': 'Deleted',
                'deleted_date': fields.Datetime.now()
            })

    def unlink(self):
        raise UserError("Physical deletion is not allowed. Use 'Cancel' or 'Delete' status instead.")