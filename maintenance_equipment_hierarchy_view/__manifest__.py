{
    'name': 'Maintenance Equipments Hierarchy View',
    'version': '18.0.0.1.0',
    'summary': 'Maintenance Equipments Hierarchy View',
    'category': 'Project',
    'description': """
        Maintenance Equipments Hierarchy View.
    """,
    'author': 'Vertel AB',
    'website': 'https://vertel.se/apps/odoo-maintenance/maintenance_equipment_hierarchy_view',
    'images': ['static/description/banner.png'],  # 560x280 px.
    'license': 'AGPL-3',
    'contributor': '',
    'maintainer': 'Vertel AB',
    'repository': 'https://github.com/vertelab/odoo-project',
    'depends': ['maintenance_equipment_hierarchy', 'web_hierarchy'],
    'data': [
        'views/maintenance_equipment_views.xml',
    ],
    'assets': {
        'web.assets_backend_lazy': [
            'maintenance_equipment_hierarchy_view/static/src/views/**/*',
        ],
    },
    'installable': True,
}