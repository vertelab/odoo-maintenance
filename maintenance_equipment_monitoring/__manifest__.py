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

# Copyright 2016-2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

{
    "name": "Maintenance: equipment monitoring",
    "summary": "For other Odoo databases to monitor the status of their server.",
    'category': 'Helpdesk',
    "author": "Vertel AB",
    "contributor": "",
    "maintainer": "Vertel AB",
    "repository": "https://github.com/vertelab/odoo-maintenance",
    "version": "14.0.1.0.2",
    # Version ledger: 14.0 = Odoo version. 1 = Major. Non regressionable code.
    # 2 = Minor. New features that are regressionable. 3 = Bug fixes
    "license": "AGPL-3",
    "website": "https://vertel.se/apps/odoo-maintenance/maintenance_equipment_monitoring",
    "description": """
       The purpose of this module is to monitor other odoo databases to see the
       status of their server. In order to query other databases the need
       "maintenance_monitoring_status" or "maintenance_monitoring_status_extension" installed.

       In order to specify which database you want to monitor you fill the Monitor URL
       field on the equipment view and there is  a ping button to trigger this query.
       The url needs to look like: http ://hostname/monitoring/status?db=databasename.

       There is also cron job called "Ping Remote Server" that will ping every
       60 minutes to all equipment that has "Is Monitored" field set to true.
    """,
    "depends": ["maintenance", "maintenance_monitoring_status_extension"],
    "data": [
        "security/ir.model.access.csv",
        "views/maintenance_view.xml",
        "views/maintenance_server_log_view.xml",
        "data/cron.xml",
    ],
    "installable": True,
}
