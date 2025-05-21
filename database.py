import sqlite3
import bcrypt
import hashlib
import os

def create_database():
    conn = sqlite3.connect('fleet_management.db')
    cursor = conn.cursor()

    # Kullanıcılar tablosu
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        company_name TEXT,
        full_name TEXT,
        phone TEXT
    )
    ''')

    # Sürücüler tablosu
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS drivers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        phone TEXT,
        license_no TEXT,
        user_id INTEGER NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')

    # Kamyonlar tablosu
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS trucks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        plate_number TEXT UNIQUE NOT NULL,
        driver_id INTEGER NOT NULL,
        load_weight REAL,
        user_id INTEGER NOT NULL,
        FOREIGN KEY (driver_id) REFERENCES drivers (id),
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')

    # Seferler tablosu
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS trips (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        truck_id INTEGER NOT NULL,
        destination TEXT NOT NULL,
        start_date TEXT NOT NULL,
        status TEXT NOT NULL,
        route_data TEXT,
        user_id INTEGER NOT NULL,
        FOREIGN KEY (truck_id) REFERENCES trucks (id),
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')

    # Mevcut veritabanında route_data sütunu yoksa ekleyelim
    cursor.execute('''
    SELECT COUNT(*) FROM sqlite_master 
    WHERE type='table' AND name='trips' AND 
    sql LIKE '%route_data%'
    ''')
    
    if cursor.fetchone()[0] == 0:
        cursor.execute('''
        ALTER TABLE trips ADD COLUMN route_data TEXT
        ''')

    conn.commit()
    conn.close()

def hash_password(password):
    """Şifreyi hashler ve salt ekler"""
    salt = os.urandom(32)  # 32 byte rastgele salt
    key = hashlib.pbkdf2_hmac(
        'sha256',  # Hash algoritması
        password.encode('utf-8'),  # Şifreyi byte'a çevir
        salt,  # Salt ekle
        100000  # İterasyon sayısı
    )
    # Salt ve key'i birleştir ve hex'e çevir
    return (salt + key).hex()

def verify_password(password, stored_password):
    """Şifreyi doğrular"""
    try:
        # Önce normal şifre kontrolü yap
        if password == stored_password:
            return True
            
        # Hex formatındaki şifre kontrolü
        stored_password = bytes.fromhex(stored_password)
        salt = stored_password[:32]  # İlk 32 byte salt
        key = stored_password[32:]  # Geri kalanı hash
        new_key = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt,
            100000
        )
        return key == new_key
    except Exception as e:
        print(f"Şifre doğrulama hatası: {str(e)}")
        return False

if __name__ == '__main__':
    create_database() 