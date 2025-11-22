# -*- coding: utf-8 -*-
{
    'name': "Expédition de colis",
    'sequence': 143,

    'summary': """
        Application de gestion des colis inter urbain
        """,

    'description': """
        Gestionnaire de d'expédition de colis interurbain
    """,

    'author': "ADEO Consulting",
    'website': "http://www.adeo-consulting.cm",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'ADEO',
    'version': '14.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'base_branch', 'mail', 'portal', 'utm', 'stock', 'sale_management'],

    # always loaded
    'data': [
        'data/sequences.xml',
        'security/ir.model.access.csv',
        'views/colis_views.xml',
        'views/partner_views.xml',
        'views/city_views.xml',
        'views/colis_types_views.xml',
        'views/product_template_views.xml',
        'views/location_views.xml',
        'views/colis_travel_views.xml',
        'views/colis_reception_views.xml',
        'views/location_menu_views.xml',
        'views/colis_sms_views.xml',
        'views/colis_client_retrieve_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        #'demo/demo.xml',
    ],
    'installable': True,
    'application': True,
}
