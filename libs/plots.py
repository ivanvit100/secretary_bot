import matplotlib.pyplot as plt # type: ignore
import numpy as np # type: ignore
import logging
import os

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
        plt.plot(months, balances, label='Balance', marker='o')
        plt.plot(months, saldos, label='Saldo', marker='o')
        plt.xlabel('Month')
        plt.ylabel('Amount')
        plt.title('Balance and Saldo by Month')
        plt.legend()
        plt.grid(True)
        plt.xticks(rotation=25)

        plt.savefig('balance_plot.png')
        plt.close()
        logging.info("Balance plot saved as balance_plot.png")
    except Exception as e:
        logging.error(f"Error in plot_balance: {e}")
        raise

def plot_income_expenses(data: dict):
    try:
        income = sum(data.get('income', []))
        expenses = sum(data.get('expenses', []))
        labels = ['Income', 'Expenses']
        sizes = [income, expenses]

        if sum(sizes) == 0:
            logging.warning("Both income and expenses are zero. Skipping pie chart generation.")
            return

        plt.figure(figsize=(8, 8))
        plt.pie(sizes, labels=labels, wedgeprops=dict(width=0.5), 
                autopct='%1.1f%%', startangle=90, 
                textprops={'fontsize': 14, 'fontweight': 'bold', 'color': '#242424'}) 
        plt.axis('equal')

        plt.savefig('income_expenses_plot.png')
        plt.close()
        logging.info("Income and expenses plot saved as income_expenses_plot.png")
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

        ax.bar(x - width / 2, incomes, width, label='incomes')
        ax.bar(x + width / 2, expenses, width, label='expenses')

        ax.set_title('Mounth stats')
        ax.set_xticks(x)
        ax.set_xticklabels(days)
        ax.legend()
        ax.grid(True)

        plt.savefig('mounth_plot.png')
        plt.close()
        logging.info("Balance plot saved as mounth_plot.png")
    except Exception as e:
        logging.error(f"Error in mounth_plot: {e}")
        raise