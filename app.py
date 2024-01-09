from flask import Flask, request, jsonify, send_file, render_template, url_for, redirect, Response
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from io import BytesIO
from datetime import datetime
import pprint
import json

# Import Portfolio classes
from portfolioClass import Portfolio, MasterPortfolio
from portfolioManager import PortfolioManager

pm = PortfolioManager()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db' 
db = SQLAlchemy(app)

ALLOWED_EXTENSIONS = {'csv'}

# Method provided from Flask docummentations
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Models for SQLite Database
class Upload(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(50))
    data = db.Column(db.LargeBinary)

class ApiKey(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    service = db.Column(db.String(50), nullable=False)  # 'Coinbase', 'Gemini', etc.
    api_key = db.Column(db.String(200), nullable=False)
    api_secret = db.Column(db.String(200), nullable=False)

# Post Coinbase Keys
@app.route('/api/coinbase/keys', methods=['POST'])
def set_coinbase_keys():
    data = request.get_json()
    print(data)

    # Check if data is None or if 'api_key' and 'api_secret' are present in the data
    if data is None or 'api_key' not in data or 'api_secret' not in data:
        return jsonify({'error': 'Invalid request format. Please provide "api_key" and "api_secret" in the request body.'}), 400

    key = data['api_key']
    secret = data['api_secret']

    coinbase_keys = ApiKey.query.filter_by(service='Coinbase').first()

    if coinbase_keys:
        coinbase_keys.api_key = key
        coinbase_keys.api_secret = secret
    else:
        new_coinbase_keys = ApiKey(service='Coinbase', api_key=key, api_secret=secret)
        db.session.add(new_coinbase_keys)
    db.session.commit()

    pm.initCoinbase(key, secret)
    return jsonify({'message':'Coinbase keys updated successfully'}), 201

# Post Gemini Keys
@app.route('/api/gemini/keys', methods=['POST'])
def set_gemini_keys():
    data = request.get_json()

    # Check if data is None or if 'api_key' and 'api_secret' are present in the data
    if data is None or 'api_key' not in data or 'api_secret' not in data:
        return jsonify({'error': 'Invalid request format. Please provide "api_key" and "api_secret" in the request body.'}), 400
    
    key = data['api_key']
    secret = data['api_secret']

    gemini_keys = ApiKey.query.filter_by(service='Gemini').first()

    if gemini_keys:
        gemini_keys.api_key = key
        gemini_keys.api_secret = secret
    else:
        new_gemini_keys = ApiKey(service='Gemini',api_key=key, api_secret=secret)
        db.session.add(new_gemini_keys)
    db.session.commit()

    pm.initGemini(key, secret)
    return jsonify({'message':'Gemini keys updated successfully'}), 201

# Post Ledger CSV Data
@app.route('/api/ledger/upload-csv', methods=['POST', 'GET'])
def upload_ledger_csv():
    if request.method == 'POST':
        # Check if the POST request has a file part
        if 'file' not in request.files:
            return {'error': 'No file part'}, 400

        file = request.files['file']

        # Check if the file is empty
        if file.filename == '':
            return {'error': 'No selected file'}, 400
        
        # Check if the file is an Excel file
        if not file.filename.endswith('.csv'):
            return {'error': 'Invalid file format. Please upload a CSV file (.csv)'}, 400
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)

            existing_upload = Upload.query.first()

            if existing_upload:
                existing_upload.filename = filename
                existing_upload.data = file.read()
            else:
                upload = Upload(filename = filename, data = file.read())
                db.session.add(upload)
            db.session.commit()

            upload = Upload.query.order_by(Upload.id.desc()).first()
            if upload is None:
                return jsonify({'error': 'No ledger file found'}), 404
            file_data = BytesIO(upload.data)

            pm.initLedger(file_data)
            return redirect(url_for('download_page'))
        
        return 'Upload failed.'
    
    return render_template('upload.html')

@app.route('/download', methods=['GET'])
def download_page():
    return render_template('download.html')

# Return Coinbase Loaded JSON
@app.route('/api/coinbase/json', methods=['GET'])
def coinbase_json():
    if type(pm.coinbase) == Portfolio:
        pm.coinbase.loadData()
        data = pm.coinbase.portfolio
        response = Response(json.dumps(data, sort_keys=False), mimetype='application/json')
        return response, 202
    
    return jsonify({'message':'Error returning Coinbase portfolio json...'}), 404

# Return Coinbase Total Balance
@app.route('/api/coinbase/total-balance', methods=['GET'])
def coinbase_total_balance():
    if type(pm.coinbase) == Portfolio:
        pm.coinbase.loadData()
        return jsonify({'balance':pm.coinbase.totalBalance()}), 202

    return jsonify({'message':'Error returning Coinbase balance...'}), 404

# Return Gemini Loaded JSON
@app.route('/api/gemini/json', methods=['GET'])
def gemini_json():
    if type(pm.gemini) == Portfolio:
        pm.gemini.loadData()
        data = pm.gemini.portfolio
        response = Response(json.dumps(data, sort_keys=False), mimetype='application/json')
        return response, 202
    
    return jsonify({'message':'Error returning Gemini portfolio json...'}), 404

# Return Gemini Total Balance
@app.route('/api/gemini/total-balance', methods=['GET'])
def gemini_total_balance():
    if type(pm.gemini) == Portfolio:
        pm.gemini.loadData()
        return jsonify({'balance':pm.gemini.totalBalance()}), 202

    return jsonify({'message':'Error returning Gemini balance...'}), 404

# Return Ledger Loaded JSON
@app.route('/api/ledger/json', methods=['GET'])
def ledger_json():
    if type(pm.ledger) == Portfolio:
        pm.ledger.loadData()
        data = pm.ledger.portfolio
        response = Response(json.dumps(data, sort_keys=False), mimetype='application/json')
        return response, 202
    
    return jsonify({'message':'Error returning Ledger portfolio json...'}), 404

# Return Ledger Total Balance
@app.route('/api/ledger/total-balance', methods=['GET'])
def ledger_total_balance():
    if type(pm.ledger) == Portfolio:
        pm.ledger.loadData()
        return jsonify({'balance':pm.ledger.totalBalance()}), 202
    
    return jsonify({'message':'Error returning Ledger balance...'}), 404

# Return Master Loaded JSON (w/ all assets)
@app.route('/api/master/json', methods = ['GET'])
def master_json():
    pm.initMaster()

    if type(pm.master) == MasterPortfolio:
        pm.master.loadData()
        data = pm.master.portfolio
        response = Response(json.dumps(data, sort_keys=False), mimetype='application/json')
        return response, 202
    
    return jsonify({'message':'Error returning Master portfolio json...'}), 404
    
# Return Total Balance of All Assets
@app.route('/api/master/total-balance', methods=['GET'])
def master_total_balance():
    pm.initMaster()

    if type(pm.master) == MasterPortfolio:
        pm.master.loadData()
        return jsonify({'balance':pm.master.totalBalance()}), 202

    return jsonify({'message':'Error returning Master balance...'}), 404

# Export Master xlsx of All Assets
@app.route('/api/master/download-xlsx', methods = ['GET'])
def download_master_xlsx():
    pm.initMaster()
    pm.master.loadData()

    excel_file = pm.master.pandasToExcel_api()

    current_time = datetime.now().strftime("%m-%d-%Y %H:%M")
    fileName = f'master_portfolio_{current_time}.xlsx'

    return send_file(excel_file, 
                     as_attachment=True, 
                     download_name=fileName,
                     mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)