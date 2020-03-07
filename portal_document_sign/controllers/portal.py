# -*- coding: utf-8 -*-

from odoo.addons.portal.controllers.portal import (
    CustomerPortal, pager as portal_pager)
from odoo.http import request, route
from odoo import _


class AgreementPortal(CustomerPortal):

    def _prepare_portal_layout_values(self):
        values = super(AgreementPortal, self)._prepare_portal_layout_values()
        agreement_count = request.env['agreement'].search_count([])
        values['agreement_count'] = agreement_count
        return values

    # ------------------------------------------------------------
    # My Agreements
    # ------------------------------------------------------------

    def _agreement_get_page_view_values(
            self, agreement, access_token, **kwargs):
        values = {
            'page_name': 'agreement',
            'agreement': agreement,
        }
        # TODO: en lo del history no estoy nada seguro
        return self._get_page_view_values(
            agreement,
            access_token,
            values,
            'my_agreement_history', False, **kwargs)

    @route(
        ['/my/agreements', '/my/agreements/page/<int:page>'],
        type='http', auth="user", website=True)
    def portal_my_agreements(
            self, page=1, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        Agreement = request.env['agreement']

        domain = []

        searchbar_sortings = {
            'name': {'label': _('Autorización'), 'order': 'name desc'},
            'documentbase_id': {
                'label': _('Documento'), 'order': 'documentbase'},
        }
        # default sort by order
        if not sortby:
            sortby = 'name'
        order = searchbar_sortings[sortby]['order']

        # TODO: esto no lo tengo nada claro
        archive_groups = self._get_archive_groups('agreement', domain)

        # count for pager
        agreement_count = Agreement.search_count(domain)
        # pager
        pager = portal_pager(
            url="/my/agreements",
            url_args={
                'sortby': sortby
            },
            total=agreement_count,
            page=page,
            step=self._items_per_page
        )
        # content according to pager and archive selected
        agreements = Agreement.search(
            domain,
            order=order,
            limit=self._items_per_page,
            offset=pager['offset']
        )
        request.session['my_agreements_history'] = agreements.ids[:100]
        values.update({
            'agreements': agreements,
            'page_name': 'agreement',
            'pager': pager,
            'archive_groups': archive_groups,
            'default_url': '/my/agreements',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
        })
        return request.render(
            "portal_document_sign.portal_my_agreements", values)
