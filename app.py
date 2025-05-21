from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'gizli_anahtar_buraya'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fleet_management.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Log seviyesini ayarla
import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

db = SQLAlchemy(app)

class Vehicle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    plate = db.Column(db.String(20), nullable=False)
    driver = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(50), default='Aktif')
    last_maintenance = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/vehicles')
def vehicles():
    vehicles = Vehicle.query.all()
    return render_template('vehicles.html', vehicles=vehicles)

def open_browser():
    import webbrowser
    import time
    time.sleep(1)  # Sunucunun başlaması için kısa bir bekleme
    webbrowser.open('http://127.0.0.1:5000')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    # Tarayıcıyı otomatik aç
    import threading
    threading.Thread(target=open_browser).start()
    # Uygulamayı çalıştır
    print("\nUygulama başlatılıyor...")
    print("Tarayıcı otomatik olarak açılıyor...\n")
    app.run(debug=True, use_reloader=False)
