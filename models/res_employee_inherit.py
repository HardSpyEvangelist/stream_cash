from odoo import models, fields

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    employee_number = fields.Char(string="Employee Number")
    employee_cashier_number = fields.Char(string="Cashier Number",store=True)
    
    # Permission fields
    # is_cashier = fields.Boolean(string="Cashier", default=True)
    # is_supervisor = fields.Boolean(string="Supervisor", default=False)
    # is_manager = fields.Boolean(string="Manager", default=False)