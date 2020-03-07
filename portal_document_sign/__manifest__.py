# Copyright 2020 CBMP Rayito Salinero
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Portal document sign",
    "summary": "Allows portal users to view and sign documents",
    'version': '12.0.1.0.0',
    "category": "Customer Relationship Management",
    "website": "https://github.com/rubencabrera/odoo-addons",
    "author": "Rubén Cabrera Martínez",
    "contributors": [
        'Rubén Cabrera Martínez <dev@rubencabrera.es>',
    ],
    "license": "AGPL-3",
    'application': False,
    'installable': True,
    'auto_install': False,
    "depends": [
        "portal",
        "web_widget_digitized_signature",
    ],
    "data": [
        "views/documentbase.xml",
        "views/agreement.xml",
        "views/portal_templates.xml",
        "security/ir.model.access.csv",
    ],
}
