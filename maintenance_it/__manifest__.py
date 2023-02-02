# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo SA, Open Source Management Solution, third party addon
#    Copyright (C) 2021- Vertel AB (<https://vertel.se>).
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
    'name': 'Maintenance: IT',
    'summary': 'Add IT fields to the maintenance module.',
    'category': 'Helpdesk',
    'author': 'Vertel AB',
    'contributor': '',
    'maintainer': 'Vertel AB',
    'repository': 'https://github.com/vertelab/odoo-maintenance',
    'version': '14.0.1.0.0',
    # Version ledger: 14.0 = Odoo version. 1 = Major. Non regressionable code. 2 = Minor. New features that are regressionable. 3 = Bug fixes
    'website': 'https://vertel.se/apps/odoo-maintenance/maintenance_it',
    'images': ['static/description/banner.png'], # 560x280 px.
    'license': 'AGPL-3',

    'description': """
        Adding helper IT fields such as IP, MAC and domain.

        This module is maintained from: https://github.com/vertelab/odoo-maintenance/
    """,
    'depends': ['base','maintenance'],
    # always loaded
    'data': [
        'views/maintenance_views.xml',
    ],
}
