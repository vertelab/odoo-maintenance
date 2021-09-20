# -*- coding: utf-8 -*-
{
    'name': "Maintenance IT",

    'summary': """
        Add IT fields to the maintenance module.""",

    'description': """
        Adding helper IT fields such as IP, MAC and domain.

        This module is maintained from: https://github.com/vertelab/odoo-maintenance/
    """,
    'author': "Vertel AB",
    'website': "https://vertel.se",
    'category': 'other',
    'version': '14.0.1.0.0',
    'depends': ['base','maintenance'],
    # always loaded
    'data': [
        'views/maintenance_views.xml',
    ],
}
