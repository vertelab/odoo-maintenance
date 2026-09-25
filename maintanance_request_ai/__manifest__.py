{
    'website': 'https://vertel.se/apps/odoo-maintenance/maintanance_request_ai',
    "name": "Maintenance Request AI",
    'summary': "Adds AI assistance to maintenance requests.",
    'description': '''
Maintenance Request AI
======================

    Adds AI assistance to maintenance requests.

    Features:

        - Extends Odoo: Builds on ai.agent, maintenance.request.
    ''',
    'version': '18.0.1.1.0',
    'license': 'AGPL-3',
    "depends": ["maintenance", "ai_agent"],
    "data": [
        'data/ai_agent_data.xml',
    ],
    "installable": True,
    'application': True,
}
