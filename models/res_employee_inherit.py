from odoo import models, fields

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    employee_number = fields.Char(string="Employee Number")
    employee_cashier_number = fields.Char(string="Cashier Number",store=True)
    
   