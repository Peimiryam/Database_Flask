from flask import Flask, flash
from flask import render_template
from flask import request
from flask import redirect, url_for
#from os import listdir
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///products.sqlite3'
db = SQLAlchemy(app)

app.config["SECRET_KEY"] = "12345678asdfg"

class Products(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(120), unique = True, nullable = False)
    price = db.Column(db.Float, nullable = False)
    warehouse = db.Column(db.Integer, nullable = False, default = 0)

class WarehouseBalance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    balance = db.Column(db.Float, nullable=False, default=0)

class History(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    action = db.Column(db.String(10), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    price = db.Column(db.Float, nullable=False)

with app.app_context():
    db.create_all()

    if not WarehouseBalance.query.first():
        warehouse_balance = WarehouseBalance(balance=0)
        db.session.add(warehouse_balance)
        db.session.commit()

#http://127.0.0.1:5000
@app.route('/')
def main_page():
    return render_template('task.html')
 
#http://127.0.0.1:5000/Purchase
@app.route("/Purchase",methods = ['GET', 'POST'])
def purchase():
    if request.method == "POST":
        productname = request.form.get("productname")
        quantity = float(request.form.get("quantity"))
        price = float(request.form.get("price"))

        product = Products.query.filter_by(name=productname).first()

        if warehouse_balance.balance < price * quantity:
            flash("Not enough funds")
            return render_template('purchase.html')

        #add a new product that doesn't exist
        if not product:

            product = Products(
                name = productname,
                warehouse = quantity,
                price = price,
            )
            db.session.add(product)
        
        #update the balance
            warehouse_balance = WarehouseBalance.query.first()
            warehouse_balance.balance -= price * quantity

        #update history
            history_entry = History(product_id=product.id, action="purchase", quantity=quantity, price=price)
            db.session.add(history_entry)

            db.session.commit()
            flash("Purchase successfully")
            return render_template('purchase.html')

    return render_template('purchase.html')

#http://127.0.0.1:5000/Sale
@app.route("/Sale", methods = ['GET', 'POST'])
def sale():
    if request.method == 'POST':
        saleproductname = request.form.get('saleproductname')
        salequantity = int(request.form.get('salequantity'))
        saleprice = float(request.form.get('saleprice'))

        product = Products.query.filter_by(name=saleproductname).first()
        #if not available:
        if not product:
            flash("Product not found")
            return render_template('sale.html')

        if product.warehouse >= salequantity:
            product.warehouse -= salequantity

            #update balance

            warehouse_balance = WarehouseBalance.query.first()
            warehouse_balance.balance += saleprice * salequantity

            #update history
            history_entry = History(product_id=product.id, action="sale", quantity=salequantity, price=saleprice)
            db.session.add(history_entry)

            db.session.commit()
            flash("Sale successful")
            return render_template('sale.html')
        else:
            flash("Not enough quantity available for sale")
            return render_template('sale.html')
        
    return render_template('sale.html')


#http://127.0.0.1:5000/Balance
@app.route("/Balance", methods = ['GET', 'POST'])
def balance():
    if request.method == 'POST':
        money = float(request.form.get('money'))
        #update balance
        warehouse_balance = WarehouseBalance.query.first()

        warehouse_balance.balance += money

        #history
        action = "add" if money > 0 else "subtract"
        history_entry = History(product_id=None, action=action, quantity=abs(money), price=0)
        db.session.add(history_entry)
        db.session.commit()

        if money > 0:
            flash(f"Added money to warehouse balance")
        elif money < 0:
            flash(f"Subtracted money from warehouse balance")

    return render_template('balance.html')


@app.route("/History", methods = ['GET', 'POST'])
def history():
    if request.method == 'POST':
        from_value = int(request.form.get('from_value'))
        to_value = int(request.form.get('to_value'))

        if from_value and to_value:
            history_entries = History.query.filter_by(product_id=None).order_by(History.id).all()
            selected_entries = history_entries[from_value - 1:to_value]
            return render_template('history.html', history_entries=selected_entries)
        else:
            flash("Both Values required.")
            return render_template('history.html')
        
    return render_template('history.html')


if __name__ == '__main__':
    app.run()