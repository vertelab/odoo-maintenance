# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2021 Vertel AB (<anders.wallenquist@vertel.se>)
#    All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import models, fields, api, _
from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)

class MaintanenceEquipmentRequestCopy(models.TransientModel):
    _name = 'maintenance.equipment.request.copy'

    request_id  = fields.Many2one(comodel_name='maintenance.request',) 
    

    def copy_requests(self):
        
        for equipment in self.env['maintanence.equipment'].browse(self.env.context.get('active_ids')):
            request = self.request_id.copy()
            request.equipment_id = equipment.id
            
            


class MaintanenceEquipment(models.Model):
    _inherit = 'maintenance.equipment'

    operation_id  = fields.Many2one(comodel_name='maintenance.equipment.operation',string="Operation",help="Main operation") 
    operation_ids = fields.Many2many(comodel_name='maintenance.equipment.operation',string='Operations',help="List of operations",widget='many2many_tags')
    

class MaintanenceEquipmentOperation(models.Model):
    _name = 'maintenance.equipment.operation'
    
    name = fields.Char(string='Operation', size=64, trim=True, )
    
    