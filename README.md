# Filo Yönetim Sistemi

Bu masaüstü uygulaması, kamyon filosu yönetimi için geliştirilmiş bir sistemdir.

## Özellikler

- Kullanıcı kayıt ve giriş sistemi
- Kamyon yönetimi (ekleme, silme, güncelleme)
- Sürücü yönetimi (ekleme, silme)
- Kamyon ve sürücü bilgilerinin listelenmesi

## Gereksinimler

- Python 3.6+
- PyQt5
- SQLite3
- bcrypt

## Kurulum

1. Gerekli paketleri yükleyin:
```bash
pip install -r requirements.txt
```

2. Uygulamayı başlatın:
```bash
python login.py
```

## Kullanım

1. İlk kullanımda kayıt olun
2. Giriş yapın
3. Kamyon ve sürücü yönetimi sekmelerini kullanarak işlemlerinizi gerçekleştirin

## Veritabanı Şeması

### Users Tablosu
- id (PRIMARY KEY)
- username (UNIQUE)
- password

### Drivers Tablosu
- id (PRIMARY KEY)
- name
- phone
- license_number (UNIQUE)

### Trucks Tablosu
- id (PRIMARY KEY)
- plate_number (UNIQUE)
- driver_id (FOREIGN KEY)
- status
- load_weight
- arrival_date 
