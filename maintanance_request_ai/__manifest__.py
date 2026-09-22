{
    'website': 'https://vertel.se/apps/odoo-maintenance/maintanance_request_ai',
    "name": "Maintenance Request AI",
    "version": "1.0",
    'license': 'AGPL-3',
    "depends": ["maintenance", "ai_agent"],
    "data": [
        'data/ai_agent_data.xml',
    ],
    "installable": True,
    'application': True,
}
