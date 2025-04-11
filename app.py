import os
import logging
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import uuid
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Database setup
class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///health_verify.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize the app with the extension
db.init_app(app)

# Set up login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Import models after db is defined to avoid circular imports
from models import User, Article, News, Appointment, Subscription

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Import verification module
from verification import verify_health_info

# Import chatbot module
from chatbot import get_chatbot_response

# Create database tables
with app.app_context():
    db.create_all()
    
    # Add some initial data for testing if database is empty
    if Article.query.count() == 0:
        sample_articles = [
            Article(title="Understanding COVID-19 Variants", 
                   content="Information about the latest variants and their implications.", 
                   category="disease", 
                   image_url="https://cdn.pixabay.com/photo/2020/03/16/16/29/virus-4937553_960_720.jpg"),
            Article(title="Diabetes Management Tips", 
                   content="Effective strategies for managing diabetes.", 
                   category="disease", 
                   image_url="https://cdn.pixabay.com/photo/2016/11/14/03/05/surgery-1822458_960_720.jpg"),
            Article(title="Heart Health Guidelines Updated", 
                   content="New recommendations for maintaining cardiac health.", 
                   category="disease", 
                   image_url="https://cdn.pixabay.com/photo/2018/07/06/19/48/ecg-3520427_960_720.jpg")
        ]
        for article in sample_articles:
            db.session.add(article)
        
        sample_news = [
            News(title="New Breakthrough in Alzheimer's Research", 
                 content="Scientists discover potential new treatment approach.", 
                 source="Medical Journal", 
                 published_date=datetime.now(),
                 image_url="https://cdn.pixabay.com/photo/2013/07/13/11/44/stethoscope-158728_960_720.jpg"),
            News(title="Global Health Organization Updates Pandemic Guidelines", 
                 content="New protocols announced for future pandemic responses.", 
                 source="Health Authority", 
                 published_date=datetime.now(),
                 image_url="https://cdn.pixabay.com/photo/2020/11/03/15/32/doctor-5709181_960_720.jpg"),
            News(title="Nutrition Study Reveals Benefits of Mediterranean Diet", 
                 content="Long-term study confirms heart health advantages.", 
                 source="Nutrition Research", 
                 published_date=datetime.now(),
                 image_url="https://cdn.pixabay.com/photo/2017/03/17/10/29/healthy-food-2151383_960_720.jpg")
        ]
        for news in sample_news:
            db.session.add(news)
            
        db.session.commit()

# Routes
@app.route('/')
def index():
    articles = Article.query.filter_by(category='disease').limit(5).all()
    news_items = News.query.order_by(News.published_date.desc()).limit(5).all()
    return render_template('index.html', articles=articles, news_items=news_items)

@app.route('/verify', methods=['POST'])
def verify():
    text = request.form.get('text', '')
    file = request.files.get('file')
    
    # Process the verification - in real app this would be more sophisticated
    result = verify_health_info(text, file)
    
    return jsonify(result)

@app.route('/chatbot', methods=['POST'])
def chatbot():
    message = request.json.get('message', '')
    
    # Get response from chatbot
    response = get_chatbot_response(message)
    
    return jsonify({"response": response})

@app.route('/news')
def news():
    news_items = News.query.order_by(News.published_date.desc()).all()
    return render_template('news.html', news_items=news_items)

@app.route('/consultation')
def consultation():
    return render_template('consultation.html')

@app.route('/book_appointment', methods=['POST'])
@login_required
def book_appointment():
    doctor = request.form.get('doctor')
    date = request.form.get('date')
    time = request.form.get('time')
    symptom = request.form.get('symptom')
    
    appointment = Appointment(
        user_id=current_user.id,
        doctor=doctor,
        date=date,
        time=time,
        symptom=symptom,
        status='pending'
    )
    
    db.session.add(appointment)
    db.session.commit()
    
    flash('Appointment booked successfully!', 'success')
    return redirect(url_for('consultation'))

@app.route('/subscribe', methods=['POST'])
def subscribe():
    email = request.form.get('email')
    
    # Check if email already exists
    existing = Subscription.query.filter_by(email=email).first()
    if existing:
        flash('This email is already subscribed!', 'warning')
    else:
        subscription = Subscription(email=email)
        db.session.add(subscription)
        db.session.commit()
        flash('Thank you for subscribing to our newsletter!', 'success')
    
    return redirect(url_for('index'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid email or password', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Check if email already exists
        user_exists = User.query.filter_by(email=email).first()
        if user_exists:
            flash('Email already in use', 'danger')
            return redirect(url_for('register'))
        
        # Hash password and create user
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, email=email, password_hash=hashed_password)
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Account created successfully! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
