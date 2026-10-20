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

from odoo import models, fields


class MaintenanceElevatorType(models.Model):
    """Reference data for elevators.

    Ported from Elevata's eleven `fsm.*` reference models
    (elevator.type, mechanical.brand, control.system, car.door.type,
    shaft.door.type, bearing.config, lubrication.type, gsm.device,
    emergency.phone.type, inspection.company, order.type).

    They share the same shape — a name and an active flag — so they live
    in one model distinguished by `model_type`. Eleven near-identical
    models would be eleven near-identical tables.
    """

    _name = 'maintenance.elevator.type'
    _description = 'Elevator Reference Data'
    _order = 'model_type, sequence, name'

    name = fields.Char(string='Name', required=True, translate=True)
    model_type = fields.Selection(
        selection=[
            ('elevator', 'Elevator Type'),
            ('brand', 'Mechanical Brand'),
            ('control_system', 'Control System'),
            ('car_door', 'Car Door Type'),
            ('shaft_door', 'Shaft Door Type'),
            ('bearing', 'Bearing / Top / Pit'),
            ('lubrication', 'Lubrication Type'),
            ('gsm', 'GSM Device'),
            ('emergency_phone', 'Emergency Phone Type'),
        ],
        string='Reference Type',
        required=True,
        index=True,
    )
    code = fields.Char(string='Code', help='Short code used in reports.')
    sequence = fields.Integer(string='Sequence', default=10)
    active = fields.Boolean(string='Active', default=True)
    note = fields.Text(string='Note')

    _sql_constraints = [
        (
            'model_type_name_uniq',
            'unique(model_type, name)',
            'A reference value with this name already exists for this type.',
        ),
    ]
