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
    'name': 'Maintenance: Elevator',
    'summary': 'Elevator (lift) data on maintenance assets.',
    'category': 'Maintenance',
    'author': 'Vertel Sverige AB',
    'contributor': '',
    'maintainer': 'Vertel Sverige AB',
    'repository': 'https://github.com/vertelab/odoo-maintenance',
    'version': '18.0.1.0.0',
    # Version ledger: 18.0 = Odoo version. 1 = Major. Non regressionable code.
    # 0 = Minor. 1 = Bug fixes
    'images': ['static/description/banner.png'],  # 560x280 px.
    'license': 'AGPL-3',
    'website': 'https://vertel.se/apps/odoo-maintenance/maintenance_elevator',
    'description': '''
Maintenance: Elevator
=====================

    An elevator is an asset in a maintenance system, not a location.

    This module adds elevator-specific data to `maintenance.equipment`:
    identity, technical configuration, statutory inspection tracking,
    operational status and a risk register.

    Designed to sit on top of `property_maintanance`, so every elevator
    reaches its property through `maintenance.equipment.property_id` and
    its address through the property's partner.

    Features:

        - Elevator flag and identity (manufacturing number, year, stops)
        - Technical configuration (type, brand, control system, doors,
          bearings, lubrication, GSM, emergency phone)
        - Eight sectioned technical documentation fields
        - Statutory inspection tracking with due-date warning
        - Out-of-order tracking with reason and date
        - Risk register with computed score and severity
    ''',
    'depends': [
        'maintenance',
        'property_maintanance',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/maintenance_elevator_data.xml',
        'views/maintenance_elevator_type_views.xml',
        'views/maintenance_equipment_views.xml',
    ],
    'application': False,
    'installable': True,
}
