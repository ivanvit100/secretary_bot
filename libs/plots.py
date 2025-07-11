import matplotlib.pyplot as plt
import numpy as np
import logging
import os
from i18n import _

plt.switch_backend('Agg')
current_dir = os.path.dirname(os.path.abspath(__file__))

def plot_balance(data: dict):
    try:     
        months = list(data['year'].keys())
        balances = [data['year'][month].get('balance', 0) for month in months]
        saldos = [data['year'][month].get('saldo', 0) for month in months]

        balances = np.nan_to_num(balances)
        saldos = np.nan_to_num(saldos)
        
        if len(balances) > 0 and len(saldos) > 0:
            min_saldo = np.min(saldos)
            max_balance = np.max(balances)
            separate_graphs = (max_balance - min_saldo) > 100000
        else:
            separate_graphs = False
        
        if separate_graphs:
            plt.figure(figsize=(10, 5))
            plt.plot(months, balances, label=_('plot_balance_label'), marker='o', color='blue')
            plt.xlabel(_('plot_month_label'))
            plt.ylabel(_('plot_amount_label'))
            plt.title(_('plot_balance_title_only'))
            plt.grid(True)
            plt.xticks(rotation=25)
            plt.tight_layout()
            plt.savefig('balance_plot.png')
            plt.close()
            
            plt.figure(figsize=(10, 5))
            plt.plot(months, saldos, label=_('plot_saldo_label'), marker='o', color='green')
            plt.xlabel(_('plot_month_label'))
            plt.ylabel(_('plot_amount_label'))
            plt.title(_('plot_saldo_title_only'))
            plt.grid(True)
            plt.xticks(rotation=25)
            plt.tight_layout()
            plt.savefig('saldo_plot.png')
            plt.close()
            
            logging.info(_("plot_separate_balance_saldo_saved"))
        else:
            plt.figure(figsize=(10, 5))
            plt.plot(months, balances, label=_('plot_balance_label'), marker='o')
            plt.plot(months, saldos, label=_('plot_saldo_label'), marker='o')
            plt.xlabel(_('plot_month_label'))
            plt.ylabel(_('plot_amount_label'))
            plt.title(_('plot_balance_title'))
            plt.legend()
            plt.grid(True)
            plt.xticks(rotation=25)
            plt.tight_layout()
            plt.savefig('balance_plot.png')
            plt.close()
            logging.info(_("plot_balance_saved"))
        
        return separate_graphs
        
    except Exception as e:
        logging.error(f"Error in plot_balance: {e}")
        return False

def plot_income_expenses(data: dict):
    try:
        income = data.get('income', [])
        expenses = data.get('expenses', [])

        if not isinstance(income, list) or not isinstance(expenses, list):
            logging.warning(_("plot_invalid_data"))
            return

        income_sum = sum(income)
        expenses_sum = sum(expenses)
        labels = [_('plot_income_label'), _('plot_expenses_label')]
        sizes = [income_sum, expenses_sum]

        if income_sum == 0 and expenses_sum == 0:
            logging.warning(_("plot_zero_income_expenses"))
            return

        plt.figure(figsize=(8, 8))
        plt.pie(sizes, labels=labels, wedgeprops=dict(width=0.5), 
                autopct='%1.1f%%', startangle=90, 
                textprops={'fontsize': 14, 'fontweight': 'bold', 'color': '#242424'}) 
        plt.axis('equal')

        plt.savefig('income_expenses_plot.png')
        plt.close()
        logging.info(_("plot_income_saved"))
    except Exception as e:
        logging.error(f"Error in plot_income_expenses: {e}")
        raise

def mounth_plot(data: dict):
    try:     
        incomes = data["income"]
        expenses = data["expenses"]
        days = [i + 1 for i in range(31)]
        width = .45

        x = np.arange(31)
        fig, ax = plt.subplots(figsize=(10, 5))

        ax.bar(x - width / 2, incomes, width, label=_('plot_income_legend'))
        ax.bar(x + width / 2, expenses, width, label=_('plot_expenses_legend'))

        ax.set_title(_('plot_month_stats_title'))
        ax.set_xticks(x)
        ax.set_xticklabels(days)
        ax.legend()
        ax.grid(True)

        plt.savefig('mounth_plot.png')
        plt.close(fig)
        logging.info(_("plot_month_saved"))
    except Exception as e:
        logging.error(f"Error in mounth_plot: {e}")
        raise

def plot_categories(data):
    try:
        months = list(data['year'].keys())
        important = []
        unplanned = []
        optional = []
        uncategorized = []
        
        for month in months:
            if 'categories' in data['year'][month]:
                important.append(data['year'][month]['categories'].get('important', 0))
                unplanned.append(data['year'][month]['categories'].get('unplanned', 0))
                optional.append(data['year'][month]['categories'].get('optional', 0))
                uncategorized.append(data['year'][month]['categories'].get('uncategorized', 0))
            else:
                important.append(0)
                unplanned.append(0)
                optional.append(0)
                uncategorized.append(0)
        
        plt.figure(figsize=(12, 6))
        plt.bar(months, important, label=_('expense_important'))
        plt.bar(months, unplanned, bottom=important, label=_('expense_unplanned'))
        plt.bar(months, optional, bottom=[i+u for i, u in zip(important, unplanned)], label=_('expense_optional'))
        plt.bar(months, uncategorized, 
                bottom=[i+u+o for i, u, o in zip(important, unplanned, optional)], 
                label=_('expense_uncategorized'))
        
        plt.xlabel(_('months'))
        plt.ylabel(_('amount'))
        plt.title(_('expense_categories_chart_title'))
        plt.legend()
        plt.grid(True)
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        plt.savefig('categories_plot.png')
        plt.close()
        
    except Exception as e:
        logging.error(f"Error creating categories plot: {e}")