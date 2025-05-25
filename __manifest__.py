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
        'views/declaration_views.xml',
        'views/add_declarations_popup_wizard.xml',
        'views/currency_views_inherit.xml',
        'views/employee_views_inherit.xml',
        'views/declarations_notes_line.xml',
        'views/declaration_line.xml',
        'views/declaration_type_views.xml',
        'views/transaction_type_views.xml'
    ],
    'license': 'LGPL-3',
}