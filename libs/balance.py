import os
import json
import datetime
import numpy as np # type: ignore
import matplotlib.pyplot as plt # type: ignore
from sklearn.linear_model import LinearRegression # type: ignore

current_dir = os.path.dirname(os.path.abspath(__file__))
balance_file_path = os.path.join(current_dir, '../data/balance.json')

plt.switch_backend('Agg')

def update_current_month_balance():
    data = get_full_balance()
    current_month = datetime.datetime.now().strftime('%B')
    previous_month = (datetime.datetime.now() - datetime.timedelta(days=30)).strftime('%B')
    previous_balance = data['year'].get(previous_month, {}).get('balance', 0)
    data['year'][current_month] = {
        'balance': previous_balance,
        'saldo': 0
    }
    with open(balance_file_path, 'w') as file:
        json.dump(data, file, indent=4)
    return previous_balance

def get_balance(month=-1):
    with open(balance_file_path, 'r') as file:
        data = json.load(file)
    if month == -1:
        month = datetime.datetime.now().strftime('%B')
    return round(data['year'].get(month, {}).get('balance', 0), 2), round(data['year'].get(month, {}).get('saldo', 0), 2)

def get_full_balance():
    with open(balance_file_path, 'r') as file:
        data = json.load(file)
    return data

def plot_balance(data):
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

def plot_income_expenses(data):
    income = data.get('income', 0)
    expenses = data.get('expenses', 0)
    labels = ['Income', 'Expenses']
    sizes = [income, expenses]
    colors = ['#ff9999','#66b3ff']
    explode = (0.1, 0)

    sizes = np.nan_to_num(sizes)

    plt.figure(figsize=(8, 8))
    plt.pie(sizes, explode=explode, labels=labels, colors=colors,
            autopct='%1.1f%%', shadow=True, startangle=140)
    plt.axis('equal')

    plt.savefig('income_expenses_plot.png')
    plt.close()

def update_balance(new_balance):
    with open(balance_file_path, 'r') as file:
        data = json.load(file)
    month = datetime.datetime.now().strftime('%B')
    data['year'][month]['balance'] += new_balance
    data['year'][month]['saldo'] += new_balance
    with open(balance_file_path, 'w') as file:
        json.dump(data, file, indent=4)

def forecast_balance_and_saldo(data):
    months = list(data['year'].keys())
    balances = [data['year'][month].get('balance', 0) for month in months]
    saldos = [data['year'][month].get('saldo', 0) for month in months]

    balances = np.nan_to_num(balances)
    saldos = np.nan_to_num(saldos)

    X = np.arange(len(months)).reshape(-1, 1)
    y_balance = np.array(balances)
    y_saldo = np.array(saldos)

    model_balance = LinearRegression()
    model_balance.fit(X, y_balance)
    forecast_balance = model_balance.predict([[len(months)]])[0]

    model_saldo = LinearRegression()
    model_saldo.fit(X, y_saldo)
    forecast_saldo = model_saldo.predict([[len(months)]])[0]

    return forecast_balance, forecast_saldo