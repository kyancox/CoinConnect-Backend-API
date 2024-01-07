from flask import Flask, request, jsonify, abort, send_file
import pandas as pd
from io import BytesIO

# Import for Coinbase
from cb import coinbasePortfolio

# Import for Gemini
from gemini import geminiPortfolio

from portfolioClass import Portfolio, MasterPortfolio


app = Flask(__name__)

'''
Methods:

POST: API Key
w/ API Key and API Secret

POST: Ledger CSV

GET: Json with Portfolio data 
how to implement this?
we have 4 options
return coinbase data, gemini data, ledger data, or master portfolio data... 


GET: Excel File with Data
https://chat.openai.com/c/9daee5bd-d674-40a5-a31d-dd6929e2ea5f
- send_file() using Flask

GET: total balance
'''

api_keys = {}

# Global variables for exchange Portfolio classes
coinbase = None
gemini = None
ledger = None
master = None
accounts = []

@app.route('/api/coinbase/keys', methods=['POST'])
def set_coinbase_keys():
    data = request.get_json()
    print(data)

    # Check if data is None or if 'api_key' and 'api_secret' are present in the data
    if data is None or 'api_key' not in data or 'api_secret' not in data:
        return jsonify({'error': 'Invalid request format. Please provide "api_key" and "api_secret" in the request body.'}), 400

    api_keys['Coinbase'] = {
        'api_key': data['api_key'],
        'api_secret': data['api_secret']
    }

    print(api_keys)
    init_coinbase()
    return jsonify({'message':'Coinbase keys updated successfully'}), 201

@app.route('/api/gemini/keys', methods=['POST'])
def set_gemini_keys():
    data = request.get_json()

    # Check if data is None or if 'api_key' and 'api_secret' are present in the data
    if data is None or 'api_key' not in data or 'api_secret' not in data:
        return jsonify({'error': 'Invalid request format. Please provide "api_key" and "api_secret" in the request body.'}), 400
    
    api_keys['Gemini'] = {
        'api_key': data['api_key'],
        'api_secret': data['api_secret']
    }

    print(api_keys)
    init_gemini()
    return jsonify({'message':'Gemini keys updated successfully'}), 201

# def upload_ledger_csv():

# Maybe init methods should go in respective POST methods?

def init_coinbase():
    global coinbase

    api_key = api_keys['Coinbase']['api_key']
    api_secret = api_keys['Coinbase']['api_secret']

    try:
        coinbase = coinbasePortfolio(api_key, api_secret)
        print(f"type(coinbase) = {type(coinbase)}")
        print('Coinbase portfolio initialized successfully')
    except Exception:
        return jsonify({'message':'api_key or api_secret for Coinbase was invalid.'}), 404
    
    global accounts
    accounts.append(coinbase)
    print("coinbase account appended to accounts")
    

def init_gemini():
    global gemini

    api_key = api_keys['Gemini']['api_key']
    api_secret = api_keys['Gemini']['api_secret']

    try:
        gemini = geminiPortfolio(api_key, api_secret)
        print('Gemini portfolio initialized successfully')
    except Exception:
        return jsonify({'message':'api_key or api_secret for Gemini was invalid.'}), 404
    
    global accounts
    accounts.append(gemini)
    print("gemini account appended to accounts")

def init_ledger():

    accounts.append(ledger)

    pass

def init_master():
    global master

    if len(accounts) == 0:
        return jsonify({'message':'Accounts are invalid...'}), 404

    master = MasterPortfolio(accounts)

# @app.route('/api/<name>/json', methods=['GET'])
# def account_json(name):
#     exchange = str(name).lower()
#     account = None
#     for n in [coinbase, gemini, ledger]:
#         if exchange == n: account = n
#     if not account:
#         return jsonify({'message':'Acccount not found...'}), 404

#     if type(account) == Portfolio:
#         account.loadData()
#         return jsonify(account.portfolio), 202
    
#     return jsonify({'message':f'Error returning {name} portfolio json...'}), 404

@app.route('/api/coinbase/json', methods=['GET'])
def coinbase_json():
    print(coinbase)
    if type(coinbase) == Portfolio:
        coinbase.loadData()
        return jsonify(coinbase.portfolio), 202
    
    return jsonify({'message':'Error returning Coinbase portfolio json...'}), 404

@app.route('/api/gemini/json', methods=['GET'])
def gemini_json():
    if type(gemini) == Portfolio:
        gemini.loadData()
        return jsonify(gemini.portfolio), 202
    
    return jsonify({'message':'Error returning Gemini portfolio json...'}), 404

@app.route('/api/ledger/xlsx', methods = ['GET'])
def ledger_xlsx():
    pass 

@app.route('/api/master/json', methods = ['GET'])
def master_json():
    #init_master()
    global master
    global accounts

    if len(accounts) == 0:
        return jsonify({'message':'Accounts are invalid...'}), 404
    master = MasterPortfolio(accounts)

    if type(master) == MasterPortfolio:
        master.loadData()
        return jsonify(master.portfolio), 202
    
    return jsonify({'message':'Error returning Master portfolio json...'}), 404

@app.route('/api/total-balance/<name>', methods=['GET'])
def get_total_balance(name):
    exchange = str(name).lower()
    account = None
    for n in [coinbase, gemini, ledger]:
        if exchange == n: account = n
    if not account:
        return jsonify({'message':'Acccount not found...'}), 404
    
    return jsonify({'account':account, 'balance':str(account.get_total_balance())}), 202


'''
Sample code
https://chat.openai.com/c/9daee5bd-d674-40a5-a31d-dd6929e2ea5f
'''

@app.route('/api/ledger/csv', methods=['POST'])
def upload_ledger_csv():
    # Check if the POST request has a file part
    if 'file' not in request.files:
        return {'error': 'No file part'}, 400

    file = request.files['file']

    # Check if the file is empty
    if file.filename == '':
        return {'error': 'No selected file'}, 400

    # Check if the file is an Excel file
    if not file.filename.endswith('.xlsx'):
        return {'error': 'Invalid file format. Please upload an Excel file (.xlsx)'}, 400
    
    return

# Sample DataFrame creation function (replace this with your actual function)
def create_sample_dataframe():
    data = {'Name': ['John', 'Alice', 'Bob'],
            'Age': [28, 24, 22]}
    return pd.DataFrame(data)

@app.route('/api/ledger/export', methods=['GET'])
def export_excel():
    df = create_sample_dataframe()

    # Create a BytesIO buffer to store the file in memory
    excel_buffer = BytesIO()

    # Use pandas to write the DataFrame to the BytesIO buffer as an Excel file
    df.to_excel(excel_buffer, index=False)

    # Seek to the beginning of the buffer
    excel_buffer.seek(0)

    # Send the file as a response to the user
    return send_file(excel_buffer,
                     download_name='exported_data.xlsx',
                     mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')


if __name__ == "__main__":
    app.run(debug=True)