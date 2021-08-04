from flask import Flask, render_template, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from hashlib import sha256
import requests
from datetime import datetime

# -------------------------------------------------------------------------

app = Flask(__name__)

app.secret_key = '4632c26d48e9e2fd3069'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shop.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# ------------ STORE SECURITY ---------------------------------------------

app.config['SECRET_KEY_FOR_STORE'] = "SecretKey01"
app.config['GLOBAL_SHOP_ID'] = "5"

db = SQLAlchemy(app)

# -------------------------------------------------------------------------

# ------------ 1 TABLE FOR LOG --------------------------------------------

class LogRecord(db.Model) :
	id = db.Column(db.Integer, primary_key=True)
	currency = db.Column(db.String, default=False, nullable=False)
	amount = db.Column(db.Numeric, nullable=False)
	DATETIME = db.Column(db.DateTime, default=datetime.utcnow)
	description = db.Column(db.Text(300), nullable=False)
	is_valid = db.Column(db.Boolean, default=True)

	def __repr__(self):
		return f"Note : {self.id}"

# -------------------------------------------------------------------------

# ------------ LOG ORDER MAKER --------------------------------------------

def log_db_custom_maker(currency, amount, description, is_valid) :
	logvar = LogRecord(
		currency=currency,
		amount=amount,
		DATETIME=datetime.utcnow(),
		description=description,
		is_valid=is_valid
		)

	db.session.add(logvar)
	db.session.commit()

	return

# -------------------------------------------------------------------------

# ------------- generation requests----------------------------------------

def post_pay_for_EUR(amount,currency,shop_id,shop_order_id,description,key) :

	SHAREADY = sha256(("%s:%s:%s:%s%s"\
		%(
			amount,
			currency,
			shop_id,
			shop_order_id,
			key)
		).encode('utf-8')).hexdigest()

	response = requests.post('https://pay.piastrix.com/ru/pay', params=
		{
			'amount' : amount,
			'currency' : currency,
			'shop_id' : shop_id,
			'sign' : SHAREADY,
			'shop_order_id' : shop_order_id,
			"description": description
		})

	log_db_custom_maker(currency,amount,description,True)

	return response.url


def post_pay_for_USD(amount,payer_currency,shop_currency,shop_id,
		shop_order_id,description,key) :

	SHAREADY = sha256(("%s:%s:%s:%s:%s%s"\
		%(
			payer_currency,
			amount,
			shop_currency,
			shop_id,
			shop_order_id,
			key)
		).encode('utf-8')).hexdigest()

	response = requests.post('https://core.piastrix.com/bill/create', json=
		{
			"description": description,
			"payer_currency": payer_currency,
			"shop_amount": amount,
			"shop_currency": shop_currency,
			'shop_id' : shop_id,
			"shop_order_id": shop_order_id,
			"sign": SHAREADY	
		})

	result_json = response.json()

	if result_json['result'] == True :
		log_db_custom_maker(payer_currency,amount,description,True)
		return result_json['data']['url']

	else :
		log_db_custom_maker(payer_currency,amount,description,False)
		flash(result_json)
		return '/'


def invoise_pay_for_ADVcash(amount,currency,shop_id,shop_order_id,
		description,key) :

	payway = 'advcash_rub'

	SHAREADY = sha256(("%s:%s:%s:%s:%s%s"\
		%(
			amount,
			currency,
			payway,
			shop_id, 
			shop_order_id, 
			key)
		).encode('utf-8')).hexdigest()

	response = requests.post('https://core.piastrix.com/invoice/create', json=
		{
		"currency": currency,
		"sign": SHAREADY,
		"payway": payway,
		"amount": amount,
		"shop_id" : shop_id,
		"shop_order_id": shop_order_id
		})

	result_json = response.json()

	if result_json['result'] == True :
		log_db_custom_maker(currency,amount,description,True)
		return "advcash_submit_card.html", result_json, description
	else :
		log_db_custom_maker(currency,amount,description,False)
		flash(result_json)
		return '/'

# -------------------------------------------------------------------------

# ------------- ROUTES BLOCK ----------------------------------------------

@app.route('/')
def index() :
	return render_template('index.html')

@app.route('/', methods=['POST'])
def item_buy():

	objdb = LogRecord.query.order_by(LogRecord.id.desc()).first()

	url = ''

	if request.method == "POST":

		if float(request.form['amount']) < 10 :
			flash("Minimus amount is 10.00 .")
			return redirect('/')

		if float(request.form['amount']) > 100000 :
			flash("Maximum amount is 100000.00 .")
			return redirect('/')

		if float(len(request.form['description'])) > 500 :
			flash("Maximum lenth of description is 500 signs .")
			return redirect('/')

		if objdb != None :
			shop_order_id = int(objdb.id) + 1
		else :
			shop_order_id = 1

		if request.form['cash_selector'] == '978' :

			return redirect(post_pay_for_EUR(
				request.form['amount'],
				request.form['cash_selector'],
				app.config['GLOBAL_SHOP_ID'],
				shop_order_id,
				request.form['description'],
				app.config['SECRET_KEY_FOR_STORE']))

		if request.form['cash_selector'] == '840' :

			return redirect(post_pay_for_USD(
				request.form['amount'],
				request.form['cash_selector'],
				request.form['cash_selector'],
				app.config['GLOBAL_SHOP_ID'],
				shop_order_id,
				request.form['description'],
				app.config['SECRET_KEY_FOR_STORE']))

		if request.form['cash_selector'] == '643' :

			invoise = invoise_pay_for_ADVcash(
				request.form['amount'],
				request.form['cash_selector'],
				app.config['GLOBAL_SHOP_ID'],
				shop_order_id,
				request.form['description'],
				app.config['SECRET_KEY_FOR_STORE'])

			return render_template(invoise[0], json_r = invoise[1], descr = invoise[2])

# -------------------------------------------------------------------------

if __name__ == '__main__':
	app.run(host = '127.0.0.1', debug=False, port = 2828)