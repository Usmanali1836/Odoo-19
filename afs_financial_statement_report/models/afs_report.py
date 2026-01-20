from odoo import models, api, fields
from dateutil.relativedelta import relativedelta
import logging
_logger = logging.getLogger(__name__)

class AFSReportModel(models.Model):
    _name = 'afs.report'
    _description = 'AFS Report'

    def print_afs_report(self):
        company = self.env.company
        return self.env.ref('afs_financial_statement_report.action_afs_report_header').report_action(company)


class ReportAFSHeader(models.AbstractModel):
    _name = 'report.afs_financial_statement_report.afs_report_header'

    @api.model
    def _get_report_values(self, docids, data=None):
        company = self.env.company

        date_from = fields.Date.from_string('2026-01-01')
        date_to = fields.Date.from_string('2026-12-31')

        prev_date_from = date_from - relativedelta(years=1)
        prev_date_to = date_to - relativedelta(years=1)

        def get_account_balances(prefix, is_balance_sheet=False):
            if is_balance_sheet:
                date_domain_curr = [('date', '<=', date_to)]
                date_domain_prev = [('date', '<=', prev_date_to)]
            else:
                date_domain_curr = [('date', '>=', date_from), ('date', '<=', date_to)]
                date_domain_prev = [('date', '>=', prev_date_from), ('date', '<=', prev_date_to)]

            balances_curr = self.env['account.move.line'].read_group(
                domain=[
                           ('company_id', '=', company.id),
                           ('move_id.state', '=', 'posted'),
                           ('account_id.code', '=like', f'{prefix}%'),
                       ] + date_domain_curr,
                fields=['debit', 'credit', 'account_id'],
                groupby=['account_id'],
            )

            balances_prev = self.env['account.move.line'].read_group(
                domain=[
                           ('company_id', '=', company.id),
                           ('move_id.state', '=', 'posted'),
                           ('account_id.code', '=like', f'{prefix}%'),
                       ] + date_domain_prev,
                fields=['debit', 'credit', 'account_id'],
                groupby=['account_id'],
            )

            curr_dict = {
                l['account_id'][0]: l['credit'] - l['debit']
                for l in balances_curr if (l['credit'] - l['debit']) != 0
            }
            prev_dict = {
                l['account_id'][0]: l['credit'] - l['debit']
                for l in balances_prev if (l['credit'] - l['debit']) != 0
            }

            combined = []
            for acc_id in set(curr_dict) | set(prev_dict):
                account = self.env['account.account'].browse(acc_id)
                combined.append({
                    'code': account.code or '',
                    'name': account.name or '',
                    'balance_curr': curr_dict.get(acc_id, 0.0),
                    'balance_prev': prev_dict.get(acc_id, 0.0),
                })
            return combined

        # ================ P&L ACCOUNTS - YOUR ORIGINAL CODE - NO CHANGES ================
        # Get ALL accounts starting with '4' (Revenue accounts INCLUDING 4103)
        all_4_accounts = get_account_balances('4')

        # Get ALL accounts starting with '5' (Expense accounts INCLUDING 5101)
        all_5_accounts = get_account_balances('5')

        # Now FILTER them into correct categories:

        # 1. Exchange gain accounts (ONLY 4103)
        exchange_gain_accounts = []
        # 2. Revenue accounts (4-series EXCEPT 4103)
        revenue_accounts = []

        for acc in all_4_accounts:
            if acc['code'].startswith('4103'):
                exchange_gain_accounts.append(acc)
            else:
                revenue_accounts.append(acc)

        # 3. Direct cost accounts (ONLY 5101)
        direct_cost_accounts = []
        # 4. Operating expense accounts (5-series EXCEPT 5101)
        expense_accounts = []

        for acc in all_5_accounts:
            if acc['code'].startswith('5101'):
                direct_cost_accounts.append(acc)
            else:
                expense_accounts.append(acc)

        # Calculate totals
        # Revenue total: 4-series accounts EXCEPT 4103
        total_revenue_curr = sum(a['balance_curr'] for a in revenue_accounts)
        total_revenue_prev = sum(a['balance_prev'] for a in revenue_accounts)

        # Exchange gain total: ONLY 4103 accounts
        total_exchange_gain_curr = sum(a['balance_curr'] for a in exchange_gain_accounts)
        total_exchange_gain_prev = sum(a['balance_prev'] for a in exchange_gain_accounts)

        # Direct cost total: ONLY 5101 accounts
        total_direct_cost_curr = sum(a['balance_curr'] for a in direct_cost_accounts)
        total_direct_cost_prev = sum(a['balance_prev'] for a in direct_cost_accounts)

        # Operating expense total: 5-series EXCEPT 5101
        total_expense_curr = sum(a['balance_curr'] for a in expense_accounts)
        total_expense_prev = sum(a['balance_prev'] for a in expense_accounts)

        # Calculate Gross Profit (Revenue - Direct Costs)
        # Note: Direct costs are negative in Odoo, so Revenue - (-Cost) = Revenue + Cost
        # But we want to show Revenue - Cost, so we use abs()
        gross_profit_curr = total_revenue_curr - abs(total_direct_cost_curr)
        gross_profit_prev = total_revenue_prev - abs(total_direct_cost_prev)

        # Calculate Net Profit (Gross Profit - Operating Expenses + Exchange Gain)
        net_profit_curr = gross_profit_curr - abs(total_expense_curr) + total_exchange_gain_curr
        net_profit_prev = gross_profit_prev - abs(total_expense_prev) + total_exchange_gain_prev

        # ================ BALANCE SHEET ACCOUNTS - WITH CALCULATIONS ================
        # Get specific accounts for each section using 2-digit prefixes

        # Fixed Assets (11xx) - Equipment section
        fixed_assets_accounts = get_account_balances('11', is_balance_sheet=True)

        # Current Assets (12xx)
        current_assets_accounts = get_account_balances('12', is_balance_sheet=True)

        # Non-current Liabilities (21xx)
        non_current_liabilities_accounts = get_account_balances('21', is_balance_sheet=True)

        # Current Liabilities (22xx)
        current_liabilities_accounts = get_account_balances('22', is_balance_sheet=True)

        # Equity (31xx)
        equity_accounts = get_account_balances('31', is_balance_sheet=True)

        # ================ CALCULATE SECTION TOTALS ================

        # 1. Calculate Non-current Assets Total (Equipment section: 1101-1109)
        non_current_assets_accounts = []
        non_current_assets_total_curr = 0.0
        non_current_assets_total_prev = 0.0

        for account in fixed_assets_accounts:
            code = account.get('code', '')
            if code.startswith(('1101', '1102', '1103', '1104', '1105', '1106', '1107', '1108', '1109')):
                non_current_assets_accounts.append(account)
                non_current_assets_total_curr += account.get('balance_curr', 0)
                non_current_assets_total_prev += account.get('balance_prev', 0)

        # 2. Calculate Current Assets Total (1201-1205)
        filtered_current_assets = []
        current_assets_total_curr = 0.0
        current_assets_total_prev = 0.0

        for account in current_assets_accounts:
            code = account.get('code', '')
            if code.startswith(('1201', '1202', '1203', '1204', '1205')):
                filtered_current_assets.append(account)
                current_assets_total_curr += account.get('balance_curr', 0)
                current_assets_total_prev += account.get('balance_prev', 0)

        # 3. Calculate Total Assets
        total_assets_curr = non_current_assets_total_curr + current_assets_total_curr
        total_assets_prev = non_current_assets_total_prev + current_assets_total_prev

        # 4. Calculate Equity Total (3101)
        filtered_equity = []
        equity_total_curr = 0.0
        equity_total_prev = 0.0

        for account in equity_accounts:
            code = account.get('code', '')
            if code.startswith('3101'):
                filtered_equity.append(account)
                equity_total_curr += account.get('balance_curr', 0)
                equity_total_prev += account.get('balance_prev', 0)

        # 5. Calculate Non-current Liabilities Total (2101-2104)
        filtered_non_current_liabilities = []
        non_current_liabilities_total_curr = 0.0
        non_current_liabilities_total_prev = 0.0

        for account in non_current_liabilities_accounts:
            code = account.get('code', '')
            if code.startswith(('2101', '2102', '2103', '2104')):
                filtered_non_current_liabilities.append(account)
                # For liabilities, use absolute value to show positive
                non_current_liabilities_total_curr += abs(account.get('balance_curr', 0))
                non_current_liabilities_total_prev += abs(account.get('balance_prev', 0))

        # 6. Calculate Current Liabilities Total (2201-2204)
        filtered_current_liabilities = []
        current_liabilities_total_curr = 0.0
        current_liabilities_total_prev = 0.0

        for account in current_liabilities_accounts:
            code = account.get('code', '')
            if code.startswith(('2201', '2202', '2203', '2204')):
                filtered_current_liabilities.append(account)
                # For liabilities, use absolute value to show positive
                current_liabilities_total_curr += abs(account.get('balance_curr', 0))
                current_liabilities_total_prev += abs(account.get('balance_prev', 0))

        # 7. Calculate Total Equity and Liabilities
        total_liabilities_equity_curr = (
                equity_total_curr +
                non_current_liabilities_total_curr +
                current_liabilities_total_curr
        )
        total_liabilities_equity_prev = (
                equity_total_prev +
                non_current_liabilities_total_prev +
                current_liabilities_total_prev
        )

        return {
            'docs': company,
            'company': company,

            # P&L Data - YOUR ORIGINAL CODE - NO CHANGES
            'revenue_accounts': revenue_accounts,
            'direct_cost_accounts': direct_cost_accounts,
            'expense_accounts': expense_accounts,
            'exchange_gain_accounts': exchange_gain_accounts,
            'total_revenue_curr': total_revenue_curr,
            'total_revenue_prev': total_revenue_prev,
            'total_direct_cost_curr': total_direct_cost_curr,
            'total_direct_cost_prev': total_direct_cost_prev,
            'total_expense_curr': total_expense_curr,
            'total_expense_prev': total_expense_prev,
            'exchange_gain_curr': total_exchange_gain_curr,
            'exchange_gain_prev': total_exchange_gain_prev,
            'gross_profit_curr': gross_profit_curr,
            'gross_profit_prev': gross_profit_prev,
            'net_profit_curr': net_profit_curr,
            'net_profit_prev': net_profit_prev,

            # Balance Sheet Data - Filtered for specific accounts
            'non_current_assets_accounts': non_current_assets_accounts,  # 1101-1109
            'current_assets_accounts': filtered_current_assets,  # 1201-1205
            'equity_accounts': filtered_equity,  # 3101
            'non_current_liabilities_accounts': filtered_non_current_liabilities,  # 2101-2104
            'current_liabilities_accounts': filtered_current_liabilities,  # 2201-2204

            # Balance Sheet Totals (for display in XML)
            'non_current_assets_total_curr': non_current_assets_total_curr,
            'non_current_assets_total_prev': non_current_assets_total_prev,
            'current_assets_total_curr': current_assets_total_curr,
            'current_assets_total_prev': current_assets_total_prev,
            'equity_total_curr': equity_total_curr,
            'equity_total_prev': equity_total_prev,
            'non_current_liabilities_total_curr': non_current_liabilities_total_curr,
            'non_current_liabilities_total_prev': non_current_liabilities_total_prev,
            'current_liabilities_total_curr': current_liabilities_total_curr,
            'current_liabilities_total_prev': current_liabilities_total_prev,
            'total_assets_curr': total_assets_curr,
            'total_assets_prev': total_assets_prev,
            'total_liabilities_equity_curr': total_liabilities_equity_curr,
            'total_liabilities_equity_prev': total_liabilities_equity_prev,

            # Other
            'year_curr': date_to.year,
            'year_prev': prev_date_to.year,
            'currency': company.currency_id,
        }