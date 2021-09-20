# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2021  (<simon.rundstedt@vertel.se>)
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

import re
import ipaddress

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import ValidationError


# REGEX_IPV4 = re.compile("^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$")
# REGEX_IPV6 = re.compile(".*") # IPv6 is complicated: https://datatracker.ietf.org/doc/html/rfc5952
REGEX_MAC = re.compile("^([a-fA-F0-9]{2}:){5}[a-fA-F0-9]{2}$")

class MaintenanceEquipment(models.Model):
    '''
    Extending with basic parameters of networked equipment
    '''
    _inherit = 'maintenance.equipment'

    is_it_equipment = fields.Boolean(help="Wether or not this is networked IT equipment.")  # IT equipment doesn't need to have a known IP or MAC
    primary_ip = fields.Char(help="Main IP address used to reach the device.")
    primary_mac= fields.Char(help="Main MAC address used by the device.")
    primary_domain = fields.Char(help="Main domain name used to reach the device.")

    # Potential future fields : alt_ips, alt_macs etc...

    @api.constrains('primary_ip')
    def _ip_constraint(self):
        '''Constrain IP addresses to valid IPv4 or IPv6 addresses'''
        for record in self:
            try:
                ipaddress.ip_address(record.primary_ip)
            except ValueError as e:
                raise ValidationError(str(e))
    @api.constrains("primary_mac")
    def _mac_constraint(self):
        '''Constrain MAC addresses to valid mac addresses'''
        for record in self:
            if not REGEX_MAC.match(record.primary_mac):
                raise ValidationError("Input address {} not a valid MAC address. Check spelling, and leading and trailing white spaces.")
