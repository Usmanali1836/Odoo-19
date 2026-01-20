from odoo import models, fields, api

class ResCompany(models.Model):
    _inherit = 'res.company'

    # Free Zone & License
    free_zone = fields.Char(string="Company Free Zone")
    company_license_number = fields.Char(string="Company License Number")
    trade_license_activities = fields.Text(string="Trade License Activities")
    shareholder_ids = fields.Char(string="")
    shareholders_nationalities = fields.Char(string="")

    # Tax Information
    corporate_tax_registration_number = fields.Char(string="Corporate Tax Registration Number")
    vat_registration_number = fields.Char(string="VAT Registration Number")
    corporate_tax_start_date = fields.Date(string="Corporate Tax Start Date")
    corporate_tax_end_date = fields.Date(string="Corporate Tax End Date")

    # Incorporation
    incorporation_date = fields.Date(string="Company Incorporation Date")

    # Regulations
    implementing_regulations_freezone = fields.Text(string="Implementing Regulations for Free Zones")

    company_share = fields.Selection(
        [('paid', 'Paid'), ('unpaid', 'Unpaid')],
        string='Share',
    )


    # Individual Shareholder Fields (1 to 10)
    shareholder_1 = fields.Char(string="Shareholder 1")
    shareholder_2 = fields.Char(string="Shareholder 2")
    shareholder_3 = fields.Char(string="Shareholder 3")
    shareholder_4 = fields.Char(string="Shareholder 4")
    shareholder_5 = fields.Char(string="Shareholder 5")
    shareholder_6 = fields.Char(string="Shareholder 6")
    shareholder_7 = fields.Char(string="Shareholder 7")
    shareholder_8 = fields.Char(string="Shareholder 8")
    shareholder_9 = fields.Char(string="Shareholder 9")
    shareholder_10 = fields.Char(string="Shareholder 10")

    nationality_1 = fields.Char(string="Nationality 1")
    nationality_2 = fields.Char(string="Nationality 2")
    nationality_3 = fields.Char(string="Nationality 3")
    nationality_4 = fields.Char(string="Nationality 4")
    nationality_5 = fields.Char(string="Nationality 5")
    nationality_6 = fields.Char(string="Nationality 6")
    nationality_7 = fields.Char(string="Nationality 7")
    nationality_8 = fields.Char(string="Nationality 8")
    nationality_9 = fields.Char(string="Nationality 9")
    nationality_10 = fields.Char(string="Nationality 10")

    # No. of Shares per Shareholder
    number_of_shares_1 = fields.Integer(string="No. of Shares 1")
    number_of_shares_2 = fields.Integer(string="No. of Shares 2")
    number_of_shares_3 = fields.Integer(string="No. of Shares 3")
    number_of_shares_4 = fields.Integer(string="No. of Shares 4")
    number_of_shares_5 = fields.Integer(string="No. of Shares 5")
    number_of_shares_6 = fields.Integer(string="No. of Shares 6")
    number_of_shares_7 = fields.Integer(string="No. of Shares 7")
    number_of_shares_8 = fields.Integer(string="No. of Shares 8")
    number_of_shares_9 = fields.Integer(string="No. of Shares 9")
    number_of_shares_10 = fields.Integer(string="No. of Shares 10")

    # Share Value per Shareholder
    share_value_1 = fields.Float(string="Share Value 1")
    share_value_2 = fields.Float(string="Share Value 2")
    share_value_3 = fields.Float(string="Share Value 3")
    share_value_4 = fields.Float(string="Share Value 4")
    share_value_5 = fields.Float(string="Share Value 5")
    share_value_6 = fields.Float(string="Share Value 6")
    share_value_7 = fields.Float(string="Share Value 7")
    share_value_8 = fields.Float(string="Share Value 8")
    share_value_9 = fields.Float(string="Share Value 9")
    share_value_10 = fields.Float(string="Share Value 10")

    # Computed Total per Shareholder
    total_share_1 = fields.Float(string="Total Share 1", compute='_compute_total_shares', store=True, readonly=True)
    total_share_2 = fields.Float(string="Total Share 2", compute='_compute_total_shares', store=True, readonly=True)
    total_share_3 = fields.Float(string="Total Share 3", compute='_compute_total_shares', store=True, readonly=True)
    total_share_4 = fields.Float(string="Total Share 4", compute='_compute_total_shares', store=True, readonly=True)
    total_share_5 = fields.Float(string="Total Share 5", compute='_compute_total_shares', store=True, readonly=True)
    total_share_6 = fields.Float(string="Total Share 6", compute='_compute_total_shares', store=True, readonly=True)
    total_share_7 = fields.Float(string="Total Share 7", compute='_compute_total_shares', store=True, readonly=True)
    total_share_8 = fields.Float(string="Total Share 8", compute='_compute_total_shares', store=True, readonly=True)
    total_share_9 = fields.Float(string="Total Share 9", compute='_compute_total_shares', store=True, readonly=True)
    total_share_10 = fields.Float(string="Total Share 10", compute='_compute_total_shares', store=True, readonly=True)

    # Compute individual total shares
    @api.depends(
        'number_of_shares_1', 'share_value_1',
        'number_of_shares_2', 'share_value_2',
        'number_of_shares_3', 'share_value_3',
        'number_of_shares_4', 'share_value_4',
        'number_of_shares_5', 'share_value_5',
        'number_of_shares_6', 'share_value_6',
        'number_of_shares_7', 'share_value_7',
        'number_of_shares_8', 'share_value_8',
        'number_of_shares_9', 'share_value_9',
        'number_of_shares_10', 'share_value_10',
    )
    def _compute_total_shares(self):
        for rec in self:
            for i in range(1, 11):
                shares = rec[f'number_of_shares_{i}'] or 0
                value = rec[f'share_value_{i}'] or 0.0
                rec[f'total_share_{i}'] = shares * value

    # Compute GRAND TOTAL SHARE
    @api.depends(
        'total_share_1', 'total_share_2', 'total_share_3', 'total_share_4',
        'total_share_5', 'total_share_6', 'total_share_7', 'total_share_8',
        'total_share_9', 'total_share_10'
    )
    def _compute_total_share(self):
        for rec in self:
            rec.total_share = sum(rec[f'total_share_{i}'] for i in range(1, 11))

