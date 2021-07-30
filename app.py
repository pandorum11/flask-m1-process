from flask import Flask, render_template, request, redirect

from cloudipsp import Api, Checkout
from flask_sqlalchemy import SQLAlchemy
from piastrixlib import PiastrixClient


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shop.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)




# piastrix = PiastrixClient(1, "wqewe2e32e2e3")
# БД - Таблицы - Записи
# Таблица :

#       id    title   price   isActive

#       1     Some    100     True

#       2     Some2   200     False

#       3     Some3   40      True


class Item(db.Model) :
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(100), nullable=False)
	price = db.Column(db.Integer, nullable=False)
	isActive = db.Column(db.Boolean, default=True)
	# text = db.Column(db.Text, nullable=False)

	def __repr__(self):
		return f"Note : {self.title}"

@app.route('/')
def index() :
	items= Item.query.order_by(Item.price).all()
	return render_template('index.html', data=items)

@app.route('/about')
def about() :
	return render_template('about.html')

@app.route('/buy/<int:id>')
def item_buy(id):
	item = Item.query.get(id)
	secret_key = 'YourSecretKey'
	shop_id = 'YourShopID'

	api = PiastrixClient(shop_id, secret_key)

	amount = '1000'
	currency = '840'
	payway = 'card_rub'
	shop_order_id = str(id)
	extra_fields = {'description': 'Test description'}
	response = api.invoice(amount, currency, shop_order_id, payway, extra_fields)
	return redirect(response)
    
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