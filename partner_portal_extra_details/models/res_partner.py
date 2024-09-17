# Copyright 2020 Rubén Cabrera Martínez <dev@rubencabrera.es>
# Copyright 2020 CBMP Rayito Salinero
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from datetime import date
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

    current_year_confirmed = fields.Boolean(
        string="Confirmación de alta en la temporada."
    )

    is_player = fields.Boolean(
        string="Es Jugador/a",
        help="Marca esta casilla si este contacto es de un(a) jugador(a)"
    )

    player_category = fields.Char(
        string='Player category',
        compute='_compute_player_category',
        store=True,
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

    @api.model
    def restore_current_year_confirmation(self):
        """
        Restaurar la confirmación de participación del presente año.
        """
        players = self._filter_players()
        _logger.debug("Restaurando temporada para todos los jugadores")
        players.write(
            {
                "attach_receipt": False,
                "current_year_confirmed": False,
                "valid_receipt": False,
            }
        )

    def has_invoice_this_year(self, partner_id):
        account_invoice = invoices = self.env['account.invoice']
        dom = [
            ('partner_id', '=', partner_id),
            (
                'date_invoice',
                '>=',
                date(date.today().year, 1, 1).strftime("%Y-%m-%d")
            )
        ]
        _logger.debug("Domain: %s", dom)
        invoices |= account_invoice.search(
            dom, order='date_invoice asc', limit=1
        )
        return False if not invoices else True

    @api.multi
    def write(self, values):
        for partner in self:
            if (
                values.get("current_year_confirmed") and
                not self.has_invoice_this_year(partner.id)
            ):
                if partner.validate_portal_user:
                    partner._send_mail_to_new_validate_user()
                elif values.get("validate_portal_user"):
                    # Caso algo hipotético de que la confirmación
                    # y la validación se hagan en el mismo momento.
                    partner.is_player = True
                    partner._send_mail_to_new_validate_user()
                    partner._grant_portal_access()

            elif (
                values.get('validate_portal_user') and
                not self.has_invoice_this_year(partner.id)
            ):
                # Usuario nuevo, al que hemos validado manualmente desde
                # administración y al que vamos a mandar el email.
                partner.is_player = True
                partner._grant_portal_access()

                if partner.current_year_confirmed:
                    # Si el jugador ya había confirmado este año antes
                    # de la presente validación.
                    partner._send_mail_to_new_validate_user()

            if values.get('valid_receipt'):
                partner._send_validate_mail()

        return super(ResPartner, self).write(values)

    @api.multi
    def _send_mail_to_new_validate_user(self):
        """
        Envía un correo a un usuario que acaba de ser validado para usar
        el portal. Este correo de bienvenida sólo estaba pensado para
        enviarse una vez, no cada año, pero lo usamos en 2022 como correo
        de inicio de temporada.
        """
        for partner in self:
            if not self.has_invoice_this_year(partner.id):
                invoice = partner._create_partner_invoice()
            invoice._send_payment_terms_mail()

    @api.model
    def _filter_players(self):
        """
        Function to select which partners to send the season start
        email to.
        """
        return self.search(
            [
                '&',
                ('is_player', '=', True),
                ('active', '=', True),
            ]
        )

    @api.model
    def season_start(self):
        """
        Filter and send season start emails.

        Designed to run from a Cronjob.
        """
        players = self._filter_players()
        if players:
            for player in players:
                _logger.debug("Enviando correo a %s", player.name)
                player._send_season_start_email()

    @api.multi
    def _send_season_start_email(self):
        """
        Function to send the season start email using the
        company template.

        Called from records, expects singleton (template does so we
        carry that).
        """
        self.ensure_one()
        # TODO: there's no default set, some error handling should be added
        template = self.company_id.initial_template
        template.send_mail(
            self.id,
            force_send=True  # sends it NOW
        )

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
        """
        Envía un correo de validación. Es el correo de bienvenida de
        cada temporada.
        Inicialmente se invoca desde la función write() cuando se ha
        validado el recibo.
        """
        self.ensure_one()
        partner = self
        module_name = 'partner_portal_extra_details'
        template = self.env.ref(
            "%s.email_template_send_user_valid_receipt" % module_name
        )
        template.send_mail(partner.id)

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
