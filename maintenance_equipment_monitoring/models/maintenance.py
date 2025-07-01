from odoo import models, fields, api, _
import requests
import json
from datetime import datetime
import ast


class Maintenance(models.Model):
    _inherit = "maintenance.equipment"

    is_monitored = fields.Boolean(string="Is Monitored")
    monitor_url = fields.Char(string="Monitor URL")
    monitor_is_running = fields.Selection(
        [("offline", "Offline"), ("done", "Running")],
        string="Monitor",
        default="offline",
        tracking=True,
    )
    monitor_log_ids = fields.One2many(
        "maintenance.equipment.server.log",
        "maintenance_id",
        string="Logs",
        readonly=True,
    )

    def server_auto_sync(self):
        servers = self
        if not servers:
            servers = self.env[self._name].search([])
        for rec in servers:
            if rec.monitor_url and rec.is_monitored:
                try:
                    ping_req = requests.get(rec.monitor_url)
                    if ping_req.status_code == 200:
                        response = json.loads(ping_req.content)
                        self.env["maintenance.equipment.server.log"].sudo().create(
                            {
                                "date": datetime.now(),
                                "monitor_log": response,
                                "maintenance_id": rec.id,
                            }
                        )
                        rec.monitor_is_running = "done"
                    else:
                        # Regardless of status_code, create a log
                        self.env["maintenance.equipment.server.log"].sudo().create(
                            {
                                "date": datetime.now(),
                                "monitor_log": ping_req.reason,
                                "maintenance_id": rec.id,
                            }
                        )
                        rec.monitor_is_running = "offline"
                except Exception as e:
                    # requests.get will raise errors in some cases when
                    # it can't connect.
                    # creates a log if it cannot connect
                    self.env["maintenance.equipment.server.log"].sudo().create(
                        {
                            "date": datetime.now(),
                            "monitor_log": str(e),
                            "maintenance_id": rec.id,
                        }
                    )
                    rec.monitor_is_running = "offline"

    def view_server_log(self):
        return {
            "name": _("Server Log - %s" % self.name),
            "type": "ir.actions.act_window",
            "res_model": "maintenance.equipment.server.log",
            "views": [(False, "tree"), (False, "form")],
            "view_mode": "tree,form",
            "domain": [("maintenance_id", "=", self.id)],
            "context": {
                "maintenance_id": self.id,
                "default_maintenance_id": self.id,
            },
        }


class MaintenanceLog(models.Model):
    _name = "maintenance.equipment.server.log"
    _description = "maintenance.equipment.server.log"
    _rec_name = "date"

    date = fields.Datetime(string="Date")
    monitor_log = fields.Text(string="Log")
    maintenance_id = fields.Many2one("maintenance.equipment", string="Maintenance")
    status = fields.Selection([('0', 'Failed'), ('1', 'Successful')], string="Status",
                              compute='_get_status_info')
    space_availability = fields.Char(string="Space Availability", compute='_get_space_availability')

    @api.depends('monitor_log')
    def _get_status_info(self):
        for rec in self:
            if rec.monitor_log:
                json_fmt = ast.literal_eval(rec.monitor_log)
                status = json_fmt.get('status', False)
                if status:
                    rec.status = str(status)
                else:
                    rec.status = str(0)
            else:
                rec.status = False

    @api.depends('monitor_log')
    def _get_space_availability(self):
        for rec in self:
            if rec.monitor_log:
                json_fmt = ast.literal_eval(rec.monitor_log)
                space_availability = json_fmt.get('space_availability', False)
                if space_availability:
                    rec.space_availability = ''.join([
                        item for item in space_availability.splitlines() if item.startswith('/dev/vd')
                    ])
            else:
                rec.space_availability = False
