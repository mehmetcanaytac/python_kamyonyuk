import sqlite3

def veritabani_baglan():
    # SQLite veritabanına bağlan
    conn = sqlite3.connect("kamyonlar.db")  # Veritabanı dosyası
    cursor = conn.cursor()  # Cursor oluştur

    # Tablo oluşturma sorgusu
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS kamyonlar (
            plaka TEXT PRIMARY KEY, 
            surucu TEXT, 
            kapasite REAL, 
            yuk_adi TEXT, 
            yuk_agirlik REAL ''')
    


    conn.commit()  # Değişiklikleri kaydet
    conn.close()  # Bağlantıyı kapat

if __name__ == "__main__":
    tablo_olustur()
    print("Veritabanı ve tablo oluşturuldu.")
