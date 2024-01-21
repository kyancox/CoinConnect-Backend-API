from flask import Flask, request, jsonify, send_file, render_template, url_for, redirect, Response, abort, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os
import uuid
from requests.exceptions import JSONDecodeError as RequestsJSONDecodeError
from werkzeug.utils import secure_filename
from io import BytesIO
from datetime import datetime, timedelta
from pprint import pprint
import json

# Import for Coinbase
from cb import coinbasePortfolio
# Import for Gemini
from gemini import geminiPortfolio
# Import for Ledger
from ledger import ledgerPortfolio
# Import Portfolio classes
from portfolioClass import Portfolio, MasterPortfolio

app = Flask(__name__)
CORS(app, supports_credentials=True, origins=['http://127.0.0.1:5500', 'https://coinconnect.netlify.app/'])
#CORS(app, supports_credentials=True)
app.secret_key = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db' 
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=12)
db = SQLAlchemy(app)

ALLOWED_EXTENSIONS = {'csv'}

# Method provided from Flask documentation
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Models for SQLite Database
class Upload(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(50))
    data = db.Column(db.LargeBinary)
    session_id = db.Column(db.String(200), nullable=False)  # Link to the session

class ApiKey(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    service = db.Column(db.String(50), nullable=False)  # 'Coinbase', 'Gemini', etc.
    api_key = db.Column(db.String(200), nullable=False)
    api_secret = db.Column(db.String(200), nullable=False)
    session_id = db.Column(db.String(200), nullable=False)  # Link to the session

class PortfolioDB(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    account = db.Column(db.String(50), nullable=False)
    portfolio_data  = db.Column(db.Text, nullable=False)
    total_balance = db.Column(db.String(100), nullable=False)
    session_id = db.Column(db.String(200), nullable=False)  # Link to the session

class MasterDB(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    portfolio_data  = db.Column(db.Text, nullable=False)
    total_balance = db.Column(db.String(100), nullable=False)
    excel_bytes = db.Column(db.LargeBinary)
    session_id = db.Column(db.String(200), nullable=False)  # Link to the session


with app.app_context():
    db.create_all()


@app.route('/')
def root():
    return 'Flask API for https://github.com/kyancox/CoinConnect-Backend-API'

# Post Coinbase Keys
@app.route('/api/coinbase/keys', methods=['POST'])
def set_coinbase_keys():
    data = request.get_json()
    print(data)

    # Check if data is None or if 'api_key' and 'api_secret' are present in the data
    if data is None or 'api_key' not in data or 'api_secret' not in data:
        return jsonify({'message': 'Invalid request format. Please provide "api_key" and "api_secret" in the request body.'}), 400

    key = data['api_key']
    secret = data['api_secret']


    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())

    session_id = session['session_id']

    print(session_id)

    coinbase_keys = ApiKey.query.filter_by(service='Coinbase', session_id=session['session_id']).first()

    if coinbase_keys:
        coinbase_keys.api_key = key
        coinbase_keys.api_secret = secret
    else:
        new_coinbase_keys = ApiKey(service='Coinbase', api_key=key, api_secret=secret, session_id = session_id )
        db.session.add(new_coinbase_keys)
    db.session.commit()

    return init_coinbase()

def init_coinbase():

    coinbase_keys = ApiKey.query.filter_by(service='Coinbase', session_id=session['session_id']).first()

    if coinbase_keys and coinbase_keys.api_key and coinbase_keys.api_secret:

        key = coinbase_keys.api_key
        secret = coinbase_keys.api_secret
        session_id = session['session_id']

        coinbaseModel = PortfolioDB.query.filter_by(account='Coinbase', session_id=session_id).first()

        try:
            coinbase = coinbasePortfolio(key, secret)
            portfolio_json = json.dumps(coinbase.portfolio, sort_keys=False)

            if coinbaseModel:
                coinbaseModel.account = coinbase.accountName
                coinbaseModel.portfolio_data = portfolio_json
                coinbaseModel.total_balance = coinbase.totalBalance()
            else:
                coinbaseModel = PortfolioDB(account=coinbase.accountName,
                                            portfolio_data = portfolio_json, 
                                            total_balance=coinbase.totalBalance(),
                                            session_id=session_id) 
                db.session.add(coinbaseModel)
            db.session.commit()

            print('Coinbase portfolio initialized successfully')
            return jsonify({'message':'Coinbase keys updated successfully'}), 201
        except RequestsJSONDecodeError:
            #return jsonify({'message':'api_key or api_secret for Coinbase was invalid.'}), 404
            return jsonify({'message':'api_key or api_secret for Coinbase was invalid.'}), 404
        
        # accounts.append(coinbase)
        # print("coinbase account appended to accounts")
    else:
        return jsonify({'message':'api_key or api_secret for Coinbase was not uploaded.'}), 404


# Post Gemini Keys
@app.route('/api/gemini/keys', methods=['POST'])
def set_gemini_keys():
    data = request.get_json()

    # Check if data is None or if 'api_key' and 'api_secret' are present in the data
    if data is None or 'api_key' not in data or 'api_secret' not in data:
        return jsonify({'message': 'Invalid request format. Please provide "api_key" and "api_secret" in the request body.'}), 400
    
    key = data['api_key']
    secret = data['api_secret']

    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())

    session_id = session['session_id']

    gemini_keys = ApiKey.query.filter_by(service='Gemini', session_id=session_id).first()

    if gemini_keys:
        gemini_keys.api_key = key
        gemini_keys.api_secret = secret
    else:
        new_gemini_keys = ApiKey(service='Gemini',api_key=key, api_secret=secret, session_id=session_id)
        db.session.add(new_gemini_keys)
    db.session.commit()

    return init_gemini()

def init_gemini():
    session_id=session['session_id']

    gemini_keys = ApiKey.query.filter_by(service='Gemini',session_id=session_id).first()

    if gemini_keys and gemini_keys.api_key and gemini_keys.api_secret:

        key = gemini_keys.api_key
        secret = gemini_keys.api_secret

        geminiModel = PortfolioDB.query.filter_by(account='Gemini', session_id=session_id).first()

        try:
            gemini = geminiPortfolio(key, secret)
            portfolio_json = json.dumps(gemini.portfolio, sort_keys=False)

            if geminiModel:
                geminiModel.account = gemini.accountName
                geminiModel.portfolio_data = portfolio_json
                geminiModel.total_balance = gemini.totalBalance()
            else:
                geminiModel = PortfolioDB(account=gemini.accountName,
                                          portfolio_data=portfolio_json,
                                          total_balance=gemini.totalBalance(),
                                          session_id=session_id)
                db.session.add(geminiModel)
            db.session.commit()

            print('Gemini portfolio initialized successfully')
            return jsonify({'message':'Gemini keys updated successfully'}), 201
        except Exception:
            #return jsonify({'message':'api_key or api_secret for Gemini was invalid.'}), 404
            return jsonify({'message':'api_key or api_secret for Gemini was invalid.'}), 404
        
        # accounts.append(gemini)
        # print("gemini account appended to accounts")
    else:
        return jsonify({'message':'api_key or api_secret for Coinbase was not uploaded.'}), 404

# Post Ledger CSV Data
@app.route('/api/ledger/upload-csv', methods=['POST', 'GET'])
def upload_ledger_csv():
    if request.method == 'POST':
        # Check if the POST request has a file part
        if 'file' not in request.files:
            return jsonify({'message': 'No file part'}), 400

        file = request.files['file']

        # Check if the file is empty
        if file.filename == '':
            return jsonify({'message': 'No selected file'}), 400
        
        # Check if the file is an Excel file
        if not file.filename.endswith('.csv'):
            print('Invalid file type error reached.')
            return jsonify({'message': 'Invalid file format. Please upload a CSV file (.csv)'}), 400
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)

            if 'session_id' not in session:
                session['session_id'] = str(uuid.uuid4())

            session_id = session['session_id']

            existing_upload = Upload.query.filter_by(session_id=session_id).first()

            if existing_upload:
                existing_upload.filename = filename
                existing_upload.data = file.read()
            else:
                upload = Upload(filename = filename,
                                data = file.read(),
                                session_id=session_id)
                db.session.add(upload)
            db.session.commit()

            # upload = Upload.query.order_by(Upload.id.desc()).first()
            # if upload is None:
            #     return jsonify({'message': 'No ledger file found'}), 404
            # file_data = BytesIO(upload.data)

            return init_ledger()
        
        return jsonify({'message': 'Upload failed.'}), 404
    
    return render_template('upload.html')

@app.route('/download', methods=['GET'])
def download_page():
    return render_template('download.html')

def init_ledger():
    session_id = session['session_id']
    #upload = Upload.query.order_by(Upload.id.desc()).first()
    upload = Upload.query.filter_by(session_id=session_id).first()

    if upload is None:
        return jsonify({'message': 'No ledger file found'}), 404
    
    file_data = BytesIO(upload.data)

    ledgerModel = PortfolioDB.query.filter_by(account='Ledger', session_id=session_id).first()

    try:
        ledger = ledgerPortfolio(file_data)
        portfolio_json = json.dumps(ledger.portfolio, sort_keys=False)

        if ledgerModel:
            ledgerModel.account = ledger.accountName
            ledgerModel.portfolio_data = portfolio_json
            ledgerModel.total_balance = ledger.totalBalance()
        else:
            ledgerModel = PortfolioDB(account=ledger.accountName,
                                      portfolio_data=portfolio_json,
                                      total_balance=ledger.totalBalance(),
                                      session_id=session_id)
            db.session.add(ledgerModel)
        db.session.commit()

        print('Ledger portfolio initialized successfully')
        return jsonify({'message': 'Ledger CSV updated successfully.'}), 201
    except Exception:
        return jsonify({'message': 'CSV file for Ledger was invlaid.'}), 404
    
    # accounts.append(ledger)
    # print("ledger account appended to accounts")

def init_master():

    session_id = session.get('session_id')  # Use .get to avoid KeyError
    if not session_id:
        # Handle the missing session_id appropriately
        return jsonify({'message': 'Session ID not found. Please start a new session.'}), 400
    
    print("init_master session_id:")
    print(session_id)


    coinbaseModel = PortfolioDB.query.filter_by(account='Coinbase', session_id=session_id).first()
    geminiModel = PortfolioDB.query.filter_by(account='Gemini', session_id=session_id).first()
    ledgerModel = PortfolioDB.query.filter_by(account='Ledger', session_id=session_id).first()

    accounts = []
    
    if coinbaseModel:
        portfolio_dict = json.loads(coinbaseModel.portfolio_data)
        coinbase = Portfolio(coinbaseModel.account, portfolio_dict, True)
        accounts.append(coinbase)
    if geminiModel:
        portfolio_dict = json.loads(geminiModel.portfolio_data)
        gemini = Portfolio(geminiModel.account, portfolio_dict, True)
        accounts.append(gemini)
    if ledgerModel:
        portfolio_dict = json.loads(ledgerModel.portfolio_data)
        ledger = Portfolio(ledgerModel.account, portfolio_dict, True)
        accounts.append(ledger)

    print(f'accounts len: {len(accounts)}')

    if len(accounts) == 0:
        return jsonify({'message':'Accounts are invalid...'}), 404

    master = MasterPortfolio(accounts)
    portfolio_json = json.dumps(master.portfolio, sort_keys=False)
    excel_bytes_io = master.pandasToExcel_api()
    #excel_bytes_io.seek(0)

    masterModel = MasterDB.query.filter_by(session_id=session_id).first()

    print('Ledger portfolio initialized successfully')

    if masterModel:
        master.portfolio_data = portfolio_json
        master.total_balance = master.totalBalance()
        master.excel_bytes = excel_bytes_io.read()
    else:
        masterModel = MasterDB(
            portfolio_data=portfolio_json,
            total_balance=master.totalBalance(),
            excel_bytes=excel_bytes_io.read(),
            session_id=session_id
        )
        db.session.add(masterModel)
    db.session.commit()

    print("MASTER PORTFOLIO INITIALIZED")
    

# Return Coinbase Loaded JSON
@app.route('/api/coinbase/json', methods=['GET'])
def coinbase_json():    
    coinbase = PortfolioDB.query.filter_by(account='Coinbase', session_id=session['session_id']).first()

    if coinbase:
        data = coinbase.portfolio_data
        response = Response(data, mimetype='application/json')
        return response, 202
    
    return jsonify({'message':'Error returning Coinbase portfolio.\n\nCoinbase info may not have been uploaded.'}), 404

# Return Coinbase Total Balance
@app.route('/api/coinbase/total-balance', methods=['GET'])
def coinbase_total_balance():
    coinbase = PortfolioDB.query.filter_by(account='Coinbase', session_id=session['session_id']).first()

    if coinbase:
        return jsonify({'balance':coinbase.total_balance}), 202

    return jsonify({'message':'Error returning Coinbase balance.\n\nCoinbase info may not have been uploaded.'}), 404

# Return Gemini Loaded JSON
@app.route('/api/gemini/json', methods=['GET'])
def gemini_json():
    gemini = PortfolioDB.query.filter_by(account='Gemini', session_id=session['session_id']).first()

    if gemini:
        data = gemini.portfolio_data
        response = Response(data, mimetype='application/json')
        return response, 202
    
    return jsonify({'message':'Error returning Gemini portfolio.\n\nGemini info may not have been uploaded.'}), 404

# Return Gemini Total Balance
@app.route('/api/gemini/total-balance', methods=['GET'])
def gemini_total_balance():
    gemini = PortfolioDB.query.filter_by(account='Gemini', session_id=session['session_id']).first()

    if gemini:
        return jsonify({'balance':gemini.total_balance}), 202

    return jsonify({'message':'Error returning Gemini balance.\n\nGemini info may not have been uploaded.'}), 404

# Return Ledger Loaded JSON
@app.route('/api/ledger/json', methods=['GET'])
def ledger_json():
    ledger = PortfolioDB.query.filter_by(account='Ledger', session_id=session['session_id']).first()

    if ledger:
        data = ledger.portfolio_data
        response = Response(data, mimetype='application/json')
        return response, 202
    
    return jsonify({'message':'Error returning Ledger portfolio.\n\nLedger info may not have been uploaded.'}), 404

# Return Ledger Total Balance
@app.route('/api/ledger/total-balance', methods=['GET'])
def ledger_total_balance():
    ledger = PortfolioDB.query.filter_by(account='Ledger', session_id=session['session_id']).first()

    if ledger:
        return jsonify({'balance':ledger.total_balance}), 202
    
    return jsonify({'message':'Error returning Ledger balance.\n\nLedger info may not have been uploaded.'}), 404

# Return Master Loaded JSON (w/ all assets)
@app.route('/api/master/json', methods = ['GET'])
def master_json():
    init_master()

    session_id = session.get('session_id', None)
    if session_id is None:
            return jsonify({'message': 'Session ID is missing.\n\nPlease ensure your session is started and the cookie is sent.'}), 401
    print(session_id)

    master = MasterDB.query.filter_by(session_id=session_id).first()

    if master:
        data = master.portfolio_data
        response = Response(data, mimetype='application/json')
        return response, 202
    
    return jsonify({'message':'Error returning Master portfolio json.'}), 404
    
# Return Total Balance of All Assets
@app.route('/api/master/total-balance', methods=['GET'])
def master_total_balance():
    init_master()

    master = MasterDB.query.filter_by(session_id=session['session_id']).first()

    if master:
        return jsonify({'balance':master.total_balance}), 202

    return jsonify({'message':'Error returning Master balance.'}), 404

# Export Master xlsx of All Assets
@app.route('/api/master/download-xlsx', methods = ['GET'])
def download_master_xlsx():
    init_master()
    master = MasterDB.query.filter_by(session_id=session['session_id']).first()

    excel_file = master.excel_bytes

    if master and master.excel_bytes:

        excel_file = BytesIO(master.excel_bytes)

        current_time = datetime.now().strftime("%m-%d-%Y %H:%M")
        fileName = f'master_portfolio_{current_time}.xlsx'

        return send_file(excel_file, 
                        as_attachment=True, 
                        download_name=fileName,
                        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    
    return jsonify({'message':'No CSV file found'}), 404

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)