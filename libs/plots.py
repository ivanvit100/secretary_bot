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

        plt.figure(figsize=(10, 5))
        plt.plot(months, balances, label=_('plot_balance_label'), marker='o')
        plt.plot(months, saldos, label=_('plot_saldo_label'), marker='o')
        plt.xlabel(_('plot_month_label'))
        plt.ylabel(_('plot_amount_label'))
        plt.title(_('plot_balance_title'))
        plt.legend()
        plt.grid(True)
        plt.xticks(rotation=25)

        plt.savefig('balance_plot.png')
        plt.close()
        logging.info(_("plot_balance_saved"))
    except Exception as e:
        logging.error(f"Error in plot_balance: {e}")
        raise

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

        _, ax = plt.subplots(figsize=(10, 5))

        ax.bar(x - width / 2, incomes, width, label=_('plot_income_legend'))
        ax.bar(x + width / 2, expenses, width, label=_('plot_expenses_legend'))

        ax.set_title(_('plot_month_stats_title'))
        ax.set_xticks(x)
        ax.set_xticklabels(days)
        ax.legend()
        ax.grid(True)

        plt.savefig('mounth_plot.png')
        plt.close()
        logging.info(_("plot_month_saved"))
    except Exception as e:
        logging.error(f"Error in mounth_plot: {e}")
        raise