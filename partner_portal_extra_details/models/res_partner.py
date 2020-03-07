# Copyright 2020 Rubén Cabrera Martínez <dev@rubencabrera.es>
# Copyright 2020 CBMP Rayito Salinero
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, api, _


class ResPartner(models.Model):
    """Adds simple emergency contact fields"""
    _inherit = "res.partner"

    tutor_phone = fields.Char(string="Emergency phone")
    tutor_name = fields.Char(string="Nombre del contacto de emergencia")

    @api.multi
    def create_partner_invoice(self, partner_ids):
        Account_invoice = self.env['account.invoice']
        company_id = self.env.ref('base.main_company')
        line_vals = self.create_invoiced_line()
        for partner in partner_ids:
            invoice_vals = {
                'type': 'out_invoice',
                'reference': partner.name,
                'partner_id': partner.id,
                'date_invoice': fields.Date.today(),
                'invoice_line_ids': line_vals,
                'currency_id': company_id.currency_id.id,
                'company_id': company_id.id,
                'origin': partner.firstname
            }
            invoice_id = Account_invoice.create(invoice_vals)
            invoice_id._onchange_partner_id()
        return True

    def create_invoiced_line(self):
        product_id = \
            self.env.ref('partner_portal_extra_details.invoice_payment')
        account_id = product_id.categ_id.property_account_income_categ_id
        tax_id = self.env.ref('l10n_es.1_account_tax_template_s_iva21s')
        line_vals = [(0, 0, {
            'name': product_id.name,
            'origin': 'Factura de registro',
            'account_id': account_id.id,
            'price_unit': product_id.list_price,
            'quantity': 1.0,
            'uom_id': product_id.uom_id.id,
            'product_id': product_id.id,
            'invoice_line_tax_ids': [(6, 0, [tax_id.id])],
        })]
        return line_vals

    @api.model
    def create(self, vals):
        res = super(ResPartner, self).create(vals)
        self.create_partner_invoice(res)
        return res
