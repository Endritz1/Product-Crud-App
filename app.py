from flask import Flask,render_template,request,flash,redirect,session,url_for
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

import re
app = Flask(__name__)

app.secret_key = "hfkdsafs"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///products.db'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

class User(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(150),nullable=False)
    email = db.Column(db.String(150),unique=True,nullable=False)
    password = db.Column(db.String(150),nullable=False)

    def __init__(self,username,email,password):
        self.username = username
        self.email = email
        self.password = password
    def __repr__(self):
        return "<User %s>" % self.email
    
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    category = db.Column(db.String(150), nullable=False)
    user_id = db.Column(db.Integer(),nullable=False)

    def __init__(self, name, price, category,user_id):
        self.name = name
        self.price = price
        self.category = category
        self.user_id = user_id

    def __repr__(self):
        return "<Product %s>" % self.name
@app.route('/')
def homepage():
   return render_template('homepage.html')
@app.route('/product',methods=['GET','POST'])
def product():
    if 'is_logged_in' in session:      
        products = Product.query.all()         
        if request.method == "POST":
            if not_empty(['name','address','position']):
                name = request.form['name']
                price = request.form['price']
                category = request.form['category']
                products = Product(name,price,category,session.get('user_id'))
                db.session.add(products)
                db.session.commit()
                flash('product was created successfuly')
                return redirect(url_for('product'))
            else:
                flash('All fields required')
        
        return render_template('product.html',products=products)
    else:
        return redirect(url_for('login'))
    return render_template('product.html')


@app.route('/product/<int:product_id>/delete')
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    flash('Product was deleted successfuly!.')
    return redirect(url_for('product'))

@app.route("/edit<int:id>",methods = ['GET','POST'])
def edit_product(id):
    product = Product.query.get_or_404(id)
    if request.method == "POST":
        product.name = request.form['name']
        product.price = request.form['price']
        product.category = request.form['category']
        
        db.session.commit()
        return redirect(url_for('product'))
    
    return render_template('edit.html',product=product)

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']
        if not_empty([email,password]):
            if is_email(email):
                user = User.query.filter_by(email=email).first()
                if user:
                    if bcrypt.check_password_hash(user.password,password):
                        session['is_logged_in']=True
                        session['email'] = email
                        session['user_id'] = user.id
                        session['username'] = user.username

                        return redirect(url_for('product'))
                        
                    else:
                        flash('password is incorrect')

                else:
                    flash('User doesnt exist')
             
            else:
                flash('email is not valid')
        else:
            flash('all fields are required!')
        return redirect(url_for('login'))  
    else:
        if 'is__logged_in' in session:
            return redirect(url_for('product'))   
        return render_template('login.html')

   

@app.route('/register',methods=['GET','POST'])
def register():
    if request.method == "POST":
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        password1 = request.form['confirm_password']
        if not_empty([username,email,password,password1]):
            if is_email(email):
                if password_match(password,password1):
                    password_hash = bcrypt.generate_password_hash(password)
                    user = User(username=username,email=email,password=password_hash)
                    db.session.add(user)
                    db.session.commit()

                    session['is_logged_in']=True
                    session['email'] = email
                    session['username'] = username
                    
                    return redirect(url_for('login'))

                else:
                    flash('password doesnt match')
            else:
                flash('email is not valid')
        else:
            flash('all fields are required!')
        return redirect(url_for('register'))
        

    return render_template('register.html')


@app.route('/logout')
def logout():
    session['username'] = ""
    session['email'] = ""
    session['is_logged_in'] = False
    return redirect(url_for('login'))

def not_empty(form_fields):
    for field in form_fields:
        if len(field) == 0 :
            return False
    return True
        
def is_email(email):
    return re.search("[\w\.\_\-]\@[\w\-]+\.[a-z]{2,5}",email) !=None
def password_match(password,password1):
    return password == password1 




if __name__ == "__main__":
    app.run(debug=True)
