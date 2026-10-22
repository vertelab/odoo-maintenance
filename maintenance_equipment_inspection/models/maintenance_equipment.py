# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2026 Vertel Sverige AB (<https://vertel.se>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import api, fields, models


class MaintenanceEquipment(models.Model):
    """Inspection history on the asset.

    The counts and the last inspection are computed rather than stored: an
    inspection is never deleted, so recomputing is cheap and there is no
    second source of truth to drift.
    """

    _inherit = 'maintenance.equipment'

    inspection_ids = fields.One2many(
        'maintenance.equipment.inspection',
        'equipment_id',
        string='Inspections',
    )
    inspection_count = fields.Integer(
        compute='_compute_inspection_stats',
    )
    last_inspection_date = fields.Date(
        compute='_compute_inspection_stats',
        store=True,
    )
    last_inspection_remark_level = fields.Selection(
        selection=[
            ('none', 'No Remark'),
            ('remark', 'Remark'),
            ('red_remark', 'Red Remark'),
        ],
        compute='_compute_inspection_stats',
        store=True,
    )
    inspection_template_id = fields.Many2one(
        'maintenance.inspection.template',
        string='Default Inspection Template',
        help='Used when creating an inspection from this asset.',
    )

    @api.depends('inspection_ids', 'inspection_ids.remark_level',
                 'inspection_ids.date', 'inspection_ids.state')
    def _compute_inspection_stats(self):
        for equipment in self:
            done = equipment.inspection_ids.filtered(
                lambda i: i.state == 'done')
            equipment.inspection_count = len(done)
            if done:
                latest = done.sorted('date', reverse=True)[0]
                equipment.last_inspection_date = latest.date
                equipment.last_inspection_remark_level = latest.remark_level
            else:
                equipment.last_inspection_date = False
                equipment.last_inspection_remark_level = False

    def action_view_inspections(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': self.env._('Inspections — %s', self.name),
            'res_model': 'maintenance.equipment.inspection',
            'view_mode': 'list,form',
            'domain': [('equipment_id', '=', self.id)],
            'context': {
                'default_equipment_id': self.id,
                'default_template_id': self.inspection_template_id.id or False,
            },
        }

    def action_new_inspection(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': self.env._('New Inspection'),
            'res_model': 'maintenance.equipment.inspection',
            'view_mode': 'form',
            'target': 'current',
            'context': {
                'default_equipment_id': self.id,
                'default_template_id': self.inspection_template_id.id or False,
            },
        }
