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

from psycopg2 import IntegrityError

from odoo import fields
from odoo.tests import TransactionCase, tagged
from odoo.tools import mute_logger


@tagged('post_install', '-at_install')
class TestMaintenanceElevator(TransactionCase):
    """Covers the three things the port must get right:

    1. Reference data is one model with a model_type discriminator.
    2. The risk register computes score and severity from the 1-5 scale.
    3. The inspection window reads its threshold from a system parameter.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.equipment = cls.env['maintenance.equipment'].create({
            'name': 'Test Elevator',
            'is_elevator': True,
            'elevator_number': 'TEST-001',
            'has_machine_room': True,
            'tech_machine_room': '<p>Machine room notes</p>',
        })

    def test_reference_data_is_one_model(self):
        """Every reference type lives in maintenance.elevator.type."""
        types = self.env['maintenance.elevator.type'].search([
            ('model_type', '=', 'elevator'),
        ])
        self.assertTrue(types, 'Seed data for elevator types is missing')

        # One model, many model_types — not eleven tables.
        model_types = set(
            self.env['maintenance.elevator.type'].search([]).mapped('model_type')
        )
        self.assertIn('elevator', model_types)
        self.assertIn('lubrication', model_types)

    def test_reference_name_unique_per_type(self):
        """The same name may exist per type, but not twice within one type."""
        ElevatorType = self.env['maintenance.elevator.type']
        ElevatorType.create({'name': 'Duplicate Probe', 'model_type': 'gsm'})
        with mute_logger('odoo.sql_db'), self.assertRaises(IntegrityError):
            ElevatorType.create({'name': 'Duplicate Probe', 'model_type': 'gsm'})

    def test_risk_score_is_consequence_times_probability(self):
        risk = self.env['maintenance.elevator.risk'].create({
            'name': 'Door does not close',
            'equipment_id': self.equipment.id,
            'hazard': 'Passenger can be trapped',
            'consequence': '3',
            'probability': '5',
        })
        self.assertEqual(risk.risk_score, 15)
        self.assertEqual(risk.severity, 'critical')

    def test_risk_severity_thresholds(self):
        """>=15 critical, >=9 high, >=4 medium, else low."""
        Risk = self.env['maintenance.elevator.risk']
        cases = [
            ('5', '5', 25, 'critical'),
            ('3', '3', 9, 'high'),
            ('2', '2', 4, 'medium'),
            ('1', '2', 2, 'low'),
        ]
        for consequence, probability, score, severity in cases:
            risk = Risk.create({
                'name': 'Threshold %sx%s' % (consequence, probability),
                'equipment_id': self.equipment.id,
                'hazard': 'Probe',
                'consequence': consequence,
                'probability': probability,
            })
            self.assertEqual(risk.risk_score, score)
            self.assertEqual(risk.severity, severity)

    def test_risk_confirm_and_reset(self):
        risk = self.env['maintenance.elevator.risk'].create({
            'name': 'Confirm probe',
            'equipment_id': self.equipment.id,
            'hazard': 'Probe',
        })
        self.assertEqual(risk.state, 'draft')
        risk.action_confirm()
        self.assertEqual(risk.state, 'confirmed')
        self.assertTrue(risk.confirmed_date)
        risk.action_reset_to_draft()
        self.assertEqual(risk.state, 'draft')
        self.assertFalse(risk.confirmed_date)

    def test_inspection_soon_uses_system_parameter(self):
        """The warning window is configuration, not code."""
        ICP = self.env['ir.config_parameter'].sudo()
        today = fields.Date.context_today(self.equipment)

        ICP.set_param('maintenance_elevator.inspection_warning_days', 60)
        self.equipment.next_inspection_date = today + timedelta(days=30)
        self.equipment.invalidate_recordset(['inspection_soon'])
        self.assertTrue(self.equipment.inspection_soon)

        self.equipment.next_inspection_date = today + timedelta(days=90)
        self.equipment.invalidate_recordset(['inspection_soon'])
        self.assertFalse(self.equipment.inspection_soon)

        # A wider window must pull the 90-day inspection back in.
        ICP.set_param('maintenance_elevator.inspection_warning_days', 120)
        self.equipment.invalidate_recordset(['inspection_soon'])
        self.assertTrue(self.equipment.inspection_soon)

        ICP.set_param('maintenance_elevator.inspection_warning_days', 60)

    def test_out_of_order_actions(self):
        self.assertEqual(self.equipment.operational_status, 'operational')
        self.equipment.action_mark_out_of_order()
        self.assertEqual(self.equipment.operational_status, 'out_of_order')
        self.assertTrue(self.equipment.out_of_order_date)
        self.equipment.action_restore_to_service()
        self.assertEqual(self.equipment.operational_status, 'operational')
        self.assertFalse(self.equipment.out_of_order_date)
