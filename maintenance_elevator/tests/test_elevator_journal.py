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

from odoo import fields
from odoo.exceptions import AccessError, UserError
from odoo.tests import TransactionCase, new_test_user, tagged


@tagged('post_install', '-at_install')
class TestElevatorJournal(TransactionCase):
    """The journal is evidence, so the rules that make it evidence are what
    gets tested: a number that is not the id, entries that become immutable
    once confirmed, and an idempotency key that survives a re-run.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.equipment = cls.env['maintenance.equipment'].create({
            'name': 'Journal Elevator',
            'is_elevator': True,
        })
        cls.user = new_test_user(
            cls.env, login='journal_plain_user', groups='base.group_user')
        cls.manager = new_test_user(
            cls.env, login='journal_manager',
            groups='base.group_user,maintenance.group_equipment_manager')

    def test_create_assigns_a_sequence_number(self):
        """The number comes from ir.sequence, not from the id."""
        entry = self.env['maintenance.elevator.journal'].create({
            'equipment_id': self.equipment.id,
            'event_type': 'service',
            'scope': 'Yearly service',
        })
        self.assertNotEqual(entry.name, 'New')
        self.assertTrue(entry.name.startswith('HJ/'))

    def test_confirmed_entry_is_locked(self):
        """A confirmed entry may not be edited or deleted by a plain user."""
        entry = self.env['maintenance.elevator.journal'].with_user(
            self.manager).create({
                'equipment_id': self.equipment.id,
                'event_type': 'service',
                'scope': 'Yearly service',
            })
        entry.action_confirm()
        self.assertEqual(entry.state, 'confirmed')
        self.assertEqual(entry.confirmed_by_id, self.manager)

        with self.assertRaises(AccessError):
            entry.with_user(self.user).write({'scope': 'Changed my mind'})
        with self.assertRaises(UserError):
            entry.with_user(self.manager).unlink()

    def test_manager_can_reopen(self):
        entry = self.env['maintenance.elevator.journal'].with_user(
            self.manager).create({
                'equipment_id': self.equipment.id,
                'event_type': 'service',
                'scope': 'Yearly service',
            })
        entry.action_confirm()
        entry.action_reopen()
        self.assertEqual(entry.state, 'draft')

    def test_plain_user_cannot_confirm(self):
        entry = self.env['maintenance.elevator.journal'].with_user(
            self.user).create({
                'equipment_id': self.equipment.id,
                'event_type': 'service',
                'scope': 'Yearly service',
            })
        with self.assertRaises(AccessError):
            entry.action_confirm()

    def test_create_automatic_is_confirmed(self):
        """System-created entries record something that already happened."""
        entry = self.env['maintenance.elevator.journal'].create_automatic({
            'equipment_id': self.equipment.id,
            'event_type': 'outage',
            'scope': 'Power failure',
            'source_model': 'test.source',
            'source_id': 1,
        })
        self.assertEqual(entry.state, 'confirmed')
        self.assertTrue(entry.confirmed_date)

    def test_event_type_derivation(self):
        """One derivation, name-based, used by every caller."""
        Journal = self.env['maintenance.elevator.journal']
        self.assertEqual(
            Journal.event_type_for_order_type('Service'), 'service')
        self.assertEqual(
            Journal.event_type_for_order_type('Besiktning'),
            'statutory_inspection')
        self.assertEqual(
            Journal.event_type_for_order_type('Annual Inspection'),
            'statutory_inspection')
        self.assertEqual(
            Journal.event_type_for_order_type('Reparation'), 'repair')
        self.assertEqual(
            Journal.event_type_for_order_type(False), 'repair')

    def test_backfill_is_idempotent(self):
        """Running the backfill twice must not duplicate events."""
        self.equipment.write({
            'last_inspection': fields.Date.today(),
            'operational_status': 'out_of_order',
            'out_of_order_reason': 'Door fault',
        })
        Journal = self.env['maintenance.elevator.journal']
        Journal.backfill_journals()
        first = Journal.search_count([
            ('equipment_id', '=', self.equipment.id),
        ])
        Journal.backfill_journals()
        second = Journal.search_count([
            ('equipment_id', '=', self.equipment.id),
        ])
        self.assertEqual(first, second)
        self.assertEqual(first, 3)  # initial, status, inspection

    def test_equipment_counts_journal_entries(self):
        self.env['maintenance.elevator.journal'].create({
            'equipment_id': self.equipment.id,
            'event_type': 'service',
            'scope': 'Yearly service',
        })
        self.assertEqual(self.equipment.journal_count, 1)
        action = self.equipment.action_view_journal()
        self.assertEqual(action['res_model'], 'maintenance.elevator.journal')


@tagged('post_install', '-at_install')
class TestElevatorElectricalPlan(TransactionCase):
    """ESA 2006:1 requires the plan to be made before the work starts and
    approved by someone accountable. The state machine is the control.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.equipment = cls.env['maintenance.equipment'].create({
            'name': 'Plan Elevator',
            'is_elevator': True,
        })
        cls.employee = cls.env['hr.employee'].create({
            'name': 'Safety Responsible',
        })
        cls.manager = new_test_user(
            cls.env, login='plan_manager',
            groups='base.group_user,maintenance.group_equipment_manager')

    def _create_plan(self):
        return self.env['maintenance.elevator.electrical.plan'].create({
            'equipment_id': self.equipment.id,
            'safety_responsible_id': self.employee.id,
            'work_method': 'dead',
        })

    def test_create_assigns_a_sequence_number(self):
        plan = self._create_plan()
        self.assertTrue(plan.name.startswith('EP/'))
        self.assertEqual(plan.state, 'draft')
        self.assertTrue(plan.electrical_hazard)

    def test_state_machine(self):
        plan = self._create_plan()
        plan.action_ready()
        self.assertEqual(plan.state, 'ready')
        plan.with_user(self.manager).action_approve()
        self.assertEqual(plan.state, 'approved')
        self.assertEqual(plan.approved_by_id, self.manager)
        plan.action_done()
        self.assertEqual(plan.state, 'done')

    def test_competence_warning_is_gone(self):
        """D3: the field depended on modules that are not ported."""
        self.assertNotIn(
            'competence_warning',
            self.env['maintenance.elevator.electrical.plan']._fields,
        )

    def test_equipment_counts_plans(self):
        self._create_plan()
        self.assertEqual(self.equipment.electrical_plan_count, 1)
