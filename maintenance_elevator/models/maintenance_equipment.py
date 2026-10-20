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

from datetime import timedelta

from odoo import models, fields, api, _
from odoo.tools.translate import html_translate


class MaintenanceEquipment(models.Model):
    _inherit = 'maintenance.equipment'

    # ------------------------------------------------------------------
    # Identity
    # ------------------------------------------------------------------
    is_elevator = fields.Boolean(
        string='Is Elevator',
        default=False,
        help='Mark this asset as an elevator. Reveals the elevator tabs.',
    )
    elevator_number = fields.Char(
        string='Elevator Number',
        tracking=True,
        help='Customer-facing identifier, e.g. "Lift 1" or a property '
             'numbering scheme.',
    )
    manufacturing_number = fields.Char(string='Manufacturing Number', tracking=True)
    installation_year = fields.Integer(string='Installation Year', tracking=True)
    number_of_stops = fields.Integer(string='Number of Stops', tracking=True)
    operating_intensity = fields.Char(
        string='Operating Intensity',
        help='Traffic class, e.g. use category per SS-EN 81-20.',
    )

    # ------------------------------------------------------------------
    # Technical configuration (references)
    # ------------------------------------------------------------------
    elevator_type_id = fields.Many2one(
        'maintenance.elevator.type',
        string='Elevator Type',
        domain=[('model_type', '=', 'elevator')],
        tracking=True,
    )
    mechanical_brand_id = fields.Many2one(
        'maintenance.elevator.type',
        string='Mechanical Brand',
        domain=[('model_type', '=', 'brand')],
        tracking=True,
    )
    control_system_id = fields.Many2one(
        'maintenance.elevator.type',
        string='Control System',
        domain=[('model_type', '=', 'control_system')],
        tracking=True,
    )
    car_door_type_id = fields.Many2one(
        'maintenance.elevator.type',
        string='Car Door Type',
        domain=[('model_type', '=', 'car_door')],
    )
    shaft_door_type_id = fields.Many2one(
        'maintenance.elevator.type',
        string='Shaft Door Type',
        domain=[('model_type', '=', 'shaft_door')],
    )
    bearing_config_id = fields.Many2one(
        'maintenance.elevator.type',
        string='Bearing / Top / Pit',
        domain=[('model_type', '=', 'bearing')],
    )
    lubrication_type_id = fields.Many2one(
        'maintenance.elevator.type',
        string='Lubrication Type',
        domain=[('model_type', '=', 'lubrication')],
    )
    gsm_device_id = fields.Many2one(
        'maintenance.elevator.type',
        string='GSM Device',
        domain=[('model_type', '=', 'gsm')],
    )
    emergency_phone_type_id = fields.Many2one(
        'maintenance.elevator.type',
        string='Emergency Phone Type',
        domain=[('model_type', '=', 'emergency_phone')],
    )
    p100 = fields.Char(
        string='P100',
        help='Phone number of the elevator GSM unit.',
    )
    sim_image = fields.Binary(
        string='SIM Image',
        help='Photo of the SIM card, so a technician can identify it on site.',
    )
    has_machine_room = fields.Boolean(string='Machine Room', default=False)

    # ------------------------------------------------------------------
    # Technical documentation — one field per physical section
    # ------------------------------------------------------------------
    tech_general = fields.Html(string='General', translate=html_translate)
    tech_car = fields.Html(string='Car', translate=html_translate)
    tech_control_panel = fields.Html(string='Control Panel', translate=html_translate)
    tech_doors = fields.Html(string='Doors', translate=html_translate)
    tech_machine_room = fields.Html(
        string='Machine Room (documentation)', translate=html_translate)
    tech_options = fields.Html(string='Options', translate=html_translate)
    tech_shaft = fields.Html(string='Shaft', translate=html_translate)
    tech_signalization = fields.Html(string='Signalization', translate=html_translate)

    # ------------------------------------------------------------------
    # Statutory inspection
    # ------------------------------------------------------------------
    inspection_company_id = fields.Many2one(
        'res.partner',
        string='Inspection Company',
        tracking=True,
    )
    inspection_number = fields.Char(string='Inspection Number', tracking=True)
    inspection_month = fields.Selection(
        selection=[
            ('1', 'January'), ('2', 'February'), ('3', 'March'),
            ('4', 'April'), ('5', 'May'), ('6', 'June'),
            ('7', 'July'), ('8', 'August'), ('9', 'September'),
            ('10', 'October'), ('11', 'November'), ('12', 'December'),
        ],
        string='Inspection Month',
        tracking=True,
    )
    last_inspection = fields.Date(string='Last Inspection', tracking=True)
    next_inspection_date = fields.Date(
        string='Next Inspection',
        tracking=True,
        help='Drives the "inspection soon" flag.',
    )
    inspection_soon = fields.Boolean(
        string='Inspection Soon',
        compute='_compute_inspection_soon',
        search='_search_inspection_soon',
        # Not stored: the flag depends on today's date and on a system
        # parameter, neither of which is a dependency Odoo can track. A stored
        # value would silently go stale after the parameter is changed.
        # A search method is therefore required: without it Odoo rejects the
        # search filter with "Unsearchable field".
        help='True when the next inspection falls within the warning window.',
    )
    revision_inspection_required = fields.Boolean(
        string='Revision Inspection Required',
    )
    revision_inspection_done = fields.Boolean(
        string='Revision Inspection Done',
    )

    # ------------------------------------------------------------------
    # Operational status
    # ------------------------------------------------------------------
    operational_status = fields.Selection(
        selection=[
            ('operational', 'In Service'),
            ('out_of_order', 'Out of Order'),
            ('shutdown', 'Shut Down'),
            ('decommissioned', 'Decommissioned'),
        ],
        string='Operational Status',
        default='operational',
        required=True,
        tracking=True,
    )
    out_of_order_date = fields.Date(string='Out of Order Since', tracking=True)
    out_of_order_reason = fields.Text(string='Out of Order Reason', tracking=True)
    out_of_order_by = fields.Many2one(
        'res.users',
        string='Out of Order Reported By',
        tracking=True,
    )

    # ------------------------------------------------------------------
    # Risk register
    # ------------------------------------------------------------------
    risk_ids = fields.One2many(
        'maintenance.elevator.risk',
        'equipment_id',
        string='Risks',
    )
    risk_count = fields.Integer(
        string='Risk Count',
        compute='_compute_risk_count',
    )

    # ------------------------------------------------------------------
    # Computed
    # ------------------------------------------------------------------
    @api.depends('next_inspection_date')
    def _compute_inspection_soon(self):
        """Flag inspections due within the configured window (default 60 days).

        The window is a system parameter so operations can tune it without a
        code change.
        """
        days = int(
            self.env['ir.config_parameter']
            .sudo()
            .get_param('maintenance_elevator.inspection_warning_days', 60)
        )
        today = fields.Date.context_today(self)
        horizon = today + timedelta(days=days)
        for equipment in self:
            if equipment.next_inspection_date:
                equipment.inspection_soon = (
                    today <= equipment.next_inspection_date <= horizon
                )
            else:
                equipment.inspection_soon = False

    def _search_inspection_soon(self, operator, value):
        """Search support for the non-stored `inspection_soon` flag.

        The flag cannot be stored (it depends on today's date and on a system
        parameter), so the filter is translated into the equivalent domain on
        `next_inspection_date`.
        """
        days = int(
            self.env['ir.config_parameter']
            .sudo()
            .get_param('maintenance_elevator.inspection_warning_days', 60)
        )
        today = fields.Date.context_today(self)
        horizon = today + timedelta(days=days)
        in_window = [
            '&',
            ('next_inspection_date', '>=', today),
            ('next_inspection_date', '<=', horizon),
        ]
        if (operator == '=' and value) or (operator == '!=' and not value):
            return in_window
        return ['!'] + in_window

    @api.depends('risk_ids')
    def _compute_risk_count(self):
        for equipment in self:
            equipment.risk_count = len(equipment.risk_ids)

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------
    def action_view_risks(self):
        self.ensure_one()
        return {
            'name': _('Risks — %s', self.name),
            'type': 'ir.actions.act_window',
            'res_model': 'maintenance.elevator.risk',
            'view_mode': 'list,form',
            'domain': [('equipment_id', '=', self.id)],
            'context': {'default_equipment_id': self.id},
        }

    def action_mark_out_of_order(self):
        """Flag the elevator as out of order, stamped with the current user."""
        for equipment in self:
            equipment.write({
                'operational_status': 'out_of_order',
                'out_of_order_date': fields.Date.context_today(equipment),
                'out_of_order_by': self.env.uid,
            })

    def action_restore_to_service(self):
        for equipment in self:
            equipment.write({
                'operational_status': 'operational',
                'out_of_order_date': False,
                'out_of_order_reason': False,
                'out_of_order_by': False,
            })


class MaintenanceElevatorRisk(models.Model):
    """A risk recorded against an elevator asset.

    Ported from Elevata's `elevata.compliance.risk`, narrowed to what belongs
    on the asset. The compliance journal and incident handling stay in a
    separate module — this is the asset's risk profile, not the full
    compliance workflow.
    """

    _name = 'maintenance.elevator.risk'
    _description = 'Elevator Risk'
    _order = 'risk_score desc, id desc'
    _inherit = ['mail.thread']

    name = fields.Char(string='Title', required=True, tracking=True)
    equipment_id = fields.Many2one(
        'maintenance.equipment',
        string='Elevator',
        required=True,
        ondelete='cascade',
        index=True,
    )
    hazard = fields.Text(string='Identified Hazard', required=True)
    consequence = fields.Selection(
        selection=[(str(i), str(i)) for i in range(1, 6)],
        string='Consequence',
        required=True,
        default='1',
        tracking=True,
    )
    probability = fields.Selection(
        selection=[(str(i), str(i)) for i in range(1, 6)],
        string='Probability',
        required=True,
        default='1',
        tracking=True,
    )
    existing_controls = fields.Text(string='Existing Controls')
    required_controls = fields.Text(string='Additional Measures')
    minor_deviation = fields.Text(string='Minor Deviation')

    risk_score = fields.Integer(
        string='Risk Score',
        compute='_compute_risk_score',
        store=True,
        index=True,
    )
    serious = fields.Boolean(
        string='Serious Risk',
        compute='_compute_risk_score',
        store=True,
    )
    severity = fields.Selection(
        selection=[
            ('low', 'Low'),
            ('medium', 'Medium'),
            ('high', 'High'),
            ('critical', 'Critical'),
        ],
        compute='_compute_risk_score',
        store=True,
        string='Severity',
        index=True,
    )

    assessment_date = fields.Date(
        string='Assessment Date',
        required=True,
        default=fields.Date.context_today,
        tracking=True,
    )
    responsible_id = fields.Many2one(
        'res.users',
        string='Responsible',
        default=lambda self: self.env.user,
        tracking=True,
    )
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('confirmed', 'Confirmed'),
        ],
        string='Status',
        default='draft',
        required=True,
        tracking=True,
    )
    confirmed_by_id = fields.Many2one('res.users', string='Confirmed By', readonly=True)
    confirmed_date = fields.Datetime(string='Confirmed On', readonly=True)
    attachment_ids = fields.Many2many('ir.attachment', string='Attachments')

    @api.depends('consequence', 'probability')
    def _compute_risk_score(self):
        """Risk score is consequence × probability on a 1–5 scale.

        Thresholds: >= 15 critical, >= 9 high, >= 4 medium, else low.
        A score of 15 or more (e.g. 3×5, 5×3) is flagged serious.
        """
        for risk in self:
            consequence = int(risk.consequence or 0)
            probability = int(risk.probability or 0)
            score = consequence * probability
            risk.risk_score = score
            risk.serious = score >= 15
            if score >= 15:
                risk.severity = 'critical'
            elif score >= 9:
                risk.severity = 'high'
            elif score >= 4:
                risk.severity = 'medium'
            else:
                risk.severity = 'low'

    def action_confirm(self):
        for risk in self:
            risk.write({
                'state': 'confirmed',
                'confirmed_by_id': self.env.uid,
                'confirmed_date': fields.Datetime.now(),
            })

    def action_reset_to_draft(self):
        for risk in self:
            risk.write({
                'state': 'draft',
                'confirmed_by_id': False,
                'confirmed_date': False,
            })
