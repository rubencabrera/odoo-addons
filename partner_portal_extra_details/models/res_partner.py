# Copyright 2020 Rubén Cabrera Martínez <dev@rubencabrera.es>
# Copyright 2020 CBMP Rayito Salinero
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo import api, fields, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

CATEGORY_BY_AGE = {
    tuple(range(0, 9)): _('SUB-8'),
    tuple(range(9, 11)): _('SUB-10'),
    tuple(range(11, 13)): _('SUB-12'),
    tuple(range(13, 15)): _('SUB-14'),
    tuple(range(15, 17)): _('SUB-16'),
    tuple(range(17, 19)): _('SUB-18'),
    tuple(range(19, 120)): _('ABSOLUTE'),
}


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
    uniform_number = fields.Integer(string="Dorsal")
    validate_portal_user = fields.Boolean(
        string="Validate portal user",
        help="Allows to validate the user registered in the portal."
    )
    valid_receipt = fields.Boolean(
        string="Validate receipt",
        help="Allows to validate the attachment receipt."
    )
    player_category = fields.Char(
        string='Player category',
        compute='_compute_player_category',
        store=True,
    )

    @api.multi
    def write(self, values):
        if values.get('validate_portal_user'):
            self._send_mail_to_new_validate_user()
            self._grant_portal_access()
        if values.get('valid_receipt'):
            self._send_validate_mail()
        return super(ResPartner, self).write(values)

    @api.multi
    def _send_mail_to_new_validate_user(self):
        """
        This function sends an email to the new validated user of the portal.
        """
        self.ensure_one()
        account_invoice = invoices = self.env['account.invoice']
        dom = [
            ('partner_id', '=', self.id),
            ('state', '=', 'draft')
        ]
        invoices |= account_invoice.search(
            dom, order='date_invoice asc', limit=1
        )
        if not invoices:
            invoices |= self._create_partner_invoice()
        invoices._send_payment_terms_mail()

    def _create_partner_invoice(self):
        self.ensure_one()
        partner = self
        account_invoice = self.env['account.invoice']
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
        invoice = account_invoice.new(values)
        invoice._onchange_partner_id()
        invoice = account_invoice.create(values)
        invoice.action_invoice_open()
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

    @api.multi
    def _grant_portal_access(self):
        context = {'active_ids': self.ids}
        PortalWizard = self.env['portal.wizard'].with_context(context)
        portal_wizard = PortalWizard.create({'welcome_message': False})
        return portal_wizard.action_apply()

    def _send_validate_mail(self):
        self.ensure_one()
        partner = self
        module_name = 'partner_portal_extra_details'
        template = self.env.ref(
            "%s.email_template_send_user_valid_receipt" % module_name
        )
        template.send_mail(partner.id, force_send=True)

    @api.model
    def compute_player_category(self):
        self.search([])._compute_player_category()

    @api.multi
    @api.depends('gender', 'birthdate_date')
    def _compute_player_category(self):
        for partner in self:
            if partner.gender and partner.birthdate_date:
                partner._set_player_category()

    @api.multi
    def _set_player_category(self):
        self.ensure_one()
        player_category = _('OTHERS')
        if self.gender != 'other':
            partner_age = self._get_partner_age()
            player_category = self._get_player_category_by_age(partner_age)
            if player_category:
                player_category = '%s (%s)' % (
                    player_category,
                    self.gender == 'male' and _('MALE') or _('FEMALE'),
                )
        self.player_category = player_category

    @api.multi
    def _get_partner_age(self):
        self.ensure_one()
        current_year = fields.Date.today().year
        birth_date_year = fields.Date.to_date(self.birthdate_date).year
        return current_year - birth_date_year

    @api.multi
    def _get_player_category_by_age(self, age):
        self.ensure_one()
        for age_range, player_category in CATEGORY_BY_AGE.items():
            if age in age_range:
                return player_category
