# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2021  (<jakob@jakob-NUC8i5BEK>)
#    All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import models, fields, api, exceptions, _
from odoo.tools.translate import html_translate

import logging

_logger = logging.getLogger(__name__)


class MaintenanceRequest(models.Model):
    _name = "maintenance.request"
    _inherit = [
        "maintenance.request",
        "website.seo.metadata",
        "website.published.mixin",
    ]

    website_description = fields.Html(
        "Website Maintenance Request Full Description",
        strip_style=True,
        translate=html_translate,
    )
    website_short_description = fields.Text(
        "Website Maintenance Request Short Description", translate=True
    )

    severity_rate = fields.Selection(
        [("None", "None"), ("Low", "Low"), ("Medium", "Medium"), ("High", "High")],
        string="Severity Rate",
    )

    cve_action = fields.Text(string="Action")

    cve_analysis = fields.Text(string="Analysis")

    cve_package = fields.Char(string="Package")

    is_cve = fields.Boolean(string="Is CVE", related="maintenance_team_id.is_cve")

    maintenance_tag_ids = fields.Many2many("maintenance.tag", string="Tags")

    def _compute_website_url(self):
        super(MaintenanceRequest, self)._compute_website_url()
        for cve in self:
            cve.website_url = f"/security/cve/{cve.id}"

    def check_on_ubuntu(self):
        return {
            "type": "ir.actions.act_url",
            "name": "Ubuntu Security",
            "target": "_blank",
            "url": "https://ubuntu.com/security/%s" % self.name,
        }

    def check_on_cert(self):
        return {
            "type": "ir.actions.act_url",
            "name": "Cert Security",
            "target": "_blank",
            "url": "https://www.cert.se/sok?s%s" % self.name,
        }

    def check_on_cve_mitre(self):
        return {
            "type": "ir.actions.act_url",
            "name": "CVE Mitre",
            "target": "_blank",
            "url": "https://cve.mitre.org/cgi-bin/cvename.cgi?name=%s" % self.name,
        }


class MaintenanceTeam(models.Model):
    _inherit = "maintenance.team"

    is_cve = fields.Boolean(string="Is CVE", default=False)


class MaintenanceTags(models.Model):
    _name = "maintenance.tag"
    _description = "Maintenance Tag"

    name = fields.Char(string="Tag")
