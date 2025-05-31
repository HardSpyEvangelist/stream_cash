{
    'name': 'Stream Cash App',
    'version': '1.0',
    'category': 'Accounting',
    'summary': 'Cash Management Module',
    'description': '',
    'application': True,
    'installable': True,
    'sequence': 2,
    'depends': ['base', 'account', 'hr'],
    'data': [
        # Security files first - groups before access rights
        'security/access_rights.xml',          # Groups and categories
        'security/ir.model.access.csv',        # Access rights after groups
        
        # Views and other data files
        'views/root_menus.xml',
        'views/stream_cash_declaration_views.xml',
        'views/stream_cash_declarations_popup_wizard_views.xml',
        'views/res_currency_inherit_views.xml',
        'views/res_employee_inherit_views.xml',
        'views/stream_cash_declarations_notes_line.xml',
        'views/stream_cash_declaration_line.xml',
        'views/stream_cash_declaration_type_views.xml',
        'views/stream_cash_transaction_type_views.xml'
    ],
    'license': 'LGPL-3',
}