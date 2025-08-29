{
    "name": "Integração WhatsApp (WAHA)",
    "version": "18.0.1.0.0",
    "summary": "Envia pedidos de venda e compra por WhatsApp usando a API do WAHA.",
    "author": "Seu Nome",
    "license": "LGPL-3",
    "category": "Sales",
    "depends": [
        "base_setup",
        "sale_management",
        "purchase",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/res_config_settings_view.xml",
        "views/whatsapp_wizard_views.xml",
        "views/sale_order_views.xml",
        "views/purchase_order_views.xml",
    ],
    "installable": True,
    "application": True,
}