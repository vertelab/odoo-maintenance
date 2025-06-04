from odoo import models, _
from bs4 import BeautifulSoup


class AiAgent(models.Model):
    _inherit = 'ai.agent'

    def agent_extra_context(self, quest, record=None):
        res = super().agent_extra_context(quest=quest, record=record)
        if self.ai_type == "maintenance-chat":
            request_id = self.env['maintenance.request'].search([('ai_quest_id', '=', quest.id)], limit=1)
            if request_id:
                res['Request Name'] = request_id.name
                res['Request Equipment'] = request_id.equipment_id.name if request_id.equipment_id else ''
                res['Request Category'] = request_id.category_id.name if request_id.category_id else ''
                res['Request Description'] = request_id.description or ''
                res['Responsible'] = request_id.user_id.name if request_id.user_id else ''
                res['Maintenance Type'] = request_id.maintenance_type
                res['Scheduled Date'] = request_id.schedule_date
                res['Deadline'] = request_id.date_deadline
                res['Priority'] = request_id.priority
                res['Request Solution'] = self._maintenance_solution(request_id)
        return res

    def _maintenance_solution(self, request):
        comment_messages = request.message_ids.filtered(lambda m: m.message_type == 'comment')
        solution = _('No Solution Provided Yet!')
        if comment_messages:
            solution = BeautifulSoup(
                comment_messages[0].body.encode('utf-8').decode('unicode_escape'), 'html.parser'
            ).get_text()
        return solution
