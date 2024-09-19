from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    @api.constrains('pin')
    def _check_pin_uniqueness(self):
        for employee in self:
            if employee.pin:
                duplicate_employees = self.search([('id', '!=', employee.id), ('pin', '=', employee.pin)])
                if duplicate_employees:
                    duplicate_names = ", ".join(duplicate_employees.mapped('name'))
                    raise ValidationError(_(
                        "The PIN must be unique. The following employee(s) are already using this PIN:\n\n"
                        "%(employee_names)s\n\n"
                        "Please choose a different PIN."
                    ) % {
                        'employee_names': duplicate_names
                    })

    #@api.onchange('pin')
    #def _onchange_pin(self):
    #    if self.pin and not self.pin.isdigit():
    #        return {'warning': {
    #            'title': _("Invalid PIN"),
    #            'message': _("The PIN should only contain digits."),
    #        }}
