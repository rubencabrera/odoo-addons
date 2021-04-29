# Copyright 2020 Rubén Cabrera Martínez <dev@rubencabrera.es>
# Copyright 2020 CBMP Rayito Salinero
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ResPartner(models.Model):
    """Adds simple emergency contact fields"""
    _inherit = "res.partner"

    attach_receipt = fields.Boolean(
        string="Attach receipt",
        help="Allows to know if the user has attached the receipt of payment."
    )

    shirt_size = fields.Selection(
        string="Talla de camiseta",
        selection=[
            ("4", "4"),
            ("8", "8"),
            ("12", "12"),
            ("xs", "XS"),
            ("s", "S"),
            ("m", "M"),
            ("l", "L"),
            ("xl", "XL"),
            ("xxl", "XXL"),
            ("xxxl", "XXXL"),
        ]
    )

    top_size = fields.Selection(
        string="Talla de top",
        selection=[
            ("xxs", "XXS"),
            ("xs", "XS"),
            ("s", "S"),
            ("m", "M"),
            ("l", "L"),
            ("xl", "XL"),
            ("xxl", "XXL"),
        ]
    )
    tutor_phone = fields.Char(string="Emergency phone")
    tutor_name = fields.Char(string="Nombre del contacto de emergencia")
    validate_portal_user = fields.Boolean(
        string="Validate portal user",
        help="Allows to validate the user registered in the portal."
    )
    valid_receipt = fields.Boolean(
        string="Validate receipt",
        help="Allows to validate the attachment receipt."
    )

    @api.multi
    def write(self, values):
        if values.get('validate_portal_user'):
            self._send_mail_to_new_validate_user()
        if values.get('valid_receipt'):
            self._send_validate_mail()
        return super(ResPartner, self).write(values)

    @api.multi
    def _send_mail_to_new_validate_user(self):
        """
        This function sends an email to the new validated user of the portal.
        """
        self.ensure_one()
        AccountInvoice = invoices = self.env['account.invoice']
        dom = [
            ('partner_id', '=', self.id),
            ('state', '=', 'draft')
        ]
        invoices |= AccountInvoice.search(
            dom, order='date_invoice asc', limit=1
        )
        if not invoices:
            invoices |= self._create_partner_invoice()
        invoices._send_payment_terms_mail()

    def _create_partner_invoice(self):
        self.ensure_one()
        partner = self
        AccountInvoice = self.env['account.invoice']
        invoice_line_values = self._prepare_invoice_line_values()
        company_id = partner.company_id
        origin = self._get_invoice_origin()
        values = {
            'type': 'out_invoice',
            'reference': partner.name,
            'partner_id': partner.id,
            'date_invoice': fields.Date.today(),
            'invoice_line_ids': invoice_line_values,
            'currency_id': company_id.currency_id.id,
            'company_id': company_id.id,
            'origin': origin
        }
        invoice = AccountInvoice.new(values)
        invoice._onchange_partner_id()
        invoice = AccountInvoice.create(values)
        return invoice

    def _get_invoice_origin(self):
        self.ensure_one()
        return '{} {} {}'.format(
            self.firstname, self.lastname, self.lastname2
        )

    def _prepare_invoice_line_values(self):
        self.ensure_one()
        product = self.company_id.product_id
        if not product:
            raise UserError(
                _('You must select the service to create invoice.')
            )
        account_id = product.categ_id.property_account_income_categ_id
        values = [(0, 0, {
            'name': product.name,
            'origin': 'Factura de registro',
            'account_id': account_id.id,
            'price_unit': product.list_price,
            'quantity': 1.0,
            'uom_id': product.uom_id.id,
            'product_id': product.id,
            'invoice_line_tax_ids': [(6, 0, [product.taxes_id.id])],
        })]
        return values

    def _send_validate_mail(self):
        self.ensure_one()
        partner = self
        module_name = 'partner_portal_extra_details'
        template = self.env.ref(
            "%s.email_template_send_user_valid_receipt" % module_name
        )
        template.send_mail(partner.id, force_send=True)

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
