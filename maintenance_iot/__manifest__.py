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

{
    'name': 'Maintenance: IoT',
    'version': '18.0.1.0.0',
    # Version ledger: 18.0 = Odoo version. 1 = Major. Non regressionable code.
    # 0 = Minor. 1 = Bug fixes
    'summary': 'Sensor readings, alarm thresholds and automatic fault orders.',
    'category': 'Maintenance',
    'description': '''
Maintenance: IoT
================

    An asset that reports its own state: a pump's run hours, a motor's
    temperature, a door's cycle count. That stream is the difference between
    a service company that finds out something is wrong when the customer
    calls, and one that sends a technician before anyone notices.

    This module is the receiving end. It does not talk to the hardware:
    every gateway speaks its own protocol — Modbus, MQTT, a vendor cloud API
    — and that belongs in a connector, one per vendor. What this defines is
    the model the connector writes into:

        maintenance.sensor          a measured value on an equipment record
        maintenance.sensor.reading  one measurement, with a timestamp

    A connector calls sensor.add_reading(value) and the rest happens here.
    Thresholds and alarms are the module's business, not the connector's.

    A sensor carries a warning and a critical threshold and a direction:
    run hours and temperature alarm above, a pressure sensor might alarm
    below. A threshold of 0 means "not set" — a sensor with no critical
    threshold never goes critical.

    Crossing the warning posts a message. Crossing the critical opens a
    maintenance request, because a critical reading on an asset means
    someone has to go there. The reading is recorded on the request so the
    technician sees the value, not just the fact that something happened.

    Readings are kept rather than overwritten: the trend is the point. A
    door that has done 40 000 cycles in a year needs adjustment, and that is
    only visible if the history is there.

    Features:

        - Sensors per equipment: cycles, run hours, temperature, state
        - Readings with timestamp, kept for trend
        - Warning and critical thresholds, configurable per sensor
        - Alarm posts a message or opens a maintenance request
        - Sensor state visible on the equipment
    ''',
    'author': 'Vertel Sverige AB',
    'website': 'https://vertel.se/apps/odoo-maintenance/maintenance_iot',
    'license': 'AGPL-3',
    'contributor': '',
    'maintainer': 'Vertel Sverige AB',
    'repository': 'https://github.com/vertelab/odoo-maintenance',
    'depends': [
        'maintenance',
        'mail',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/maintenance_sensor_views.xml',
        'views/maintenance_equipment_views.xml',
        'views/maintenance_menu.xml',
    ],
    'application': False,
    'installable': True,
    'auto_install': False,
}
