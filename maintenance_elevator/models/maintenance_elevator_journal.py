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
from odoo.exceptions import AccessError, UserError

#: Group allowed to confirm and reopen journal entries. The source module
#: used `fieldservice.group_fsm_manager`; this module has no fieldservice
#: dependency (the elevator is a maintenance asset), so the maintenance
#: equipment manager takes that role.
JOURNAL_MANAGER_GROUP = 'maintenance.group_equipment_manager'


def _require_journal_manager(record):
    if not record.env.user.has_group(JOURNAL_MANAGER_GROUP):
        raise AccessError(
            _('Only a Maintenance Equipment Manager may confirm or reopen '
              'a journal entry.'))


class MaintenanceElevatorJournal(models.Model):
    """The elevator's digital logbook.

    One row per event in the elevator's life: commissioned, inspected,
    serviced, taken out of service, modified. The logbook is the evidence
    an authority (BFS 2011:12) expects to be able to read.

    Rows created by the system (`create_automatic`) are confirmed on
    creation: they are a record of something that already happened. Rows
    typed by a person start as drafts and are confirmed by a manager, after
    which they are immutable — corrections are new rows, not edits.

    `source_model` + `source_id` is the idempotency key. Whatever creates a
    row automatically writes the model and id of the thing that caused it,
    so a re-run of the backfill never duplicates an event.
    """

    _name = 'maintenance.elevator.journal'
    _description = 'Elevator Journal'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'event_date desc, id desc'

    name = fields.Char(default='New', readonly=True, copy=False)
    equipment_id = fields.Many2one(
        'maintenance.equipment',
        string='Elevator',
        required=True,
        ondelete='restrict',
        tracking=True,
        index=True,
    )
    event_date = fields.Datetime(
        string='Date and Time',
        required=True,
        default=fields.Datetime.now,
        tracking=True,
        index=True,
    )
    event_type = fields.Selection(
        selection=[
            ('initial', 'Journal Created'),
            ('inspection', 'Periodic Supervision'),
            ('service', 'Service and Maintenance'),
            ('repair', 'Repair / Fault'),
            ('change', 'Elevator Modification'),
            ('outage', 'Out of Service'),
            ('operation', 'Back in Service'),
            ('statutory_inspection', 'Statutory Inspection'),
            ('incident', 'Accident / Near Miss'),
            ('risk', 'Risk Assessment'),
            ('other', 'Other'),
        ],
        string='Event Type',
        required=True,
        default='other',
        tracking=True,
        index=True,
    )
    scope = fields.Text(
        string='Action and Scope',
        required=True,
        tracking=True,
    )
    performed_by_id = fields.Many2one(
        'hr.employee',
        string='Performed By',
        tracking=True,
    )
    performed_by_name = fields.Char(string='Performed By (External)')
    incident_id = fields.Many2one(
        'mgmtsystem.nonconformity',
        string='Incident / Deviation',
        ondelete='set null',
    )
    downtime_start = fields.Datetime(string='Out of Service From')
    downtime_end = fields.Datetime(string='Out of Service Until')
    downtime_reason = fields.Text(string='Out of Service Reason')
    operating_intensity = fields.Char(string='Operating Intensity')
    revision_inspection_required = fields.Boolean(
        string='Revision Inspection Required')
    revision_inspection_done = fields.Boolean(
        string='Revision Inspection Done')
    minor_deviation = fields.Text(string='Minor Deviation')
    attachment_ids = fields.Many2many('ir.attachment', string='Attachments')

    # Idempotency key: which record, in which model, caused this row.
    source_model = fields.Char(readonly=True, index=True)
    source_id = fields.Integer(readonly=True, index=True)

    state = fields.Selection(
        selection=[('draft', 'Draft'), ('confirmed', 'Confirmed')],
        default='draft',
        required=True,
        tracking=True,
        index=True,
    )
    confirmed_by_id = fields.Many2one(
        'res.users', string='Confirmed By', readonly=True)
    confirmed_date = fields.Datetime(string='Confirmed On', readonly=True)
    can_manage = fields.Boolean(compute='_compute_can_manage')

    @api.depends_context('uid')
    def _compute_can_manage(self):
        allowed = self.env.user.has_group(JOURNAL_MANAGER_GROUP)
        for record in self:
            record.can_manage = allowed

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = (
                    self.env['ir.sequence']
                    .next_by_code('maintenance.elevator.journal') or 'New')
        return super().create(vals_list)

    def write(self, vals):
        if (
            any(record.state == 'confirmed' for record in self)
            and not self.env.user.has_group(JOURNAL_MANAGER_GROUP)
        ):
            raise AccessError(
                _('Confirmed journal entries may only be changed by a '
                  'Maintenance Equipment Manager.'))
        return super().write(vals)

    def unlink(self):
        if any(record.state == 'confirmed' for record in self):
            raise UserError(
                _('Confirmed journal entries may not be deleted. Create a '
                  'corrective entry instead.'))
        return super().unlink()

    def action_confirm(self):
        _require_journal_manager(self)
        self.write({
            'state': 'confirmed',
            'confirmed_by_id': self.env.user.id,
            'confirmed_date': fields.Datetime.now(),
        })

    def action_reopen(self):
        _require_journal_manager(self)
        self.write({'state': 'draft'})

    @api.model
    def create_automatic(self, vals):
        """Create an already-confirmed entry.

        Used by the integrations that record something that has already
        happened: an order was closed, the status changed, a backfill ran.
        `sudo()` keeps those writes working for users who may not confirm
        entries by hand.
        """
        vals = dict(
            vals,
            state='confirmed',
            confirmed_by_id=self.env.user.id,
            confirmed_date=fields.Datetime.now(),
        )
        return self.sudo().create(vals)

    @api.model
    def event_type_for_order_type(self, order_type_name):
        """Derive the journal event type from a work order's type name.

        The order type is free text as far as this module is concerned, so
        the mapping is deliberately name-based: 'service' → service,
        'besikt'/'inspection' → statutory inspection, everything else →
        repair. The order side passes the name of whichever type field it
        has; this module does not depend on fieldservice and cannot read
        `fsm.order.type` itself.
        """
        type_name = (order_type_name or '').lower()
        if 'service' in type_name:
            return 'service'
        if 'besikt' in type_name or 'inspection' in type_name:
            return 'statutory_inspection'
        return 'repair'

    @api.model
    def backfill_journals(self):
        """Seed the journal from data the elevator already carries.

        Creates the three events that are knowable without any history:
        the elevator existed, its current operational status, and its last
        statutory inspection. Idempotent through `source_model`/`source_id`.
        """
        elevators = self.env['maintenance.equipment'].search([
            ('is_elevator', '=', True),
        ])
        created = 0
        for elevator in elevators:
            created += self._backfill_source(
                elevator,
                source_model='maintenance.equipment.initial',
                vals={
                    'event_date': elevator.create_date or fields.Datetime.now(),
                    'event_type': 'initial',
                    'scope': 'Digital elevator journal created for an '
                             'existing elevator.',
                },
            )
            if elevator.operational_status != 'operational':
                created += self._backfill_source(
                    elevator,
                    source_model='maintenance.equipment.status',
                    vals={
                        'event_date': elevator.write_date or fields.Datetime.now(),
                        'event_type': 'outage',
                        'scope': 'Existing operational status: %s' % (
                            dict(elevator._fields['operational_status'].selection)
                            .get(elevator.operational_status)),
                        'downtime_reason': elevator.out_of_order_reason,
                    },
                )
            if elevator.last_inspection:
                created += self._backfill_source(
                    elevator,
                    source_model='maintenance.equipment.inspection',
                    vals={
                        'event_date': fields.Datetime.to_datetime(
                            elevator.last_inspection),
                        'event_type': 'statutory_inspection',
                        'scope': 'Existing inspection recorded. Inspecting '
                                 'body: %s. Number: %s.' % (
                                     elevator.inspection_company_id.name or '-',
                                     elevator.inspection_number or '-'),
                    },
                )
        return len(elevators), created

    @api.model
    def _backfill_source(self, elevator, source_model, vals):
        """Create one backfill entry unless it already exists."""
        if self.search_count([
            ('source_model', '=', source_model),
            ('source_id', '=', elevator.id),
        ]):
            return 0
        self.create_automatic(dict(
            vals,
            equipment_id=elevator.id,
            source_model=source_model,
            source_id=elevator.id,
        ))
        return 1
