from flask import Flask, render_template, request,session,redirect,url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
import hashlib
import time
app = Flask(__name__)
app.secret_key = 'osmancan_hakan'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Users(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.Text, nullable=False)
    pasword = db.Column(db.Integer)
    email = db.Column(db.Text, unique=True, nullable=False)
    authentication = db.Column(db.Integer)
class Categorys(db.Model):
    __tablename__ = "categorys"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.Text, unique=True, nullable=False)
class Products(db.Model):
    __tablename__ = "products"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.Text, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    stock = db.Column(db.Integer, nullable=False)
    popular = db.Column(db.Text)
    image = db.Column(db.Text)
    category_id = db.Column(db.Integer, db.ForeignKey('categorys.id'))
class Orders(db.Model):
    __tablename__ = "orders"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    many = db.Column(db.Text, nullable=False)#adet
    date = db.Column(db.Text,nullable=False)#tarih

db.create_all()
products = Products.query.all()
category = Categorys.query.all()
cartt=[]
@app.route('/')
def index():
    products = Products.query.all()
    return render_template('index.html', products = products)
#kullanıcı giriş çıkış kayıt işlemleri
@app.route("/logout")
def logout():
    session['logged_in'] = False
    session.pop('carts', None)
    session.pop('name', None)
    session.pop('id', None)
    session.pop('authentication', None)
    cartt.clear()
    return redirect(url_for('index'))
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        if 'logged_in' in session:
            if session['logged_in'] == True:
                return redirect(url_for('index'))
            else:
                return render_template('login.html')
        else:
            session['logged_in'] = False
            return render_template('login.html')
    else:
        email = request.form['email']
        sifre = request.form['pw']
        sifrelenmis = hashlib.sha256(sifre.encode("utf8")).hexdigest()
        if Users.query.filter_by(email=email, pasword=sifrelenmis).first():
            veri = Users.query.filter_by(email=email, pasword=sifrelenmis).first()
            session['logged_in'] = True
            session['name'] = veri.username
            session['id'] = veri.id
            session['authentication'] = veri.authentication
            session['carts'] = cartt
            return redirect(url_for('index'))
        else:
            return redirect(url_for('login'))

@app.route('/register', methods = ['POST', 'GET'])
def register():    
    if request.method == 'GET':
        if 'logged_in' in session:
            if session['logged_in'] == True:
                return redirect(url_for('index'))
            else:
                return render_template('register.html')
        else:
            session['logged_in'] = False
            return render_template('register.html')
    else:
        try:
            isim = request.form['name']
            email = request.form['email']
            sifre = request.form['pw']
            sifrelenmis = hashlib.sha256(sifre.encode("utf8")).hexdigest()
            user = Users(username=isim, pasword=sifrelenmis, email=email, authentication='0')
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('index'))
        except:
            return redirect(url_for('register'))
#ürün ekleme işlemleri
@app.route('/stop')
def stop():
    return render_template('stop.html')
@app.route('/add', methods = ['POST', 'GET'])
def add():
    if 'logged_in' in session:
        if (session['logged_in'] == True):
            if request.method == 'GET':
                if (session["authentication"] == 1):
                    category = Categorys.query.all()
                    return render_template('add.html', category=category)
                else:
                    return redirect(url_for('stop'))
            else:
                pname = request.form['pname']
                price = request.form['price']
                pstock = request.form['pstock']
                image = request.form['pimage']
                categor = request.form['categor']
                pro = Products(name=pname, price=price, stock=pstock, popular=0, image=image, category_id=categor)
                db.session.add(pro)
                db.session.commit()
                return redirect(url_for('index'))
        else:
            return redirect(url_for('login'))
    else:
        session['logged_in'] = False
        return redirect(url_for('login'))
@app.route('/update', methods = ['POST', 'GET'])
def update():
    if 'logged_in' in session:
        if (session['logged_in'] == True):
            if request.method == 'GET':
                if (session["authentication"] == 1):
                    category = Categorys.query.all()
                    products = Products.query.all()
                    return render_template('update.html', products=products, category=category);
                else:
                    return redirect(url_for('stop'))
            else:
                pro = Products.query.filter_by(id=request.form['prod']).first()
                pro.name = request.form['pname']
                pro.price = request.form['price']
                pro.stock = request.form['pstock']
                pro.image = request.form['pimage']
                pro.categor = request.form['categor']
                db.session.add(pro)
                db.session.commit()
                return redirect(url_for('update'))
        else:
            return redirect(url_for('login'))
    else:
        session['logged_in'] = False
        return redirect(url_for('login'))
@app.route('/delete', methods = ['POST', 'GET'])
def delete():
    if 'logged_in' in session:
        if (session['logged_in'] == True):
            if request.method == 'GET':
                if (session["authentication"] == 1):
                    products = Products.query.all()
                    return render_template('delete.html', products=products)
                else:
                    return redirect(url_for('dur'))
            else:
                delprod = request.form['prod']
                product = Products.query.filter_by(id=delprod).first()
                db.session.delete(product)
                db.session.commit()
                return redirect(url_for('delete'))
        else:
            return redirect(url_for('login'))
    else:
        session['logged_in'] = False
        return redirect(url_for('login'))

#sepet işlemleri
@app.route('/addcart/<productid>',methods = ['POST','GET'])
def addcart(productid):
    if 'logged_in' in session:
        if (session['logged_in'] == True):
            urun = Products.query.filter_by(id=productid).first()
            durum = False
            cartt = session["carts"] 
            for bul in cartt:
                if str(bul['id']) == str(productid):
                    durum = True
            if cartt == []:
                adet = 1
                toplam = adet * urun.price
                sepeturun = {
                    'id': urun.id,
                    'name': urun.name,
                    'price': urun.price,
                    'image': urun.image,
                    'adet': adet,
                    'toplam': toplam
                }
                cartt.append(sepeturun)
            elif durum == True:
                for bul in cartt:
                    if str(bul['id']) == str(productid):
                        adet = int(bul["adet"])
                        adet += 1
                        fiyat = int(bul['price'])
                        toplam = fiyat * adet
                        bul['adet'] = str(adet)
                        bul['toplam'] = str(toplam)
            else:
                adet = 1
                toplam = adet * urun.price
                sepeturun = {
                    'id': urun.id,
                    'name': urun.name,
                    'price': urun.price,
                    'image': urun.image,
                    'adet': adet,
                    'toplam': toplam
                }
                cartt.append(sepeturun)
            session["carts"] = cartt
            return redirect(url_for('cart'))
        else:
            return redirect(url_for('login'))
    else:
        session['logged_in'] = False
        return redirect(url_for('login'))



@app.route('/deletecart/<productid>',methods = ['POST','GET'])
def deletecart(productid):
    if 'logged_in' in session:
        if (session['logged_in'] == True):
            car = []
            car = session["carts"]
            cartt.clear()
            for silinmeyecek in car:
                if str(silinmeyecek['id']) != str(productid):
                    cartt.append(silinmeyecek)
            session["carts"] = cartt
            return render_template('cart.html', cart=session["carts"])
        else:
            return redirect(url_for('login'))
    else:
        session['logged_in'] = False
        return redirect(url_for('login'))
@app.route('/alldeletecart',methods = ['POST','GET'])
def alldeletecart():
    if 'logged_in' in session:
        if (session['logged_in'] == True):
            cartt.clear()
            session["carts"] = cartt
            return redirect(url_for('cart'))
        else:
            return redirect(url_for('login'))
    else:
        session['logged_in'] = False
        return redirect(url_for('login'))
@app.route('/updateCart/<productid>', methods = ['POST', 'GET'])
def updateCart(productid):
    if 'logged_in' in session:
        if (session['logged_in'] == True):
            if request.method == 'GET':
                return redirect(url_for('index'))
            else:
                adet = int(request.form['adet'])

                cartt=session["carts"]
                for degistir in cartt:
                    if str(degistir['id']) == str(productid):
                        fiyat = int(degistir['price'])
                        toplam = (fiyat * adet)
                        degistir['adet'] = str(adet)
                        degistir['toplam'] = str(toplam)
                session["carts"] = cartt
                return redirect(url_for('cart'))
        else:
            return redirect(url_for('login'))
    else:
        session['logged_in'] = False
        return redirect(url_for('login'))
@app.route('/cart')
def cart():
    if 'logged_in' in session:
        if (session['logged_in'] == True):
            pro = session["carts"]
            return render_template('cart.html', cart=pro)
        else:
            return redirect(url_for('login'))
    else:
        session['logged_in'] = False
        return redirect(url_for('login'))
@app.route('/buy')
def buy():
    if 'logged_in' in session:
        if (session['logged_in'] == True):
            kid = session['id']
            cartt = session["carts"]
            for urun in cartt:
                urun_id = int(urun["id"])
                adet = urun["adet"]
                urunn = Products.query.filter_by(id=urun_id).first()
                eski = int(urunn.popular)
                urunn.popular = str(int(adet) + eski)
                urunn.stock -= int(adet)
                db.session.add(urunn)
                db.session.commit()
                tarih = str(time.strftime("%x") + "-" + time.strftime("%X"))
                order = Orders(user_id=kid, product_id=urun_id, many=adet, date=tarih)
                db.session.add(order)
                db.session.commit()
            cartt.clear()
            session["carts"] = cartt
            return redirect(url_for('cart'))
        else:
            return redirect(url_for('login'))
    else:
        session['logged_in'] = False
        return redirect(url_for('login'))
@app.route('/category')
def category():
    popular = Products.query.order_by(desc(Products.popular))
    catego = Categorys.query.all()
    return render_template('category.html',categor=catego,product=popular)

@app.route('/category/<categoryid>')
def categoryy(categoryid):
    itemData = Products.query.filter_by(category_id=categoryid).order_by(desc(Products.popular))
    catego = Categorys.query.all()
    return render_template('categorysort.html', categor=catego, product=itemData)


@app.route('/order')
def order():
    if 'logged_in' in session:
        if (session['logged_in'] == True):
            kullanici_id = session["id"]
            siparisverilen = Orders.query.filter_by(user_id=kullanici_id)
            veri = []
            for dön in siparisverilen:
                uruncagir = Products.query.filter_by(id=dön.product_id).first()
                siparislerim = {
                    'uismi': str(uruncagir.name),
                    'uresim': str(uruncagir.image),
                    'uadet': dön.many,
                    'starih': dön.date
                }
                veri.append(siparislerim)
            return render_template('orders.html', cart=veri)
        else:
            return redirect(url_for('login'))
    else:
        session['logged_in'] = False
        return redirect(url_for('login'))
if __name__ == '__main__':
    app.run(debug=True)