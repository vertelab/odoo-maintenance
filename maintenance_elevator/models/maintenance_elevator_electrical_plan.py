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
from odoo.exceptions import AccessError

#: Group allowed to approve a plan. See `JOURNAL_MANAGER_GROUP` in
#: `maintenance_elevator_journal.py` for why this is not an FSM group.
PLAN_MANAGER_GROUP = 'maintenance.group_equipment_manager'


class MaintenanceElevatorElectricalPlan(models.Model):
    """Electrical safety plan for one work moment on one elevator.

    ESA 2006:1 (Elsäkerhet vid arbete i hiss) requires the work to be
    planned before it starts: is there electrical hazard, will the work be
    done dead/live/near live, who is responsible for safety, and which of
    the protective measures are in place. This model is that plan.

    The plan is keyed on the elevator, not on a work order: the same
    hazard exists whether the work is done under an order or not, and the
    equipment module has no fieldservice dependency. Modules that have
    both can add an order link on top.

    `competence_warning` from the source model is deliberately absent. It
    read `hr.skill.compliance_mandatory` / `compliance_category` and
    `hr.employee.skill_ids.cert_status`, which only exist in
    `elevata_compliance` and `elevata_employee_certification` — modules
    that are not ported. Competence requirements are tracked by
    `mgmtsystem_hr_skills` / `elevator_competence` instead.
    """

    _name = 'maintenance.elevator.electrical.plan'
    _description = 'Elevator Electrical Safety Plan'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'plan_date desc, id desc'

    name = fields.Char(default='New', readonly=True, copy=False)
    equipment_id = fields.Many2one(
        'maintenance.equipment',
        string='Elevator',
        required=True,
        ondelete='cascade',
        tracking=True,
        index=True,
    )
    plan_date = fields.Datetime(
        string='Planned On',
        default=fields.Datetime.now,
        required=True,
    )
    electrical_hazard = fields.Boolean(
        string='Electrical Hazard Present',
        default=True,
        tracking=True,
    )
    work_method = fields.Selection(
        selection=[
            ('dead', 'Work with the Installation Dead'),
            ('live', 'Work Live'),
            ('near', 'Work Near Live Parts'),
        ],
        string='Work Method',
        required=True,
        default='dead',
        tracking=True,
    )
    safety_responsible_id = fields.Many2one(
        'hr.employee',
        string='Responsible for the Safety of the Work',
        required=True,
        tracking=True,
    )
    participant_ids = fields.Many2many('hr.employee', string='Participants')
    documentation_checked = fields.Boolean(
        string='Installation Documentation Checked')
    requirements_determined = fields.Boolean(
        string='Requirements Determined')
    disconnected = fields.Boolean(string='Disconnected')
    reconnection_protected = fields.Boolean(
        string='Protected Against Reconnection')
    voltage_tested = fields.Boolean(string='Absence of Voltage Verified')
    adjacent_parts_protected = fields.Boolean(
        string='Protection Against Adjacent Live Parts')
    instructions = fields.Text(string='Safety Instructions')
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('ready', 'Ready for Work'),
            ('approved', 'Approved'),
            ('done', 'Completed'),
        ],
        default='draft',
        required=True,
        tracking=True,
        index=True,
    )
    approved_by_id = fields.Many2one(
        'res.users', string='Approved By', readonly=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = (
                    self.env['ir.sequence']
                    .next_by_code('maintenance.elevator.electrical.plan')
                    or 'New')
        return super().create(vals_list)

    def action_ready(self):
        self.write({'state': 'ready'})

    def action_approve(self):
        if not self.env.user.has_group(PLAN_MANAGER_GROUP):
            raise AccessError(
                _('Only a Maintenance Equipment Manager may approve an '
                  'electrical safety plan.'))
        self.write({
            'state': 'approved',
            'approved_by_id': self.env.user.id,
        })

    def action_done(self):
        self.write({'state': 'done'})
