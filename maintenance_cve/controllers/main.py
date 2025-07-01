# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import http, _
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.exceptions import AccessError, MissingError
from collections import OrderedDict
from odoo.http import request


class MaintenanceController(CustomerPortal):

    @http.route(['/security/cve-list', '/security/cve-list/page/<int:page>'], auth='public', type='http', website=True)
    def maintenance_security_list(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, **kw):

        values = {} # self._prepare_portal_layout_values()
        maintenance_id = request.env['maintenance.request']

        domain = [
            ('website_published', '=', True), ('is_cve', '=', True),
        ]

        searchbar_sortings = {
            'request_date': {'label': _('Request Date'), 'cve': 'request_date desc'},
            'name': {'label': _('Title'), 'cve': 'name desc'},
            'maintenance_type': {'label': _('Type'), 'cve': 'maintenance_type'},
        }
        # default sort by order
        if not sortby:
            sortby = 'request_date'
        order = searchbar_sortings[sortby]['cve']

        searchbar_filters = {
            'all': {'label': _('All'), 'domain': []},
            'maintenance_type': {'label': _('Type'), 'domain': [('maintenance_type', '=', ('corrective', 'preventive'))]},
        }
        # default filter by value
        if not filterby:
            filterby = 'all'
        domain += searchbar_filters[filterby]['domain']

        # count for pager
        cve_maintenance_count = maintenance_id.sudo().search_count(domain)
        # pager
        pager = portal_pager(
            url="/security/cve-list",
            url_args={'sortby': sortby},
            total=cve_maintenance_count,
            page=page,
            step=self._items_per_page
        )
        # content according to pager and archive selected
        cve_maintenances = maintenance_id.sudo().search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_maintenance_history'] = cve_maintenances.ids[:100]
        odoo_versions = request.env['maintenance.tag'].sudo().search([('name', 'ilike', 'Odoo%')])

        values.update({
            'date': date_begin,
            'maintenances': cve_maintenances,
            'page_name': 'maintenance',
            'pager': pager,
            'default_url': '/security/cve-list',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
            'filterby': filterby,
            'odoo_versions': odoo_versions
        })
        return request.render("maintenance_cve.portal_cve_maintenance_list", values)

    @http.route(['/security/cve/<int:maintenance_id>', '/secruity/cve/<model("maintenance.request"):maintenance>'], auth='public', type='http', website=True) # 
    def maintenance_security(self, maintenance=False, maintenance_id=False, **kw):
        if not maintenance:
            maintenace = request.env['maintenance.request'].sudo().browse(maintenance_id)
        
        if maintenace.exists():
            values = {
                'maintenance': maintenace,
                'main_object': maintenace,
                'edit_page': False
            }
            
            return request.render("maintenance_cve.portal_cve_maintenance", values)
