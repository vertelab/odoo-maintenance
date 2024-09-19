from odoo import models, fields, api

class MaintenanceEquipment(models.Model):
    _inherit = 'maintenance.equipment'

    assignment_link = fields.Char(string="Assignment Link", compute='_compute_assignment_link', store=False)
    
    def _compute_assignment_link(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        for equipment in self:
            equipment.assignment_link = f"{base_url}/maintenance/equipment/{equipment.id}"
