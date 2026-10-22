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


class MaintenanceInspectionTemplate(models.Model):
    """What to check on an asset of a given category.

    A template is per equipment category rather than per equipment: an
    elevator of one type is checked the same way as another of the same
    type, and copying the list per asset would mean a hundred lists to keep
    in sync.
    """

    _name = 'maintenance.inspection.template'
    _description = 'Inspection Template'
    _order = 'sequence, name'

    name = fields.Char(required=True, translate=True)
    sequence = fields.Integer(default=10)
    category_id = fields.Many2one(
        'maintenance.equipment.category',
        string='Equipment Category',
        help='Leave empty to apply to any equipment.',
    )
    inspection_type = fields.Selection(
        selection=[
            ('statutory', 'Statutory'),
            ('internal', 'Internal'),
            ('safety', 'Safety Round'),
            ('other', 'Other'),
        ],
        string='Inspection Type',
        default='statutory',
        required=True,
    )
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        'res.company',
        default=lambda self: self.env.company,
    )
    line_ids = fields.One2many(
        'maintenance.inspection.template.line',
        'template_id',
        string='Check Points',
    )
    line_count = fields.Integer(compute='_compute_line_count')
    description = fields.Text()

    @api.depends('line_ids')
    def _compute_line_count(self):
        for template in self:
            template.line_count = len(template.line_ids)


class MaintenanceInspectionTemplateLine(models.Model):
    """One check point in a template."""

    _name = 'maintenance.inspection.template.line'
    _description = 'Inspection Template Line'
    _order = 'sequence, id'

    template_id = fields.Many2one(
        'maintenance.inspection.template',
        required=True,
        ondelete='cascade',
    )
    name = fields.Char(string='Check Point', required=True, translate=True)
    sequence = fields.Integer(default=10)
    instruction = fields.Text(
        help='What to look for. Shown to the inspector next to the point.',
    )
    is_mandatory = fields.Boolean(
        default=True,
        help='A mandatory point must be answered before the inspection can '
             'be completed.',
    )
    allow_red_remark = fields.Boolean(
        default=True,
        help='Some points cannot produce a red remark — a cosmetic scratch '
             'does not take an asset out of service.',
    )
