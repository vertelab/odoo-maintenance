import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, AccessError, ValidationError

_logger = logging.getLogger(__name__)

class AIQuest(models.Model):
    _inherit = "ai.quest"

    quest_ids = fields.Many2many(comodel_name="ai.quest")
    