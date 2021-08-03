from flask import Flask, render_template, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from piastrixlib import PiastrixClient
from hashlib import sha256
import requests
from datetime import datetime



secret_key = "SecretKey01"
global_shop_id = "5"

app = Flask(__name__)
app.secret_key = '4632c26d48e9e2fd3069'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shop.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Item(db.Model) :
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(100), nullable=False)
	price = db.Column(db.Integer, nullable=False)
	isActive = db.Column(db.Boolean, default=True)
	# text = db.Column(db.Text, nullable=False)

	def __repr__(self):
		return f"Note : {self.title}"

class LogRecord(db.Model) :
	id = db.Column(db.Integer, primary_key=True)
	currency = db.Column(db.String, default=False, nullable=False)
	amount = db.Column(db.Numeric, nullable=False)
	DATETIME = db.Column(db.DateTime, default=datetime.utcnow)
	description = db.Column(db.Text(300), nullable=False)
	is_valid = db.Column(db.Boolean, default=True)

	def __repr__(self):
		return f"Note : {self.id}"

# ------------ LOG DB -----------------------------------------------------

def log_db_custom_maker(currency, amount, description, is_valid) :
	logvar = LogRecord(currency=currency, amount=amount, DATETIME=datetime.utcnow(),\
					description=description, is_valid=is_valid)
	db.session.add(logvar)
	db.session.commit()
	return

# -------------------------------------------------------------------------

@app.route('/')
def index() :
	items= Item.query.order_by(Item.price).all()
	return render_template('index.html', data=items)

@app.route('/about')
def about() :
	return render_template('about.html')

@app.route('/', methods=['POST'])
def item_buy():

	obj = LogRecord.query.order_by(LogRecord.id.desc()).first()

	url = ''

	if request.method == "POST":

		if float(request.form['amount']) < 10 :
			flash("Minimus amount is 10.00 .")
			return redirect('/')


		shop_order_id = int(obj.id) + 1
		print(shop_order_id)

		if request.form['cash_selector'] == '978' :
			SHAREADY = sha256(("%s:%s:%s:%s%s"\
				%(request.form['amount'], request.form['cash_selector'],\
					global_shop_id, shop_order_id, secret_key)).encode('utf-8')).hexdigest()
			params = {
				'amount' : request.form['amount'],
				'currency' : request.form['cash_selector'],
				'shop_id' : global_shop_id,
				'sign' : SHAREADY,
				'shop_order_id' : shop_order_id,
				"description": request.form['description']
			}

			r = requests.post('https://pay.piastrix.com/ru/pay', params=params)
			log_db_custom_maker(params['currency'],params['amount'],\
					request.form['description'],True)
			url = r.url

		if request.form['cash_selector'] == '840' :

			SHAREADY = sha256(("%s:%s:%s:%s:%s%s"\
			 	%(request.form['cash_selector'],request.form['amount'], request.form['cash_selector'],\
			 		global_shop_id, shop_order_id, secret_key)).encode('utf-8')).hexdigest()

			params = {
				"description": request.form['description'],
				"payer_currency": request.form['cash_selector'],
				"shop_amount": request.form['amount'],
				"shop_currency": request.form['cash_selector'],
				'shop_id' : global_shop_id,
				"shop_order_id": shop_order_id,
				"sign": SHAREADY
			}
		
			r = requests.post('https://core.piastrix.com/bill/create', json=params)
			result_json = r.json()
			if result_json['result'] == True :
				url = result_json['data']['url']
				log_db_custom_maker(params['payer_currency'],params['shop_amount'],\
					request.form['description'],True)
			else :
				log_db_custom_maker(params['payer_currency'],params['shop_amount'],\
					request.form['description'],False)
				return result_json

		if request.form['cash_selector'] == '643' :

			payway = 'advcash_rub'

			SHAREADY = sha256(("%s:%s:%s:%s:%s%s"\
				%(request.form['amount'], request.form['cash_selector'],\
					payway,global_shop_id, shop_order_id, secret_key)).encode('utf-8')).hexdigest()

			params = {
				"currency": request.form['cash_selector'],
				"sign": SHAREADY,
				"payway": payway,
				"amount": request.form['amount'],
				"shop_id" : global_shop_id,
				"shop_order_id": shop_order_id
				}

			r = requests.post('https://core.piastrix.com/invoice/create', json=params)
			result_json = r.json()
			if result_json['result'] == True :
				log_db_custom_maker(params['currency'],params['amount'],\
					request.form['description'],True)
				return render_template("advcash_submit_card.html", json_r=result_json,\
				 descr=request.form['description'])
			else :
				log_db_custom_maker(params['currency'],params['amount'],\
					request.form['description'],False)
				return result_json

	else:
		return redirect('/')
	
	return redirect(url)
    
# @app.route('/create', methods=['POST', 'GET'])
# def create():
# 	if request.method == "POST":
# 		title = request.form['title']
# 		price = request.form['price']
		
# 		item = Item(title=title, price=price)
# 		try:
# 			db.session.add(item)
# 			db.session.commit()
# 			return redirect('/')
# 		except:
# 			return "Получилась ошибка"
# 	else:
# 		return render_template('create.html')

#	html
# <a class="btn btn-online-primary" href="/create">Добавать товар</a>


if __name__ == '__main__':
	app.run(host = '127.0.0.1', debug=True, port = 2828)