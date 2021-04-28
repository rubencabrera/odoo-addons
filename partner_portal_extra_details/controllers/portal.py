# -*- coding: utf-8 -*-

import base64
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.http import request, route


class RayitoCustomerPortal(CustomerPortal):

    MANDATORY_BILLING_FIELDS = [
        "birthdate_date",
        "city",
        "country_id",
        "email",
        "gender",
        "name",
        "phone",
        "street",
        "tutor_phone",
        "tutor_name",
        "vat",
    ]
    OPTIONAL_BILLING_FIELDS = [
        "company_name",
        "state_id",
        "zipcode",
    ]

    def _get_mandatory_billing_fields(self):
        MANDATORY_BILLING_FIELDS = [
            "birthdate_date",
            "city",
            "country_id",
            "email",
            "gender",
            "name",
            "phone",
            "street",
            "tutor_phone",
            "tutor_name",
            "vat",
        ]
        return MANDATORY_BILLING_FIELDS

    def _get_optional_billing_fields(self):
        OPTIONAL_BILLING_FIELDS = [
            "company_name",
            "state_id",
            "zipcode",
        ]
        return OPTIONAL_BILLING_FIELDS

    @route(['/my/account'], type='http', auth='user', website=True)
    def account(self, redirect=None, **post):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        values.update({
            'error': {},
            'error_message': [],
        })

        if post:
            error, error_message = self.details_form_validate(post)
            values.update({'error': error, 'error_message': error_message})
            values.update(post)
            if not error:
                values = {
                    key: post[key]
                    for key in self._get_mandatory_billing_fields()}
                values.update(
                    {
                        key: post[key]
                        for key in self._get_optional_billing_fields()
                        if key in post
                    }
                )
                values.update({'zip': values.pop('zipcode', '')})
                partner.sudo().write(values)
                if redirect:
                    return request.redirect(redirect)
                return request.redirect('/my/home')

        countries = request.env['res.country'].sudo().search([])
        states = request.env['res.country.state'].sudo().search([])

        values.update({
            'partner': partner,
            'countries': countries,
            'states': states,
            'has_check_vat': hasattr(request.env['res.partner'], 'check_vat'),
            'redirect': redirect,
            'page_name': 'my_details',
        })

        response = request.render("portal.portal_my_details", values)
        response.headers['X-Frame-Options'] = 'DENY'
        return response

    @route(['/my/receipt'], type='http', auth='user', website=True)
    def receipt(self, redirect=None, **post):
        values = self._prepare_portal_layout_values()
        response = self._render_receipt_payment(values)
        if post.get('attachment', False):
            attachment = self._attach_payment_receipt(post)
            if not attachment:
                return response
            values.update({
                'attachment': attachment
            })
            self._set_partner_data()
            return request.redirect('/my')
        return response

    def _attach_payment_receipt(self, post):
        Attachment = request.env['ir.attachment']
        partner = request.env.user.partner_id
        name = post.get('attachment').filename
        file = post.get('attachment')
        data = file.read()
        attachment = Attachment.sudo().create({
            'name': name,
            'datas_fname': name,
            'res_name': name,
            'type': 'binary',
            'res_model': 'res.partner',
            'res_id': partner.id,
            'datas': base64.b64encode(data)
        })
        return attachment

    def _render_receipt_payment(self, values):
        response = request.render(
            "partner_portal_extra_details.portal_my_details_receipt_payment",
            values
        )
        response.headers['X-Frame-Options'] = 'DENY'
        return response

    def _set_partner_data(self):
        partner = request.env.user.partner_id
        partner.write({'attach_receipt': True})
