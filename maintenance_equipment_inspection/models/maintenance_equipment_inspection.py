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

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class MaintenanceEquipmentInspection(models.Model):
    """One inspection of one asset.

    The record is the protocol: what was checked, what was found, who
    checked it. It is kept forever, because "when was this last inspected,
    and what did they find?" is a question that gets asked years later.
    """

    _name = 'maintenance.equipment.inspection'
    _description = 'Equipment Inspection'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc, name'

    name = fields.Char(
        required=True,
        copy=False,
        default=lambda self: self.env['ir.sequence'].next_by_code(
            'maintenance.equipment.inspection') or _('New'),
        tracking=True,
    )
    equipment_id = fields.Many2one(
        'maintenance.equipment',
        string='Equipment',
        required=True,
        index=True,
        ondelete='cascade',
        tracking=True,
    )
    template_id = fields.Many2one(
        'maintenance.inspection.template',
        string='Template',
        help='Used to generate the check points. Can be changed before the '
             'inspection starts.',
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
        tracking=True,
    )

    date = fields.Date(
        required=True,
        default=fields.Date.context_today,
        tracking=True,
    )
    inspector_id = fields.Many2one(
        'res.users',
        string='Inspector',
        default=lambda self: self.env.user,
        tracking=True,
    )
    inspection_body_id = fields.Many2one(
        'res.partner',
        string='Inspection Body',
        domain="[('is_company', '=', True)]",
        help='The external body that performed the inspection, if any. '
             'Empty for internal rounds.',
    )
    request_id = fields.Many2one(
        'maintenance.request',
        string='Maintenance Request',
        ondelete='set null',
        help='The request this inspection was performed under, if it came '
             'from a maintenance plan.',
    )

    line_ids = fields.One2many(
        'maintenance.equipment.inspection.line',
        'inspection_id',
        string='Check Points',
    )
    line_count = fields.Integer(compute='_compute_counts', store=True)
    remark_count = fields.Integer(compute='_compute_counts', store=True)
    red_remark_count = fields.Integer(compute='_compute_counts', store=True)

    remark_level = fields.Selection(
        selection=[
            ('none', 'No Remark'),
            ('remark', 'Remark'),
            ('red_remark', 'Red Remark'),
        ],
        compute='_compute_counts',
        store=True,
        tracking=True,
        help='Aggregated from the check points. A red remark is the one that '
             'matters: it means the asset must be taken out of service.',
    )

    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('in_progress', 'In Progress'),
            ('done', 'Completed'),
            ('cancelled', 'Cancelled'),
        ],
        default='draft',
        required=True,
        tracking=True,
    )
    notes = fields.Html()
    report = fields.Binary(string='Inspection Report')
    report_filename = fields.Char()
    company_id = fields.Many2one(
        'res.company',
        default=lambda self: self.env.company,
    )

    @api.depends('line_ids', 'line_ids.result')
    def _compute_counts(self):
        for inspection in self:
            lines = inspection.line_ids
            inspection.line_count = len(lines)
            remarks = lines.filtered(
                lambda l: l.result in ('remark', 'red_remark'))
            inspection.remark_count = len(remarks)
            red = lines.filtered(lambda l: l.result == 'red_remark')
            inspection.red_remark_count = len(red)
            if red:
                inspection.remark_level = 'red_remark'
            elif remarks:
                inspection.remark_level = 'remark'
            else:
                inspection.remark_level = 'none'

    @api.onchange('template_id')
    def _onchange_template_id(self):
        """Prefill the check points from the template.

        Only in the form, as a convenience: the create path generates them
        too, so an inspection created by code or import gets the same list.
        """
        if not self.template_id or self.line_ids:
            return
        self.line_ids = [(0, 0, vals) for vals in self._prepare_line_vals()]

    @api.model_create_multi
    def create(self, vals_list):
        inspections = super().create(vals_list)
        for inspection in inspections:
            if not inspection.line_ids and inspection.template_id:
                vals = inspection._prepare_line_vals()
                if vals:
                    inspection.line_ids = [(0, 0, v) for v in vals]
        return inspections

    def _prepare_line_vals(self):
        """Build the check points from the template."""
        self.ensure_one()
        return [{
            'template_line_id': line.id,
            'name': line.name,
            'sequence': line.sequence,
            'instruction': line.instruction,
            'is_mandatory': line.is_mandatory,
            'allow_red_remark': line.allow_red_remark,
        } for line in self.template_id.line_ids]

    def action_start(self):
        for inspection in self:
            if not inspection.line_ids:
                raise UserError(_(
                    'Add check points before starting the inspection.'))
            inspection.state = 'in_progress'

    def action_complete(self):
        for inspection in self:
            unanswered = inspection.line_ids.filtered(
                lambda l: l.is_mandatory and not l.result)
            if unanswered:
                raise UserError(_(
                    'Every mandatory check point must be answered. '
                    '%(count)s remaining.', count=len(unanswered)))
            inspection.state = 'done'

    def action_cancel(self):
        for inspection in self:
            inspection.state = 'cancelled'

    def action_reset_draft(self):
        for inspection in self:
            inspection.state = 'draft'

    def action_generate_lines(self):
        self.ensure_one()
        if self.line_ids:
            raise UserError(_(
                'This inspection already has check points. Remove them first '
                'if you want to regenerate from the template.'))
        vals = self._prepare_line_vals()
        if not vals:
            raise UserError(_(
                'The template has no check points to generate.'))
        self.line_ids = [(0, 0, v) for v in vals]


class MaintenanceEquipmentInspectionLine(models.Model):
    """One check point's result.

    The name and instruction are copied from the template at creation, not
    read through it: an inspection done in March must still read the same in
    December, even if the template was edited in between. That is the
    difference between a protocol and a live view.
    """

    _name = 'maintenance.equipment.inspection.line'
    _description = 'Equipment Inspection Line'
    _order = 'sequence, id'

    inspection_id = fields.Many2one(
        'maintenance.equipment.inspection',
        required=True,
        ondelete='cascade',
        index=True,
    )
    template_line_id = fields.Many2one(
        'maintenance.inspection.template.line',
        string='Template Point',
        ondelete='set null',
    )
    name = fields.Char(string='Check Point', required=True)
    sequence = fields.Integer(default=10)
    instruction = fields.Text(
        help='Copied from the template: what to look for.',
    )
    is_mandatory = fields.Boolean(
        default=True,
        help='Copied from the template.',
    )
    allow_red_remark = fields.Boolean(
        default=True,
        help='Copied from the template.',
    )

    result = fields.Selection(
        selection=[
            ('ok', 'OK'),
            ('remark', 'Remark'),
            ('red_remark', 'Red Remark'),
            ('not_applicable', 'Not Applicable'),
        ],
        default='ok',
    )
    note = fields.Text()
    photo = fields.Binary()
    photo_filename = fields.Char()
    action_request_id = fields.Many2one(
        'maintenance.request',
        string='Action Request',
        ondelete='set null',
        readonly=True,
        help='Created from this remark, if any.',
    )

    @api.onchange('result', 'allow_red_remark')
    def _onchange_result(self):
        """Refuse a red remark on a point that cannot produce one."""
        if self.result == 'red_remark' and not self.allow_red_remark:
            self.result = 'remark'

    def action_create_maintenance_request(self):
        """Turn a remark into a maintenance request on the same asset.

        The inspection found something; the fix belongs in the maintenance
        system, not in the protocol. One request per point, linked back so
        the protocol shows what came of it.
        """
        self.ensure_one()
        if self.action_request_id:
            return self._action_view_request()

        inspection = self.inspection_id
        request = self.env['maintenance.request'].create({
            'name': self.name,
            'equipment_id': inspection.equipment_id.id,
            'description': self.note or self.name,
            'request_date': fields.Date.context_today(self),
            'maintenance_type': 'corrective',
        })
        self.action_request_id = request
        return self._action_view_request()

    def _action_view_request(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Maintenance Request'),
            'res_model': 'maintenance.request',
            'res_id': self.action_request_id.id,
            'view_mode': 'form',
            'target': 'current',
        }
