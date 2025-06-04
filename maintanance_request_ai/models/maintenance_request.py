from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging
_logger = logging.getLogger(__name__)


class MaintenanceRequest(models.Model):
    _inherit = 'maintenance.request'

    ai_quest_id = fields.Many2one('ai.quest', string="AI Quest", readonly=True)

    @api.model
    def create(self, vals):
        request = super().create(vals)
        _logger.info(" Maintenance Request created: %s", request)

        if not request.ai_quest_id:
            ai_quest = self.env['ai.quest'].create({
                'name': f"[{request.id}] {request.name or 'Maintenance Request'}",
                'ai_type': 'default',
                'init_type': 'channel',
                'status': 'active',
                'code': """result = quest.build(session=session,message=message_body).invoke(message_invoke)""",
            })
            request.ai_quest_id = ai_quest

            self.env['ai.quest.agent'].create({
                'ai_agent_id': self.env.ref('maintanance_request_ai.ai_agent_maintenance_chat').id,
                'ai_quest_id': ai_quest.id,
            })

            channel = self.env['discuss.channel'].create({
                'name': f"[{request.id}] {request.name or 'Maintenance'}",
                'ai_quest_id': ai_quest.id,
                'description': _('Chat with maintenance request'),
            })

            ai_quest.channel_id = channel.id
            _logger.info(" Created AI Quest + Channel for maintenance request.")

        return request
