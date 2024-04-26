
from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///restaurant.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'  # Change this to a random string

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)


# Login Manager Configuration
login_manager.login_view = 'login'  # Set the login view for regular users
login_manager.admin_login_view = 'admin_login'  # Set the login view for admin users

# Define User model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

# Modify the MenuItem model to include an image_url attribute
class MenuItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200))
    price = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.String(200))  # Add this line
    

# Update the home route to pass menu items with image URLs to the template
@app.route('/home')
def home():
    menu_items = MenuItem.query.all()
    return render_template('home.html', menu_items=menu_items)

# Define CartItem model
class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    menu_item_id = db.Column(db.Integer, db.ForeignKey('menu_item.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Define routes for login and registration
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('home'))
        else:
            error = 'Invalid username or password'
            return render_template('login.html', error=error)
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            error = 'Username already taken, please choose another one'
            return render_template('register.html', error=error)
        else:
            hashed_password = generate_password_hash(password)
            new_user = User(username=username, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('login'))
    return render_template('register.html')

# Admin dashboard route
@app.route('/admin')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        return redirect(url_for('login'))
    menu_items = MenuItem.query.all()
    return render_template('admin_dashboard.html', menu_items=menu_items)

# Add menu item route
@app.route('/admin/add_menu_item', methods=['GET', 'POST'])
@login_required
def add_menu_item():
    if not current_user.is_admin:
        return redirect(url_for('login'))
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = request.form['price']
        new_item = MenuItem(name=name, description=description, price=price)
        db.session.add(new_item)
        db.session.commit()
        return redirect(url_for('admin_dashboard'))
    return render_template('add_menu_item.html')

# Edit menu item route
@app.route('/admin/edit_menu_item/<int:item_id>', methods=['GET', 'POST'])
@login_required
def edit_menu_item(item_id):
    if not current_user.is_admin:
        return redirect(url_for('login'))
    item = MenuItem.query.get_or_404(item_id)
    if request.method == 'POST':
        item.name = request.form['name']
        item.description = request.form['description']
        item.price = request.form['price']
        db.session.commit()
        return redirect(url_for('admin_dashboard'))
    return render_template('edit_menu_item.html', item=item)

# Delete menu item route
@app.route('/admin/delete_menu_item/<int:item_id>', methods=['POST'])
@login_required
def delete_menu_item(item_id):
    if not current_user.is_admin:
        return redirect(url_for('login'))
    item = MenuItem.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    return redirect(url_for('admin_dashboard'))


# User cart route
@app.route('/cart')
@login_required
def cart():
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    return render_template('cart.html', cart_items=cart_items)


# Admin login route
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        print("Received username:", username)
        print("Received password:", password)
        if username == 'jazim' and password == 'admin123':
            # Redirect to admin dashboard upon successful login
            return redirect(url_for('admin_dashboard'))
        else:
            error = 'Invalid username or password for admin'
            return render_template('admin_login.html', error=error)
    return render_template('admin_login.html')


# Admin home route
@app.route('/admin/home')
@login_required
def admin_home():
    return render_template('admin_home.html')

# Admin logout route
@app.route('/admin/logout')
@login_required
def admin_logout():
    logout_user()
    return redirect(url_for('admin_login'))

if __name__ == "__main__":
    print(app.config['SQLALCHEMY_DATABASE_URI'])

    with app.app_context():
        db.create_all()
    app.run(debug=True, port=8000)

