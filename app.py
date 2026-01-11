from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from pymongo import MongoClient
import requests
import datetime
import os

app = Flask(__name__)
CORS(app)

# Connect to MongoDB
client = MongoClient('mongodb://127.0.0.1:27017/')
db = client['accountBook']
balance_collection = db['balance']
transactions_collection = db['transactions']

# Initialize Balance
if balance_collection.count_documents({}) == 0:
    balance_collection.insert_one({'amount': 0})
    print('Initialized Balance to 0')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/balance', methods=['GET'])
def get_balance():
    try:
        balance = balance_collection.find_one({}, {'_id': 0, 'amount': 1})
        if not balance:
            return jsonify({'amount': 0})
        return jsonify(balance)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/topup', methods=['POST'])
def topup():
    try:
        data = request.json
        amount = float(data.get('amount'))
        reason = data.get('reason')

        # Update Balance
        balance_doc = balance_collection.find_one()
        new_amount = (balance_doc['amount'] if balance_doc else 0) + amount
        
        if balance_doc:
            balance_collection.update_one({'_id': balance_doc['_id']}, {'$set': {'amount': new_amount}})
        else:
            balance_collection.insert_one({'amount': new_amount})

        # Record Transaction
        transaction = {
            'type': 'income',
            'amount': amount,
            'reason': reason,
            'date': datetime.datetime.now()
        }
        transactions_collection.insert_one(transaction)

        return jsonify({'message': 'Top-up successful', 'balance': new_amount})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/expense', methods=['POST'])
def expense():
    try:
        data = request.json
        amount = float(data.get('amount'))
        reason = data.get('reason')

        # Update Balance
        balance_doc = balance_collection.find_one()
        if not balance_doc:
            return jsonify({'error': 'Balance not found'}), 404
            
        new_amount = balance_doc['amount'] - amount
        balance_collection.update_one({'_id': balance_doc['_id']}, {'$set': {'amount': new_amount}})

        # Record Transaction
        transaction = {
            'type': 'expense',
            'amount': amount,
            'reason': reason,
            'date': datetime.datetime.now()
        }
        transactions_collection.insert_one(transaction)

        return jsonify({'message': 'Expense recorded', 'balance': new_amount})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/history', methods=['GET'])
def history():
    try:
        date_str = request.args.get('date')
        if not date_str:
            return jsonify([])

        # Parse date YYYY-MM-DD
        start_date = datetime.datetime.strptime(date_str, '%Y-%m-%d')
        end_date = start_date + datetime.timedelta(days=1)

        transactions = list(transactions_collection.find({
            'date': {'$gte': start_date, '$lt': end_date}
        }).sort('date', -1))

        # Convert ObjectId to str for JSON serialization
        for t in transactions:
            t['_id'] = str(t['_id'])
            t['date'] = t['date'].isoformat()

        return jsonify(transactions)
    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 500

@app.route('/api/monthly_stats', methods=['GET'])
def monthly_stats():
    try:
        year = int(request.args.get('year'))
        month = int(request.args.get('month'))

        start_date = datetime.datetime(year, month, 1)
        if month == 12:
            end_date = datetime.datetime(year + 1, 1, 1)
        else:
            end_date = datetime.datetime(year, month + 1, 1)

        transactions = list(transactions_collection.find({
            'date': {'$gte': start_date, '$lt': end_date}
        }).sort('date', 1))

        income_data = {}
        expense_data = {}
        max_expense = {'amount': 0, 'reason': '', 'date': ''}

        for t in transactions:
            day = t['date'].strftime('%Y-%m-%d')
            amount = t['amount']
            
            if t['type'] == 'income':
                income_data[day] = income_data.get(day, 0) + amount
            elif t['type'] == 'expense':
                expense_data[day] = expense_data.get(day, 0) + amount
                if amount > max_expense['amount']:
                    max_expense = {
                        'amount': amount,
                        'reason': t['reason'],
                        'date': day
                    }

        # Prepare data for charts (fill in all days of the month)
        days_in_month = (end_date - start_date).days
        all_days = [(start_date + datetime.timedelta(days=i)).strftime('%Y-%m-%d') for i in range(days_in_month)]

        today_date = datetime.date.today()
        
        final_income = []
        final_expense = []

        for day_str in all_days:
            day_date = datetime.datetime.strptime(day_str, '%Y-%m-%d').date()
            if day_date > today_date:
                amount = None
            else:
                amount = income_data.get(day_str, 0)
            final_income.append({'date': day_str, 'amount': amount})

        for day_str in all_days:
            day_date = datetime.datetime.strptime(day_str, '%Y-%m-%d').date()
            if day_date > today_date:
                amount = None
            else:
                amount = expense_data.get(day_str, 0)
            final_expense.append({'date': day_str, 'amount': amount})
        
        return jsonify({
            'income': final_income,
            'expense': final_expense,
            'max_expense': max_expense
        })

    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 500

@app.route('/api/rate', methods=['GET'])
def rate():
    try:
        # Using Frankfurter for consistency with history chart
        response = requests.get('https://api.frankfurter.app/latest?from=SGD&to=CNY')
        data = response.json()
        rate = data['rates']['CNY']
        date = data['date']
        
        return jsonify({
            'SGD': 1,
            'CNY': rate,
            'rate': rate,
            'reverseRate': 1/rate,
            'timestamp': date # Frankfurter provides date YYYY-MM-DD
        })
    except Exception as e:
        print(e)
        return jsonify({'error': 'Failed to fetch exchange rate'}), 500

@app.route('/api/rate_history', methods=['GET'])
def rate_history():
    try:
        end_date = datetime.datetime.now()
        start_date = end_date - datetime.timedelta(days=30)
        
        start_str = start_date.strftime('%Y-%m-%d')
        end_str = end_date.strftime('%Y-%m-%d')
        
        # Frankfurter API for historical rates (SGD -> CNY)
        url = f'https://api.frankfurter.app/{start_str}..{end_str}?from=SGD&to=CNY'
        response = requests.get(url)
        data = response.json()
        
        rates = data.get('rates', {})
        # Flatten structure: {'2024-01-01': {'CNY': 5.3}, ...} -> [{'date': '2024-01-01', 'rate': 5.3}, ...]
        history_data = []
        
        # Ensure we have all dates in range
        last_known_rate = None
        
        # Get the first available rate to init last_known_rate if possible, or wait loop
        # We iterate day by day
        num_days = (end_date - start_date).days + 1
        
        for i in range(num_days):
            current_date = start_date + datetime.timedelta(days=i)
            date_str = current_date.strftime('%Y-%m-%d')
            
            if date_str in rates:
                rate_val = rates[date_str]['CNY']
                last_known_rate = rate_val
            else:
                # Use last known rate if available (weekend/holiday)
                rate_val = last_known_rate
                
            if rate_val is not None:
                history_data.append({'date': date_str, 'rate': rate_val})
            
        return jsonify(history_data)
    except Exception as e:
        print(e)
        # Fallback empty list if API fails
        return jsonify([])

if __name__ == '__main__':
    app.run(port=3000, debug=True)
