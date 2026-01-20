{
    'name': 'AFS Financial Statements Report',
    'version': '1.0',
    'summary': 'AFS PDF Report (custom module)',
    'category': 'Accounting',
    'depends': ['account', 'base', ],
    'data': [
        'security/ir.model.access.csv',
        'views/afs_report_views.xml',
        'reports/afs_report.xml',
        'reports/report_action.xml',
        'reports/report_footer.xml',

    ],
    'assets': {
        'web.assets_backend': [
            'afs_financial_statement_report/static/src/css/font.css',
        ],
        'web.assets_frontend': [
            'afs_financial_statement_report/static/src/css/font.css',
        ],
        'web.report_assets_common': [
            'afs_financial_statement_report/static/src/css/report.css',
        ],
    },

    'installable': True,
    'application': True,
}
