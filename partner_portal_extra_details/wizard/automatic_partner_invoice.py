# -*- coding: utf-8 -*-
from odoo import fields, models, api, _

class AutomaticPartnerInvoice(models.TransientModel):
    _name = 'automatic.partner.invoice'

    @api.multi
    def create_automatic_invoice(self):
        Partner = self.env['res.partner']
        ids = self.env.context.get('active_ids', False)
        partners = Partner.browse(ids)
        Partner.create_partner_invoice(partners)
        return True