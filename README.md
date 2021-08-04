# deployed https://flask-m1-process.herokuapp.com


# logging to DB SQLite
# 

# using python-3.9.6
#

FLASK sevise which produse 3 tipes of payment :

PAY		-	https://pay.piastrix.com/ru/pay 			- amount:currency:shop_id:shop_order_idkey

BILL	-	https://core.piastrix.com/bill/create		- payer_currency:amount:shop_currency:shop_id:shop_order_idkey

invoice	-	https://core.piastrix.com/invoice/create	- amount:currency:payway:shop_id:shop_order_idkey

#--------------------------------------------------------------------------------------------------