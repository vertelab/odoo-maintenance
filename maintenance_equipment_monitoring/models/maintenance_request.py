import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, AccessError, ValidationError

_logger = logging.getLogger(__name__)

class MaintenanceRequest(models.Model):
    _inherit = "maintenance.equipment"

    quest_ids = fields.Many2many(comodel_name="ai.quest")
