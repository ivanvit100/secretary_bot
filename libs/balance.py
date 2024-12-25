import os
import json
import datetime
import matplotlib.pyplot as plt

current_dir = os.path.dirname(os.path.abspath(__file__))
balance_file_path = os.path.join(current_dir, '../data/balance.json')

def get_balance():
    with open(balance_file_path, 'r') as file:
        data = json.load(file)
    month = datetime.datetime.now().strftime('%B')
    return data.get("year").get(month, {}).get('balance'), data.get("year").get(month, {}).get('saldo')

def get_full_balance():
    with open(balance_file_path, 'r') as file:
        data = json.load(file)
    return data.get("year", {})

def plot_balance(data):
    months = list(data.keys())
    balances = [data[month].get('balance', 0) for month in months]
    saldos = [data[month].get('saldo', 0) for month in months]

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

def update_balance(new_balance):
    with open(balance_file_path, 'r') as file:
        data = json.load(file)
    month = datetime.datetime.now().strftime('%B')
    data['year'][month]['balance'] += new_balance
    data['year'][month]['saldo'] += new_balance
    with open('./data/balance.json', 'w') as file:
        json.dump(data, file, indent=4)