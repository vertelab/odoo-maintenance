import logging
from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)

class MaintenanceEquipmentController(http.Controller):

    @http.route(['/maintenance/equipment/<int:equipment_id>'], type='http', auth="public", website=True)
    def equipment_page(self, equipment_id, **kw):
        _logger.info(f"Accessing equipment page for ID: {equipment_id}")
        try:
            equipment = request.env['maintenance.equipment'].sudo().browse(equipment_id)
            if not equipment.exists():
                _logger.warning(f"Equipment with ID {equipment_id} not found")
                return request.render("maintenance_equipment_page_assignment.equipment_not_found")
            
            _logger.debug(f"Equipment found: {equipment.name}")
            
            employee = equipment.employee_id
            department = equipment.department_id
            
            _logger.debug(f"Assigned Employee: {employee.name if employee else 'None'}")
            _logger.debug(f"Assigned Department: {department.name if department else 'None'}")
            
            return request.render("maintenance_equipment_page_assignment.equipment_details", {
                'equipment': equipment,
                'employee': employee,
                'department': department,
            })
        except Exception as e:
            _logger.error(f"Error occurred while rendering equipment page: {str(e)}")
            return request.render("maintenance_equipment_page_assignment.equipment_not_found")

    @http.route(['/maintenance/equipment/assign'], type='http', auth="public", website=True, methods=['POST'])
    def assign_equipment(self, **post):
        equipment_id = int(post.get('equipment_id'))
        pin = post.get('pin')
        
        equipment = request.env['maintenance.equipment'].sudo().browse(equipment_id)
        employee = request.env['hr.employee'].sudo().search([('pin', '=', pin)], limit=1)
        
        if employee:
            equipment.write({'employee_id': employee.id})
            return request.redirect(f'/maintenance/equipment/{equipment_id}')
        else:
            return request.render("maintenance_equipment_page_assignment.equipment_details", {
                'equipment': equipment,
                'employee': False,
                'department': False,
                'error_message': 'Invalid PIN. Please try again.'
            })
    
    @http.route(['/maintenance/equipment/unassign'], type='http', auth="public", website=True, methods=['POST'])
    def unassign_equipment(self, **post):
        equipment_id = int(post.get('equipment_id'))
        pin = post.get('pin')
        
        equipment = request.env['maintenance.equipment'].sudo().browse(equipment_id)
        employee = request.env['hr.employee'].sudo().search([('pin', '=', pin)], limit=1)
        
        if employee and employee == equipment.employee_id:
            equipment.write({'employee_id': False, 'department_id': False})
            return request.redirect(f'/maintenance/equipment/{equipment_id}')
        else:
            return request.render("maintenance_equipment_page_assignment.equipment_details", {
                'equipment': equipment,
                'employee': equipment.employee_id,
                'department': equipment.department_id,
                'error_message': 'Invalid PIN or you are not assigned to this equipment. Please try again.'
            })
