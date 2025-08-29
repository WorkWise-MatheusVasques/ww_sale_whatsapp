{
    "name": "Integração WhatsApp (WAHA)",
    "version": "18.0.3.0.0", # Versão final
    "summary": "Envia pedidos de venda e compra por WhatsApp usando a API do WAHA.",
    "author": "Seu Nome",
    "license": "LGPL-3",
    "category": "Sales",
    "depends": [
        "account", # Dependência ESSENCIAL para relatórios e views
        "sale_management",
        "purchase",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/whatsapp_settings_views.xml", # Novo arquivo de menu
        "views/whatsapp_wizard_views.xml",
        "views/sale_order_views.xml",
        "views/purchase_order_views.xml",
    ],
    "installable": True,
    "application": True,
}