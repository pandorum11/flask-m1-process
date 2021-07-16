from flask import Flask, render_template, request, redirect

from cloudipsp import Api, Checkout
from flask_sqlalchemy import SQLAlchemy
from piastrixlib import PiastrixClient


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shop.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

secret_key = 'YourSecretKey'
shop_id = 'YourShopID'

piastrix = PiastrixClient(shop_id, secret_key)


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

    api = Api(merchant_id=1396424,
        secret_key='test')
    checkout = Checkout(api=api)
    data = {
        "currency": "RUB",
        "amount": str(item.price) + "00"
    }
    url = checkout.url(data).get('checkout_url')
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