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
    'name': 'Maintenance: Equipment Inspection',
    'version': '18.0.1.0.0',
    # Version ledger: 18.0 = Odoo version. 1 = Major. Non regressionable code.
    # 0 = Minor. 1 = Bug fixes
    'summary': 'Structured inspections with checklists and remarks.',
    'category': 'Maintenance',
    'description': '''
Maintenance: Equipment Inspection
=================================

    An inspection is not a maintenance request.

    A request says "something is wrong, fix it" and carries a free-text
    description. An inspection says "I went through these twelve points and
    here is what I found" — and that is what a supervisory authority asks
    for. Odoo has the request; it has nothing for the inspection.

    What this adds:

        maintenance.inspection.template       the points to check
        maintenance.inspection.template.line  one point
        maintenance.equipment.inspection      one inspection of one asset
        maintenance.equipment.inspection.line one point's result

    An inspection is tied to a single maintenance.equipment record. That is
    the right level: an elevator, a fire extinguisher and a ventilation unit
    are all equipment, and each has its own inspection regime. A property
    view is a computed One2many on the property, not a second model.

    The remark level is aggregated from the lines:

        none          every point OK or not applicable
        remark        at least one remark
        red_remark    at least one red remark

    A red remark is the one that matters: on an elevator it means the asset
    must be taken out of service. What "out of service" means is industry
    specific, so this module only records the level — the industry module
    acts on it.

    Features:

        - Inspection templates per equipment category
        - Points copied at creation, so editing a template does not rewrite
          history
        - Result per point: OK, remark, red remark, not applicable
        - Photo and note per point
        - Turn a remark into a maintenance request
        - Aggregated remark level on the inspection
    ''',
    'author': 'Vertel Sverige AB',
    'website': 'https://vertel.se/apps/odoo-maintenance/maintenance_equipment_inspection',
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
        'data/inspection_sequence.xml',
        'views/maintenance_inspection_template_views.xml',
        'views/maintenance_equipment_inspection_views.xml',
        'views/maintenance_equipment_views.xml',
        'views/maintenance_menu.xml',
    ],
    'application': False,
    'installable': True,
    'auto_install': False,
}
