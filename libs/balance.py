import os
import json
import logging
import datetime
import numpy as np # type: ignore
import matplotlib.pyplot as plt # type: ignore
from sklearn.preprocessing import StandardScaler # type: ignore
from sklearn.linear_model import LinearRegression # type: ignore

current_dir = os.path.dirname(os.path.abspath(__file__))
balance_file_path = os.path.join(current_dir, '../data/balance.json')

plt.switch_backend('Agg')

def get_balance(month=-1):
    try:
        with open(balance_file_path, 'r') as file:
            data = json.load(file)
        if month == -1:
            month = datetime.datetime.now().strftime('%B')
        return round(data['year'].get(month, {}).get('balance', 0), 2), round(data['year'].get(month, {}).get('saldo', 0), 2)
    except Exception as e:
        logging.error(f"Error in get_balance: {e}")
        raise

def get_full_balance():
    try:
        with open(balance_file_path, 'r') as file:
            data = json.load(file)
        return data
    except Exception as e:
        logging.error(f"Error in get_full_balance: {e}")
        raise

def plot_balance(data):
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

        plt.savefig('balance_plot.png')
        plt.close()
        logging.info("Balance plot saved as balance_plot.png")
    except Exception as e:
        logging.error(f"Error in plot_balance: {e}")
        raise

def plot_income_expenses(data):
    try:
        income = data.get('income', 0)
        expenses = data.get('expenses', 0)
        labels = ['Income', 'Expenses']
        sizes = [income, expenses]
        colors = ['#ff9999','#66b3ff']
        explode = (0.1, 0)
        sizes = np.nan_to_num(sizes)

        if sum(sizes) == 0:
            logging.warning("Both income and expenses are zero. Skipping pie chart generation.")
            return

        plt.figure(figsize=(8, 8))
        plt.pie(sizes, explode=explode, labels=labels, colors=colors,
                autopct='%1.1f%%', shadow=True, startangle=140)
        plt.axis('equal')

        plt.savefig('income_expenses_plot.png')
        plt.close()
        logging.info("Income and expenses plot saved as income_expenses_plot.png")
    except Exception as e:
        logging.error(f"Error in plot_income_expenses: {e}")
        raise

def update_balance(new_balance):
    try:
        with open(balance_file_path, 'r') as file:
            data = json.load(file)
        month = datetime.datetime.now().strftime('%B')
        data['year'][month]['balance'] += new_balance
        data['year'][month]['saldo'] += new_balance
        data['income'] += new_balance if new_balance > 0 else 0
        data['expenses'] += -new_balance if new_balance < 0 else 0
        with open(balance_file_path, 'w') as file:
            json.dump(data, file, indent=4)
        logging.info("Balance updated")
    except Exception as e:
        logging.error(f"Error in update_balance: {e}")
        raise

def forecast_balance_and_saldo(data):
    try:
        months = list(data['year'].keys())
        balances = [data['year'][month].get('balance', 0) for month in months]
        saldos = [data['year'][month].get('saldo', 0) for month in months]

        balances = np.nan_to_num(balances)
        saldos = np.nan_to_num(saldos)

        X = np.arange(len(months)).reshape(-1, 1)
        y_balance = np.array(balances)
        y_saldo = np.array(saldos)

        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        model_balance = LinearRegression()
        model_balance.fit(X_scaled, y_balance)
        forecast_balance = model_balance.predict(scaler.transform([[len(months)]]))[0]

        model_saldo = LinearRegression()
        model_saldo.fit(X_scaled, y_saldo)
        forecast_saldo = model_saldo.predict(scaler.transform([[len(months)]]))[0]

        return forecast_balance, forecast_saldo
    except Exception as e:
        logging.error(f"Error in forecast_balance_and_saldo: {e}")
        raise