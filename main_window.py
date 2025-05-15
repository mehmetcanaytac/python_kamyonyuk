from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QLineEdit, QPushButton, QTableWidget,
                             QTableWidgetItem, QMessageBox, QTabWidget, QFormLayout,
                             QDateEdit, QComboBox, QHeaderView, QDialog, QSpinBox,
                             QDoubleSpinBox, QCompleter, QFrame, QSizePolicy)
from PyQt5.QtCore import (Qt, QDate, QObject, pyqtSlot, QStringListModel, QSize, 
                         QPropertyAnimation, QEasingCurve, QTimer, QRectF, QPointF, QRegExp)
from PyQt5.QtGui import (QRegExpValidator, QFont, QIcon, QPixmap, QPainter, 
                         QLinearGradient, QColor, QBrush, QPen, QPainterPath)
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineSettings
import sqlite3
import sys
import json
from datetime import datetime
import folium
from PyQt5.QtCore import QUrl
import os
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut

class Bridge(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.route_data = None

    @pyqtSlot(str)
    def saveRouteData(self, data):
        try:
            self.route_data = json.loads(data)
            self.parent().route_window.close()
            QMessageBox.information(self.parent(), "Başarılı", "Rota başarıyla kaydedildi!")
        except json.JSONDecodeError:
            QMessageBox.critical(self.parent(), "Hata", "Geçersiz JSON verisi!")

class MainWindow(QMainWindow):
    def __init__(self, username, user_id):
        super().__init__()
        self.username = username
        self.user_id = user_id
        self.setWindowTitle(f"Filo Yönetim Sistemi - {username}")
        self.setMinimumSize(1000, 700)
        
        # Ana widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Üst çubuk
        header_widget = QWidget()
        header_widget.setFixedHeight(70)  # Sabit yükseklik
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(20, 10, 20, 10)
        header_layout.setSpacing(15)
        
        # Logo butonu için özel widget
        class LogoButton(QWidget):
            def __init__(self, parent=None):
                super().__init__(parent)
                self.setFixedSize(50, 50)
                self.setCursor(Qt.PointingHandCursor)
                
                # Animasyon için timer
                self.pulse_opacity = 0.0
                self.pulse_timer = QTimer(self)
                self.pulse_timer.timeout.connect(self.update_pulse)
                self.pulse_timer.start(50)  # Her 50ms'de bir güncelle
                
            def enterEvent(self, event):
                self.pulse_opacity = 0.7
                self.update()
                
            def leaveEvent(self, event):
                self.pulse_opacity = 0.0
                self.update()
                
            def update_pulse(self):
                if self.pulse_opacity > 0:
                    self.pulse_opacity -= 0.02
                    if self.pulse_opacity < 0:
                        self.pulse_opacity = 0.7
                    self.update()
                
            def mousePressEvent(self, event):
                # Tıklama efekti
                self.pulse_opacity = 1.0
                self.update()
                # Buraya tıklama işlevi eklenebilir
                super().mousePressEvent(event)
                
            def paintEvent(self, event):
                painter = QPainter(self)
                painter.setRenderHint(QPainter.Antialiasing)
                
                # Arkaplan gradyanı
                gradient = QLinearGradient(0, 0, self.width(), self.height())
                gradient.setColorAt(0, QColor(74, 108, 247))  # #4a6cf7
                gradient.setColorAt(1, QColor(37, 65, 178))   # #2541b2
                
                # Logo kutusu
                path = QPainterPath()
                path.addRoundedRect(1, 1, self.width()-2, self.height()-2, 10, 10)
                
                # Gölge efekti
                shadow = QPainterPath()
                shadow.addRoundedRect(0, 0, self.width(), self.height(), 10, 10)
                painter.setPen(Qt.NoPen)
                painter.setBrush(QColor(0, 0, 0, 30))
                painter.drawPath(shadow)
                
                # Ana arkaplan
                painter.setPen(Qt.NoPen)
                painter.setBrush(QBrush(gradient))
                painter.drawPath(path)
                
                # Üst parlaklık efekti
                highlight = QLinearGradient(0, 0, 0, self.height()/2)
                highlight.setColorAt(0, QColor(255, 255, 255, 100))
                highlight.setColorAt(1, QColor(255, 255, 255, 0))
                painter.setBrush(QBrush(highlight))
                painter.drawPath(path)
                
                # Pulse efekti
                if self.pulse_opacity > 0:
                    pulse_pen = QPen(QColor(255, 255, 255, int(100 * self.pulse_opacity)), 2)
                    pulse_pen.setCosmetic(True)
                    painter.setPen(pulse_pen)
                    painter.setBrush(Qt.NoBrush)
                    pulse_rect = QRectF(5, 5, self.width()-10, self.height()-10)
                    painter.drawRoundedRect(pulse_rect, 7, 7)
                
                # Araç ikonu
                font = QFont('Arial', 20)
                painter.setFont(font)
                painter.setPen(Qt.white)
                painter.drawText(self.rect(), Qt.AlignCenter, '🚛')
        
        # Logo butonunu oluştur
        logo_button = LogoButton()
        
        # Header layout ayarları
        header_layout.addWidget(logo_button)
        header_layout.addStretch()
        
        # Kullanıcı bilgisi (ortada)
        user_label = QLabel(f"Hoş Geldiniz, {username}!", alignment=Qt.AlignCenter)
        user_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: 500;
                color: #4a6cf7;
                padding: 8px 25px;
                background: #f0f4ff;
                border-radius: 20px;
                border: 1px solid #d0d9ff;
                margin: 0 auto;
            }
        """)
        
        # Orta kısma yerleştirmek için container
        center_widget = QWidget()
        center_layout = QHBoxLayout(center_widget)
        center_layout.addWidget(user_label)
        center_layout.setContentsMargins(0, 0, 0, 0)
        
        header_layout.addWidget(center_widget, 1)  # 1 stretch faktörü ile genişlet
        
        # Ana layout'a ekle
        layout.addWidget(header_widget)
        
        # Çizgi ekle
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet("color: #eee;")
        layout.addWidget(line)

        # Sekmeler
        self.tabs = QTabWidget()
        self.tabs.addTab(self.create_profile_tab(), "Profil")
        self.tabs.addTab(self.create_trucks_tab(), "Kamyon Yönetimi")
        self.tabs.addTab(self.create_drivers_tab(), "Sürücü Yönetimi")
        self.tabs.addTab(self.create_trips_tab(), "Sefer Yönetimi")
        self.tabs.addTab(self.create_map_tab(), "Harita")
        self.tabs.addTab(self.create_about_tab(), "Hakkında")
        layout.addWidget(self.tabs)

        # Butonlar için yatay düzen
        button_layout = QHBoxLayout()
        
        # Çıkış butonu
        exit_btn = QPushButton("Çıkış")
        exit_btn.clicked.connect(self.exit_application)
        button_layout.addWidget(exit_btn)
        
        layout.addLayout(button_layout)

        # Stil ayarları
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            QTabWidget::pane {
                border: 1px solid #cccccc;
                background: white;
                border-radius: 5px;
            }
            QTabBar::tab {
                background: #e1e1e1;
                padding: 10px 20px;
                margin: 2px;
                border-radius: 4px;
            }
            QTabBar::tab:selected {
                background: #4CAF50;
                color: white;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 8px 15px;
                border: none;
                border-radius: 4px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QLineEdit, QDateEdit, QComboBox {
                padding: 8px;
                border: 1px solid #cccccc;
                border-radius: 4px;
            }
            QTableWidget {
                background-color: white;
                border: 1px solid #cccccc;
                border-radius: 4px;
            }
            QHeaderView::section {
                background-color: #4CAF50;
                color: white;
                padding: 8px;
                border: none;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QTableWidget::item:selected {
                background-color: #e8f5e9;
                color: black;
            }
        """)

    def create_profile_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(20)

        # Başlık
        title_label = QLabel("Profil Bilgileri")
        title_label.setFont(QFont("Arial", 18, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        # Form
        form = QFormLayout()
        form.setSpacing(15)

        # Firma adı
        self.company_name = QLineEdit()
        self.company_name.setPlaceholderText("Firma adınızı girin")
        form.addRow("Firma Adı:", self.company_name)

        # Ad Soyad
        self.full_name = QLineEdit()
        self.full_name.setPlaceholderText("Adınızı ve soyadınızı girin")
        form.addRow("Ad Soyad:", self.full_name)

        # Telefon
        self.phone = QLineEdit()
        self.phone.setPlaceholderText("5xxxxxxxxx")
        phone_validator = QRegExpValidator(QRegExp(r'[0-9]{11}'))
        self.phone.setValidator(phone_validator)
        self.phone.setMaxLength(11)
        form.addRow("Telefon:", self.phone)

        # Butonlar
        btn_layout = QHBoxLayout()
        
        # Ekle butonu
        add_btn = QPushButton("Ekle")
        add_btn.clicked.connect(self.add_profile)
        btn_layout.addWidget(add_btn)
        
        # Düzenle butonu
        edit_btn = QPushButton("Düzenle")
        edit_btn.clicked.connect(self.edit_profile)
        btn_layout.addWidget(edit_btn)
        
        # Sil butonu
        delete_btn = QPushButton("Sil")
        delete_btn.clicked.connect(self.delete_profile)
        btn_layout.addWidget(delete_btn)
        
        btn_layout.addStretch()
        
        # Tablo
        self.profile_table = QTableWidget()
        self.profile_table.setColumnCount(3)
        self.profile_table.setHorizontalHeaderLabels(["Firma Adı", "Ad Soyad", "Telefon"])
        self.profile_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.profile_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.profile_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.profile_table.setSelectionMode(QTableWidget.SingleSelection)
        self.profile_table.cellClicked.connect(self.populate_profile_fields)
        
        # Stil ayarları
        header = self.profile_table.horizontalHeader()
        header.setStyleSheet("QHeaderView::section{background-color: #4CAF50; color: white; padding: 8px;}")
        self.profile_table.verticalHeader().setVisible(False)
        
        layout.addLayout(form)
        layout.addLayout(btn_layout)
        layout.addWidget(self.profile_table)
        
        # Kayıtlı bilgileri yükle
        self.load_profile()
        
        return tab

    def load_profile(self):
        conn = sqlite3.connect('fleet_management.db')
        cursor = conn.cursor()

        try:
            # Kullanıcı tablosunu kontrol et, yoksa oluştur
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    company_name TEXT,
                    full_name TEXT,
                    phone TEXT
                )
            ''')
            
            # Kullanıcı bilgilerini getir
            cursor.execute("""
                SELECT company_name, full_name, phone 
                FROM users 
                WHERE id = ?
            """, (self.user_id,))
            result = cursor.fetchone()

            if result:
                company, full_name, phone = result
                self.company_name.setText(company or "")
                self.full_name.setText(full_name or "")
                self.phone.setText(phone or "")
                
                # Tabloyu güncelle
                self.profile_table.setRowCount(1)
                self.profile_table.setItem(0, 0, QTableWidgetItem(company or "-"))
                self.profile_table.setItem(0, 1, QTableWidgetItem(full_name or "-"))
                self.profile_table.setItem(0, 2, QTableWidgetItem(phone or "-"))
        except sqlite3.Error as e:
            QMessageBox.warning(self, "Hata", f"Profil bilgileri yüklenirken hata oluştu: {str(e)}")
        finally:
            conn.close()

    def add_profile(self):
        company_name = self.company_name.text().strip()
        full_name = self.full_name.text().strip()
        phone = self.phone.text().strip()

        if not all([company_name, full_name, phone]):
            QMessageBox.warning(self, "Hata", "Lütfen tüm alanları doldurun!")
            return
            
        if len(phone) != 11 or not phone.isdigit():
            QMessageBox.warning(self, "Hata", "Lütfen geçerli bir telefon numarası girin (11 hane).")
            self.phone.setFocus()
            return
            
        conn = sqlite3.connect('fleet_management.db')
        cursor = conn.cursor()
        
        try:
            # Kullanıcı bilgilerini güncelle
            cursor.execute("""
                UPDATE users 
                SET company_name = ?, full_name = ?, phone = ?
                WHERE id = ?
            """, (company_name, full_name, phone, self.user_id))
            
            # Eğer güncelleme yapılmadıysa (kayıt yoksa), yeni kayıt ekle
            if cursor.rowcount == 0:
                cursor.execute("""
                    INSERT INTO users (id, username, company_name, full_name, phone)
                    VALUES (?, ?, ?, ?, ?)
                """, (self.user_id, self.username, company_name, full_name, phone))
            
            conn.commit()
            
            # Formu temizle
            self.clear_profile_form()
            
            # Tabloyu güncelle
            self.load_profile()
            
            QMessageBox.information(self, "Başarılı", "Profil bilgileriniz başarıyla eklendi!")
            
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Hata", f"Profil eklenirken bir hata oluştu: {str(e)}")
        finally:
            conn.close()
            
    def edit_profile(self):
        # Check if there's any data to edit
        if self.profile_table.rowCount() == 0:
            QMessageBox.warning(self, "Uyarı", "Düzenlenecek kayıt bulunamadı!")
            return
            
        # Get the data from the form
        company_name = self.company_name.text().strip()
        full_name = self.full_name.text().strip()
        phone = self.phone.text().strip()

        # Validate the input
        if not all([company_name, full_name, phone]):
            QMessageBox.warning(self, "Hata", "Lütfen tüm alanları doldurun!")
            return
            
        if len(phone) != 11 or not phone.isdigit():
            QMessageBox.warning(self, "Hata", "Lütfen geçerli bir telefon numarası girin (11 hane).")
            self.phone.setFocus()
            return
            
        # Ask for confirmation
        reply = QMessageBox.question(self, 'Onay', 'Profil bilgilerini güncellemek istediğinize emin misiniz?',
                                   QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            conn = None
            try:
                conn = sqlite3.connect('fleet_management.db')
                cursor = conn.cursor()
                
                # Update the user's profile
                cursor.execute("""
                    UPDATE users 
                    SET company_name = ?, full_name = ?, phone = ?
                    WHERE id = ?
                """, (company_name, full_name, phone, self.user_id))
                
                conn.commit()
                
                # Refresh the table
                self.load_profile()
                
                # Clear the form
                self.clear_profile_form()
                
                QMessageBox.information(self, "Başarılı", "Profil bilgileriniz başarıyla güncellendi!")
                
            except sqlite3.Error as e:
                if conn:
                    conn.rollback()
                QMessageBox.critical(self, "Hata", f"Profil güncellenirken bir hata oluştu: {str(e)}")
            finally:
                if conn:
                    conn.close()
            
    def delete_profile(self):
        selected_row = self.profile_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Uyarı", "Silmek için bir kayıt seçiniz!")
            return
            
        reply = QMessageBox.question(self, 'Onay', 'Seçili profili silmek istediğinize emin misiniz?',
                                   QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            conn = sqlite3.connect('fleet_management.db')
            cursor = conn.cursor()
            
            try:
                # Kullanıcı bilgilerini temizle
                cursor.execute("""
                    UPDATE users 
                    SET company_name = NULL, full_name = NULL, phone = NULL
                    WHERE id = ?
                """, (self.user_id,))
                
                conn.commit()
                
                # Formu temizle
                self.clear_profile_form()
                
                # Tabloyu güncelle
                self.load_profile()
                
                QMessageBox.information(self, "Başarılı", "Profil bilgileriniz başarıyla silindi!")
                
            except sqlite3.Error as e:
                QMessageBox.critical(self, "Hata", f"Profil silinirken bir hata oluştu: {str(e)}")
            finally:
                conn.close()
    
    def clear_profile_form(self):
        self.company_name.clear()
        self.full_name.clear()
        self.phone.clear()
    
    def populate_profile_fields(self, row, column):
        # Only populate if there are rows in the table
        if self.profile_table.rowCount() > 0 and row >= 0:
            # Get the data from the selected row
            company = self.profile_table.item(row, 0).text()
            full_name = self.profile_table.item(row, 1).text()
            phone = self.profile_table.item(row, 2).text()
            
            # Fill the form with the selected data
            self.company_name.setText(company)
            self.full_name.setText(full_name)
            self.phone.setText(phone)
            
            # Highlight the selected row
            self.profile_table.selectRow(row)
            
            # Set focus to the first field for editing
            self.company_name.setFocus()

    def create_drivers_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(20)

        # Form container
        form = QFormLayout()
        self.driver_name = QLineEdit()
        self.driver_phone = QLineEdit()
        self.driver_tc = QLineEdit()
        
        # Telefon validasyonu (11 haneli)
        phone_validator = QRegExpValidator(QRegExp(r'[0-9]{11}'))
        self.driver_phone.setValidator(phone_validator)
        self.driver_phone.setPlaceholderText("5xxxxxxxxx")
        self.driver_phone.setMaxLength(11)
        
        # TC kimlik no validasyonu (11 haneli)
        tc_validator = QRegExpValidator(QRegExp(r'[0-9]{11}'))
        self.driver_tc.setValidator(tc_validator)
        self.driver_tc.setPlaceholderText("11 haneli TC kimlik no")
        self.driver_tc.setMaxLength(11)
        
        form.addRow("Sürücü Adı:", self.driver_name)
        form.addRow("Telefon:", self.driver_phone)
        form.addRow("TC Kimlik No:", self.driver_tc)

        # Butonlar
        btn_layout = QHBoxLayout()
        add_btn = QPushButton("Sürücü Ekle")
        add_btn.clicked.connect(self.add_driver)
        btn_layout.addWidget(add_btn)

        edit_btn = QPushButton("Sürücü Düzenle")
        edit_btn.clicked.connect(self.edit_driver)
        btn_layout.addWidget(edit_btn)

        delete_btn = QPushButton("Sürücü Sil")
        delete_btn.clicked.connect(self.delete_driver)
        btn_layout.addWidget(delete_btn)

        btn_layout.addStretch()

        # Tablo
        self.drivers_table = QTableWidget()
        self.drivers_table.setColumnCount(3)
        self.drivers_table.setHorizontalHeaderLabels(["Sürücü Adı", "Telefon", "TC Kimlik No"])
        self.drivers_table.horizontalHeader().setStretchLastSection(True)
        self.drivers_table.cellClicked.connect(self.populate_driver_fields)

        layout.addLayout(form)
        layout.addLayout(btn_layout)
        layout.addWidget(self.drivers_table)
        self.load_drivers_table()

        return tab

    def create_trucks_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(20)

        # Form container
        form = QFormLayout()
        self.plate_number = QLineEdit()
        self.truck_driver = QComboBox()
        self.truck_weight = QLineEdit()
        self.truck_weight.setPlaceholderText("Kg cinsinden giriniz")
        
        # Yük ağırlığı için sayısal validasyon
        weight_validator = QRegExpValidator(QRegExp(r'[0-9]*\.?[0-9]+'))
        self.truck_weight.setValidator(weight_validator)
        
        form.addRow("Plaka:", self.plate_number)
        form.addRow("Sürücü:", self.truck_driver)
        form.addRow("Yük Ağırlığı (kg):", self.truck_weight)

        # Butonlar
        btn_layout = QHBoxLayout()
        add_btn = QPushButton("Kamyon Ekle")
        add_btn.clicked.connect(self.add_truck)
        btn_layout.addWidget(add_btn)

        edit_btn = QPushButton("Kamyon Düzenle")
        edit_btn.clicked.connect(self.edit_truck)
        btn_layout.addWidget(edit_btn)

        delete_btn = QPushButton("Kamyon Sil")
        delete_btn.clicked.connect(self.delete_truck)
        btn_layout.addWidget(delete_btn)

        btn_layout.addStretch()

        # Tablo
        self.trucks_table = QTableWidget()
        self.trucks_table.setColumnCount(3)
        self.trucks_table.setHorizontalHeaderLabels(["Plaka", "Sürücü", "Yük Ağırlığı (kg)"])
        self.trucks_table.horizontalHeader().setStretchLastSection(True)
        self.trucks_table.cellClicked.connect(self.populate_truck_fields)

        layout.addLayout(form)
        layout.addLayout(btn_layout)
        layout.addWidget(self.trucks_table)

        # Verileri yükle
        self.load_drivers_combo()
        self.load_trucks_table()

        return tab

    def create_trips_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(20)

        # Form container
        form = QFormLayout()
        
        self.trip_truck = QComboBox()
        self.trip_start_point = QLineEdit()
        self.trip_destination = QLineEdit()
        self.trip_date = QDateEdit()
        self.trip_date.setDate(QDate.currentDate())
        self.trip_date.setCalendarPopup(True)
        self.trip_status = QComboBox()
        self.trip_status.addItems(["Planlandı", "Yolda", "Tamamlandı"])

        # Başlangıç noktası için onay butonu
        start_layout = QHBoxLayout()
        start_layout.addWidget(self.trip_start_point)
        start_confirm_btn = QPushButton("Onayla")
        start_confirm_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 5px 10px;
                border: none;
                border-radius: 3px;
                min-width: 60px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        start_confirm_btn.clicked.connect(lambda: self.confirm_location(self.trip_start_point))
        start_layout.addWidget(start_confirm_btn)

        # Varış noktası için onay butonu
        end_layout = QHBoxLayout()
        end_layout.addWidget(self.trip_destination)
        end_confirm_btn = QPushButton("Onayla")
        end_confirm_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 5px 10px;
                border: none;
                border-radius: 3px;
                min-width: 60px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        end_confirm_btn.clicked.connect(lambda: self.confirm_location(self.trip_destination))
        end_layout.addWidget(end_confirm_btn)

        # Konum arama önerileri için QCompleter
        self.start_completer = QCompleter()
        self.start_completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.start_completer.setFilterMode(Qt.MatchContains)
        self.trip_start_point.setCompleter(self.start_completer)
        self.trip_start_point.textChanged.connect(lambda: self.update_location_suggestions(self.trip_start_point))

        self.end_completer = QCompleter()
        self.end_completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.end_completer.setFilterMode(Qt.MatchContains)
        self.trip_destination.setCompleter(self.end_completer)
        self.trip_destination.textChanged.connect(lambda: self.update_location_suggestions(self.trip_destination))

        # Türkiye'deki şehirler ve ilçeler listesi
        self.locations = [
            # İstanbul
            "İstanbul", "Kadıköy", "Üsküdar", "Beşiktaş", "Şişli", "Bakırköy", "Pendik", "Kartal", "Maltepe", "Ataşehir",
            "Ümraniye", "Beyoğlu", "Fatih", "Bağcılar", "Bahçelievler", "Beylikdüzü", "Avcılar", "Esenyurt", "Sultanbeyli",
            "Sarıyer", "Beykoz", "Tuzla", "Çekmeköy", "Sancaktepe", "Başakşehir", "Esenler", "Gaziosmanpaşa", "Kağıthane",
            
            # Ankara
            "Ankara", "Çankaya", "Keçiören", "Mamak", "Yenimahalle", "Etimesgut", "Sincan", "Altındağ", "Pursaklar",
            "Polatlı", "Kızılcahamam", "Beypazarı", "Nallıhan", "Haymana", "Kazan", "Elmadağ", "Gölbaşı", "Kahramankazan",
            
            # İzmir
            "İzmir", "Konak", "Karşıyaka", "Bornova", "Buca", "Çiğli", "Gaziemir", "Menemen", "Torbalı", "Bergama",
            "Ödemiş", "Tire", "Aliağa", "Foça", "Çeşme", "Seferihisar", "Urla", "Kemalpaşa", "Menderes", "Bayraklı",
            
            # Bursa
            "Bursa", "Nilüfer", "Osmangazi", "Yıldırım", "İnegöl", "Gemlik", "Mudanya", "Mustafakemalpaşa", "İznik",
            "Karacabey", "Orhangazi", "Kestel", "Gürsu", "Yenişehir", "Orhaneli", "Büyükorhan", "Harmancık", "Keles",
            
            # Antalya
            "Antalya", "Muratpaşa", "Konyaaltı", "Kepez", "Manavgat", "Alanya", "Serik", "Kemer", "Kaş", "Finike",
            "Kumluca", "Demre", "Elmalı", "Akseki", "Gündoğmuş", "İbradı", "Gazipaşa", "Aksu", "Döşemealtı",
            
            # Diğer Büyük Şehirler
            "Adana", "Seyhan", "Çukurova", "Sarıçam", "Ceyhan", "Feke", "İmamoğlu", "Karaisalı", "Karataş", "Kozan",
            "Pozantı", "Saimbeyli", "Tufanbeyli", "Yumurtalık", "Yüreğir",
            
            "Konya", "Selçuklu", "Meram", "Karatay", "Ereğli", "Akşehir", "Seydişehir", "Ilgın", "Çumra", "Cihanbeyli",
            "Kulu", "Beyşehir", "Seydişehir", "Kadınhanı", "Sarayönü", "Doğanhisar", "Hüyük", "Yunak",
            
            "Gaziantep", "Şahinbey", "Şehitkamil", "Nizip", "İslahiye", "Nurdağı", "Araban", "Oğuzeli", "Yavuzeli",
            "Karkamış", "Nizip", "İslahiye", "Nurdağı", "Araban", "Oğuzeli", "Yavuzeli", "Karkamış",
            
            "Şanlıurfa", "Eyyübiye", "Haliliye", "Karaköprü", "Siverek", "Viranşehir", "Suruç", "Birecik", "Harran",
            "Akçakale", "Hilvan", "Bozova", "Halfeti", "Ceylanpınar", "Karaköprü",
            
            "Kocaeli", "İzmit", "Gebze", "Derince", "Körfez", "Gölcük", "Çayırova", "Darıca", "Karamürsel", "Kandıra",
            "Başiskele", "Kartepe", "Dilovası", "Karamürsel", "Kandıra", "Başiskele", "Kartepe", "Dilovası",
            
            # Diğer İller
            "Adıyaman", "Afyonkarahisar", "Ağrı", "Amasya", "Artvin", "Aydın", "Balıkesir", "Bilecik", "Bingöl", "Bitlis",
            "Bolu", "Burdur", "Çanakkale", "Çankırı", "Çorum", "Denizli", "Diyarbakır", "Edirne", "Elazığ", "Erzincan",
            "Erzurum", "Eskişehir", "Giresun", "Gümüşhane", "Hakkari", "Hatay", "Isparta", "Mersin", "Kars", "Kastamonu",
            "Kayseri", "Kırklareli", "Kırşehir", "Kütahya", "Malatya", "Manisa", "Kahramanmaraş", "Mardin", "Muğla", "Muş",
            "Nevşehir", "Niğde", "Ordu", "Rize", "Sakarya", "Samsun", "Siirt", "Sinop", "Sivas", "Tekirdağ", "Tokat",
            "Trabzon", "Tunceli", "Uşak", "Van", "Yozgat", "Zonguldak", "Aksaray", "Bayburt", "Karaman", "Kırıkkale",
            "Batman", "Şırnak", "Bartın", "Ardahan", "Iğdır", "Yalova", "Karabük", "Kilis", "Osmaniye", "Düzce"
        ]

        # Konum önerilerini ayarla
        self.start_completer.setModel(QStringListModel(self.locations))
        self.end_completer.setModel(QStringListModel(self.locations))

        form.addRow("Kamyon:", self.trip_truck)
        form.addRow("Başlangıç Noktası:", start_layout)
        form.addRow("Varış Noktası:", end_layout)
        form.addRow("Tarih:", self.trip_date)
        form.addRow("Durum:", self.trip_status)

        # Butonlar
        btn_layout = QHBoxLayout()
        add_btn = QPushButton("Sefer Ekle")
        add_btn.clicked.connect(self.add_trip)
        btn_layout.addWidget(add_btn)

        edit_btn = QPushButton("Sefer Düzenle")
        edit_btn.clicked.connect(self.edit_trip)
        btn_layout.addWidget(edit_btn)

        delete_btn = QPushButton("Sefer Sil")
        delete_btn.clicked.connect(self.delete_trip)
        btn_layout.addWidget(delete_btn)

        btn_layout.addStretch()

        # Tablo
        self.trips_table = QTableWidget()
        self.trips_table.setColumnCount(7)
        self.trips_table.setHorizontalHeaderLabels([
            "Kamyon", "Sürücü", "Başlangıç", "Varış Noktası", "Tarih", "Durum", "Rota"
        ])
        self.trips_table.horizontalHeader().setStretchLastSection(True)
        self.trips_table.cellClicked.connect(self.populate_trip_fields)

        layout.addLayout(form)
        layout.addLayout(btn_layout)
        layout.addWidget(self.trips_table)

        # Verileri yükle
        self.load_trucks_for_trips()
        self.load_trips_table()

        return tab

    def create_map_tab(self):
        """Harita sekmesini oluşturur"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Harita widget'ı
        self.map_view = QWebEngineView()
        
        # OpenStreetMap'i yükle
        map_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Harita</title>
            <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
            <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
            <style>
                #map { 
                    height: 100vh; 
                    width: 100%; 
                    background: #f8f9fa;
                }
                html, body { 
                    height: 100%; 
                    margin: 0; 
                    padding: 0; 
                }
            </style>
        </head>
        <body>
            <div id="map"></div>
            <script>
                let map = null;
                let routeLine = null;
                let startMarker = null;
                let endMarker = null;

                document.addEventListener('DOMContentLoaded', function() {
                    initMap();
                });

                function initMap() {
                    map = L.map('map', {
                        zoomControl: true,
                        attributionControl: false,
                        dragging: true,
                        touchZoom: true,
                        scrollWheelZoom: true,
                        doubleClickZoom: true,
                        boxZoom: true,
                        keyboard: true,
                        maxZoom: 18,
                        minZoom: 5
                    });
                    
                    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                        maxZoom: 19,
                        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                    }).addTo(map);

                    // Türkiye'nin merkezine odaklan
                    map.setView([39.9334, 32.8597], 6);
                }

                async function drawRoute(startPoint, endPoint) {
                    // Önceki rotayı temizle
                    if (routeLine) {
                        map.removeLayer(routeLine);
                    }
                    if (startMarker) {
                        map.removeLayer(startMarker);
                    }
                    if (endMarker) {
                        map.removeLayer(endMarker);
                    }

                    // Başlangıç ve bitiş noktalarını işaretle
                    startMarker = L.marker(startPoint).addTo(map);
                    startMarker.bindPopup("Başlangıç Noktası").openPopup();
                    
                    endMarker = L.marker(endPoint).addTo(map);
                    endMarker.bindPopup("Varış Noktası").openPopup();

                    try {
                        // OSRM API'sine istek at
                        const response = await fetch(
                            `https://router.project-osrm.org/route/v1/driving/${startPoint[1]},${startPoint[0]};${endPoint[1]},${endPoint[0]}?overview=full&geometries=geojson`
                        );

                        const data = await response.json();
                        console.log('API Response:', data); // API yanıtını kontrol et
                        
                        if (data.routes && data.routes.length > 0) {
                            const route = data.routes[0];
                            const coordinates = route.geometry.coordinates.map(coord => [coord[1], coord[0]]);
                            
                            console.log('Coordinates:', coordinates); // Koordinatları kontrol et

                            if (coordinates.length > 0) {
                                // Rota çizgisi
                                routeLine = L.polyline(coordinates, {
                                    color: '#4CAF50',
                                    weight: 6,
                                    opacity: 0.8,
                                    lineJoin: 'round'
                                }).addTo(map);

                                // Haritayı rotaya odakla
                                const bounds = L.latLngBounds(coordinates);
                                map.fitBounds(bounds, {
                                    padding: [50, 50],
                                    maxZoom: 12
                                });
                            } else {
                                console.error('Geçerli koordinat bulunamadı');
                                drawDirectLine();
                            }
                        } else {
                            console.error('Rota bulunamadı');
                            drawDirectLine();
                        }
                    } catch (error) {
                        console.error('Rota hesaplanırken hata oluştu:', error);
                        drawDirectLine();
                    }

                    function drawDirectLine() {
                        // Düz çizgi çiz
                        routeLine = L.polyline([startPoint, endPoint], {
                            color: '#4CAF50',
                            weight: 6,
                            opacity: 0.8,
                            lineJoin: 'round',
                            dashArray: '5, 10'
                        }).addTo(map);
                        
                        const bounds = L.latLngBounds([startPoint, endPoint]);
                        map.fitBounds(bounds, {
                            padding: [50, 50],
                            maxZoom: 12
                        });
                    }
                }
            </script>
        </body>
        </html>
        """
        
        self.map_view.setHtml(map_html)
        layout.addWidget(self.map_view)
        
        return tab

    def create_about_tab(self):
        """Hakkında sekmesini oluşturur"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Başlık
        title = QLabel("Filo Yönetim Sistemi")
        title.setStyleSheet("font-size: 24pt; font-weight: bold; color: #4CAF50;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Versiyon
        version = QLabel("Versiyon 1.0")
        version.setStyleSheet("font-size: 14pt; color: #666;")
        version.setAlignment(Qt.AlignCenter)
        layout.addWidget(version)
        
        # Açıklama
        description = QLabel("""
        Bu uygulama, filo yönetimi için geliştirilmiş bir sistemdir.
        
        Özellikler:
        • Kamyon yönetimi
        • Sürücü yönetimi
        • Sefer takibi
        • Harita görüntüleme
        
        Geliştirici: [Geliştirici Adı]
        İletişim: [İletişim Bilgileri]
        """)
        description.setStyleSheet("font-size: 12pt; margin: 20px;")
        description.setAlignment(Qt.AlignCenter)
        description.setWordWrap(True)
        layout.addWidget(description)
        
        layout.addStretch()
        return tab

    def show_map_with_route(self, route_data):
        """Haritayı gösterir ve rotayı çizer"""
        # Harita sekmesine geç
        for i in range(self.tabs.count()):
            if self.tabs.tabText(i) == "Harita":
                self.tabs.setCurrentIndex(i)
                break

        # JavaScript'e rota verisini gönder
        js_code = f"drawRoute({route_data[0]}, {route_data[1]});"
        self.map_view.page().runJavaScript(js_code)

    def draw_trip_route(self):
        """Seçili seferin rotasını haritada gösterir"""
        start_point = self.trip_start_point.text()
        destination = self.trip_destination.text()

        if not start_point or not destination:
            QMessageBox.warning(self, "Hata", "Başlangıç ve varış noktaları gereklidir!")
            return

        try:
            # Timeout süresini 5 saniyeye düşürelim
            geolocator = Nominatim(user_agent="fleet_management", timeout=5)
            
            # Başlangıç noktasının koordinatlarını al
            start_location = geolocator.geocode(start_point + ", Turkey")
            if not start_location:
                QMessageBox.warning(self, "Hata", "Başlangıç noktası bulunamadı!")
                return
                
            # Varış noktasının koordinatlarını al
            end_location = geolocator.geocode(destination + ", Turkey")
            if not end_location:
                QMessageBox.warning(self, "Hata", "Varış noktası bulunamadı!")
                return

            # Rota verilerini oluştur
            route_data = [
                [start_location.latitude, start_location.longitude],
                [end_location.latitude, end_location.longitude]
            ]

            # Haritayı göster ve rotayı çiz
            self.show_map_with_route(route_data)

        except GeocoderTimedOut:
            QMessageBox.warning(self, "Hata", "Konum servisi zaman aşımına uğradı! Lütfen tekrar deneyin.")
        except Exception as e:
            QMessageBox.warning(self, "Hata", f"Rota çizilirken hata oluştu: {str(e)}\nLütfen tekrar deneyin.")

    def confirm_location(self, line_edit):
        """Konum onaylama işlemini gerçekleştirir"""
        location_text = line_edit.text()
        if not location_text:
            QMessageBox.warning(self, "Hata", "Lütfen bir konum girin!")
            return

        try:
            # Timeout süresini 5 saniyeye düşürelim
            geolocator = Nominatim(user_agent="fleet_management", timeout=5)
            location = geolocator.geocode(location_text + ", Turkey")
            
            if location:
                QMessageBox.information(self, "Başarılı", f"Konum onaylandı: {location_text}")
            else:
                QMessageBox.warning(self, "Hata", "Konum bulunamadı!")
        except GeocoderTimedOut:
            QMessageBox.warning(self, "Hata", "Konum servisi zaman aşımına uğradı! Lütfen tekrar deneyin.")
        except Exception as e:
            QMessageBox.warning(self, "Hata", f"Konum onaylanırken hata oluştu: {str(e)}\nLütfen tekrar deneyin.")

    def add_trip(self):
        truck = self.trip_truck.currentText()
        start_point = self.trip_start_point.text()
        destination = self.trip_destination.text()
        date = self.trip_date.date().toString("yyyy-MM-dd")
        status = self.trip_status.currentText()

        if not all([truck, start_point, destination]):
            QMessageBox.warning(self, "Hata", "Tüm alanları doldurun!")
            return

        conn = sqlite3.connect('fleet_management.db')
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO trips (truck_id, start_point, destination, start_date, status, user_id)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (self.truck_ids[truck], start_point, destination, date, status, self.user_id))
            
            conn.commit()
            QMessageBox.information(self, "Başarılı", "Sefer başarıyla eklendi!")
            
            # Formu temizle
            self.trip_start_point.clear()
            self.trip_destination.clear()
            
            # Tabloyu güncelle
            self.load_trips_table()
            
        except sqlite3.Error as e:
            QMessageBox.warning(self, "Hata", f"Sefer eklenirken hata oluştu: {str(e)}")
        finally:
            conn.close()

    def edit_trip(self):
        selected_row = self.trips_table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Hata", "Düzenlenecek seferi seçin!")
            return

        # Sefer bilgilerini al
        truck = self.trip_truck.currentText()
        start_point = self.trip_start_point.text()
        destination = self.trip_destination.text()
        date = self.trip_date.date().toString("yyyy-MM-dd")
        status = self.trip_status.currentText()

        if not all([truck, start_point, destination]):
            QMessageBox.warning(self, "Hata", "Tüm alanları doldurun!")
            return

        conn = sqlite3.connect('fleet_management.db')
        cursor = conn.cursor()

        try:
            # Önce sefer ID'sini bul
            cursor.execute("""
                SELECT id FROM trips 
                WHERE truck_id = ? AND start_point = ? AND destination = ? AND start_date = ? AND user_id = ?
            """, (self.truck_ids[truck], start_point, destination, date, self.user_id))
            
            trip = cursor.fetchone()
            if not trip:
                QMessageBox.warning(self, "Hata", "Düzenlenecek sefer bulunamadı!")
                return

            # Seferi güncelle
            cursor.execute("""
                UPDATE trips 
                SET truck_id = ?, start_point = ?, destination = ?, start_date = ?, status = ?
                WHERE id = ? AND user_id = ?
            """, (self.truck_ids[truck], start_point, destination, date, status, trip[0], self.user_id))
            
            conn.commit()
            QMessageBox.information(self, "Başarılı", "Sefer başarıyla düzenlendi!")
            
            # Formu temizle
            self.trip_start_point.clear()
            self.trip_destination.clear()
            
            # Tabloyu güncelle
            self.load_trips_table()
            
        except sqlite3.Error as e:
            QMessageBox.warning(self, "Hata", f"Sefer düzenlenirken hata oluştu: {str(e)}")
        finally:
            conn.close()

    def delete_trip(self):
        selected_row = self.trips_table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Hata", "Silinecek seferi seçin!")
            return

        # Sefer bilgilerini al
        truck = self.trips_table.item(selected_row, 0).text()
        start_point = self.trips_table.item(selected_row, 2).text()
        destination = self.trips_table.item(selected_row, 3).text()
        date = self.trips_table.item(selected_row, 4).text()

        reply = QMessageBox.question(self, "Onay", 
                                   f"Bu seferi silmek istediğinizden emin misiniz?\n\n"
                                   f"Kamyon: {truck}\n"
                                   f"Başlangıç: {start_point}\n"
                                   f"Varış: {destination}\n"
                                   f"Tarih: {date}",
                                   QMessageBox.Yes | QMessageBox.No, 
                                   QMessageBox.No)
        
        if reply == QMessageBox.No:
            return

        conn = sqlite3.connect('fleet_management.db')
        cursor = conn.cursor()

        try:
            # Önce sefer ID'sini bul
            cursor.execute("""
                SELECT id FROM trips 
                WHERE truck_id = (SELECT id FROM trucks WHERE plate_number = ? AND user_id = ?)
                AND start_point = ? AND destination = ? AND start_date = ? AND user_id = ?
            """, (truck, self.user_id, start_point, destination, date, self.user_id))
            
            trip = cursor.fetchone()
            if not trip:
                QMessageBox.warning(self, "Hata", "Silinecek sefer bulunamadı!")
                return

            # Seferi sil
            cursor.execute("DELETE FROM trips WHERE id = ? AND user_id = ?", (trip[0], self.user_id))
            conn.commit()
            
            QMessageBox.information(self, "Başarılı", "Sefer başarıyla silindi!")
            
            # Formu temizle
            self.trip_start_point.clear()
            self.trip_destination.clear()
            
            # Tabloyu güncelle
            self.load_trips_table()
            
        except sqlite3.Error as e:
            QMessageBox.warning(self, "Hata", f"Sefer silinirken hata oluştu: {str(e)}")
        finally:
            conn.close()

    def populate_trip_fields(self, row):
        """Seçili seferin bilgilerini forma doldurur"""
        # Tablo verilerini al
        truck = self.trips_table.item(row, 0).text()
        start_point = self.trips_table.item(row, 2).text()
        destination = self.trips_table.item(row, 3).text()
        date = self.trips_table.item(row, 4).text()
        status = self.trips_table.item(row, 5).text()

        # Form alanlarını doldur
        for i in range(self.trip_truck.count()):
            if truck in self.trip_truck.itemText(i):
                self.trip_truck.setCurrentIndex(i)
                break

        self.trip_start_point.setText(start_point)
        self.trip_destination.setText(destination)
        self.trip_date.setDate(QDate.fromString(date, "yyyy-MM-dd"))
        self.trip_status.setCurrentText(status)

    def exit_application(self):
        # Tüm alanların dolu olup olmadığını kontrol et
        # if not self.driver_name.text() or not self.driver_phone.text() or not self.driver_license.text() or \
        #    not self.plate_number.text() or not self.truck_driver.currentText() or not self.truck_weight.text() or \
        #    not self.trip_truck.currentText() or not self.trip_destination.text():
             
        #     # QMessageBox.warning(self, "Uyarı", "Lütfen tüm alanları doldurun!")
        #     return
            
        reply = QMessageBox.question(self, "Çıkış", "Çıkış yapmak istediğinizden emin misiniz?",
                                   QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            sys.exit()
            

    def populate_driver_fields(self, row):
        self.driver_name.setText(self.drivers_table.item(row, 0).text())
        self.driver_phone.setText(self.drivers_table.item(row, 1).text())
        self.driver_tc.setText(self.drivers_table.item(row, 2).text())

    def populate_truck_fields(self, row):
        self.plate_number.setText(self.trucks_table.item(row, 0).text())
        self.truck_driver.setCurrentText(self.trucks_table.item(row, 1).text())
        self.truck_weight.setText(self.trucks_table.item(row, 2).text())

    def add_truck(self):
        plate = self.plate_number.text().upper()
        driver = self.truck_driver.currentText()
        weight = self.truck_weight.text()

        if not plate or not driver or not weight:
            QMessageBox.warning(self, "Hata", "Plaka, sürücü ve yük ağırlığı zorunludur!")
            return

        try:
            weight = float(weight) if weight else 0
        except ValueError:
            QMessageBox.warning(self, "Hata", "Yük ağırlığı geçerli bir sayı olmalıdır!")
            return

        conn = sqlite3.connect('fleet_management.db')
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO trucks (plate_number, driver_id, load_weight, user_id)
                VALUES (?, ?, ?, ?)
            """, (plate, self.driver_ids[driver], weight, self.user_id))
            
            conn.commit()
            QMessageBox.information(self, "Başarılı", "Kamyon başarıyla eklendi!")
            
            # Formu temizle
            self.plate_number.clear()
            self.truck_weight.clear()
            
            # Tabloları güncelle
            self.load_trucks_table()
            self.load_trucks_for_trips()
            
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Hata", "Bu plaka zaten kayıtlı!")
        except sqlite3.Error as e:
            QMessageBox.warning(self, "Hata", f"Kamyon eklenirken hata oluştu: {str(e)}")
        finally:
            conn.close()

    def edit_truck(self):
        selected_row = self.trucks_table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Hata", "Düzenlenecek kamyonu seçin!")
            return

        plate = self.trucks_table.item(selected_row, 0).text()
        driver = self.truck_driver.currentText()
        weight = self.truck_weight.text()

        if not driver or not weight:
            QMessageBox.warning(self, "Hata", "Sürücü ve yük ağırlığı zorunludur!")
            return

        try:
            weight = float(weight) if weight else 0
        except ValueError:
            QMessageBox.warning(self, "Hata", "Yük ağırlığı geçerli bir sayı olmalıdır!")
            return

        conn = sqlite3.connect('fleet_management.db')
        cursor = conn.cursor()

        try:
            cursor.execute("""
                UPDATE trucks SET driver_id = ?, load_weight = ? 
                WHERE plate_number = ? AND user_id = ?
            """, (self.driver_ids[driver], weight, plate, self.user_id))
            
            conn.commit()
            QMessageBox.information(self, "Başarılı", "Kamyon başarıyla düzenlendi!")
            self.load_trucks_table()
            self.load_trucks_for_trips()
        except sqlite3.Error as e:
            QMessageBox.warning(self, "Hata", f"Kamyon düzenlenirken hata oluştu: {str(e)}")
        finally:
            conn.close()

    def delete_truck(self):
        selected_row = self.trucks_table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Hata", "Silinecek kamyonu seçin!")
            return

        plate_number = self.trucks_table.item(selected_row, 0).text()

        conn = sqlite3.connect('fleet_management.db')
        cursor = conn.cursor()

        try:
            cursor.execute("""
                DELETE FROM trucks WHERE plate_number = ? AND user_id = ?
            """, (plate_number, self.user_id))
            conn.commit()
            QMessageBox.information(self, "Başarılı", "Kamyon başarıyla silindi!")
            self.load_trucks_table()
            self.load_trucks_for_trips()
        except sqlite3.Error as e:
            QMessageBox.warning(self, "Hata", f"Kamyon silinirken hata oluştu: {str(e)}")
        finally:
            conn.close()

    def load_trucks_table(self):
        conn = sqlite3.connect('fleet_management.db')
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT t.plate_number, d.name, t.load_weight
            FROM trucks t
            JOIN drivers d ON t.driver_id = d.id
            WHERE t.user_id = ?
        """, (self.user_id,))
        
        trucks = cursor.fetchall()
        self.trucks_table.setRowCount(len(trucks))
        
        for row, (plate, driver, weight) in enumerate(trucks):
            self.trucks_table.setItem(row, 0, QTableWidgetItem(plate))
            self.trucks_table.setItem(row, 1, QTableWidgetItem(driver))
            self.trucks_table.setItem(row, 2, QTableWidgetItem(f"{weight:.1f}" if weight else ""))
        
        conn.close()

    def load_trucks_for_trips(self):
        self.trip_truck.clear()
        conn = sqlite3.connect('fleet_management.db')
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT t.id, t.plate_number, d.name, d.phone
            FROM trucks t
            JOIN drivers d ON t.driver_id = d.id
            WHERE t.user_id = ?
        """, (self.user_id,))
        
        trucks = cursor.fetchall()
        self.truck_ids = {}
        
        for id, plate, driver, phone in trucks:
            display_text = f"{plate} - {driver}"
            self.truck_ids[display_text] = id
            self.trip_truck.addItem(display_text)
        
        conn.close()

    def load_drivers_combo(self):
        self.truck_driver.clear()
        conn = sqlite3.connect('fleet_management.db')
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, name, phone 
            FROM drivers 
            WHERE user_id = ?
        """, (self.user_id,))
        
        drivers = cursor.fetchall()
        self.driver_ids = {}
        
        for id, name, phone in drivers:
            display_text = f"{name} ({phone})" if phone else name
            self.driver_ids[display_text] = id
            self.truck_driver.addItem(display_text)
        
        conn.close()

    def load_drivers_table(self):
        conn = sqlite3.connect('fleet_management.db')
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT name, phone, license_no
            FROM drivers 
            WHERE user_id = ?
        """, (self.user_id,))
        
        drivers = cursor.fetchall()
        self.drivers_table.setRowCount(len(drivers))
        
        for row, (name, phone, tc_no) in enumerate(drivers):
            self.drivers_table.setItem(row, 0, QTableWidgetItem(name))
            self.drivers_table.setItem(row, 1, QTableWidgetItem(phone or ""))
            self.drivers_table.setItem(row, 2, QTableWidgetItem(tc_no or ""))
        
        conn.close()

    def add_driver(self):
        name = self.driver_name.text()
        phone = self.driver_phone.text()
        tc_no = self.driver_tc.text()

        if not name:
            QMessageBox.warning(self, "Hata", "Sürücü adı zorunludur!")
            return

        if phone and len(phone) != 11:
            QMessageBox.warning(self, "Hata", "Telefon numarası 11 haneli olmalıdır!")
            return

        if tc_no and len(tc_no) != 11:
            QMessageBox.warning(self, "Hata", "TC kimlik no 11 haneli olmalıdır!")
            return

        conn = sqlite3.connect('fleet_management.db')
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO drivers (name, phone, license_no, user_id)
                VALUES (?, ?, ?, ?)
            """, (name, phone, tc_no, self.user_id))
            
            conn.commit()
            QMessageBox.information(self, "Başarılı", "Sürücü başarıyla eklendi!")
            
            # Formu temizle
            self.driver_name.clear()
            self.driver_phone.clear()
            self.driver_tc.clear()
            
            # Tabloları güncelle
            self.load_drivers_table()
            self.load_drivers_combo()
            
        except sqlite3.Error as e:
            QMessageBox.warning(self, "Hata", f"Sürücü eklenirken hata oluştu: {str(e)}")
        finally:
            conn.close()

    def edit_driver(self):
        selected_row = self.drivers_table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Hata", "Düzenlenecek sürücüyü seçin!")
            return

        name = self.driver_name.text()
        phone = self.driver_phone.text()
        tc_no = self.driver_tc.text()

        if not name:
            QMessageBox.warning(self, "Hata", "Sürücü adı zorunludur!")
            return

        if phone and len(phone) != 11:
            QMessageBox.warning(self, "Hata", "Telefon numarası 11 haneli olmalıdır!")
            return

        if tc_no and len(tc_no) != 11:
            QMessageBox.warning(self, "Hata", "TC kimlik no 11 haneli olmalıdır!")
            return

        conn = sqlite3.connect('fleet_management.db')
        cursor = conn.cursor()

        try:
            cursor.execute("""
                UPDATE drivers 
                SET name = ?, phone = ?, license_no = ?
                WHERE name = ? AND user_id = ?
            """, (name, phone, tc_no, self.drivers_table.item(selected_row, 0).text(), self.user_id))
            
            conn.commit()
            QMessageBox.information(self, "Başarılı", "Sürücü başarıyla düzenlendi!")
            self.load_drivers_table()
            self.load_drivers_combo()
        except sqlite3.Error as e:
            QMessageBox.warning(self, "Hata", f"Sürücü düzenlenirken hata oluştu: {str(e)}")
        finally:
            conn.close()

    def delete_driver(self):
        selected_row = self.drivers_table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Hata", "Silinecek sürücüyü seçin!")
            return

        name = self.drivers_table.item(selected_row, 0).text()

        reply = QMessageBox.question(self, "Onay", 
                                   "Bu sürücüyü silmek istediğinizden emin misiniz?",
                                   QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.No:
            return

        conn = sqlite3.connect('fleet_management.db')
        cursor = conn.cursor()

        try:
            cursor.execute("""
                DELETE FROM drivers 
                WHERE name = ? AND user_id = ?
            """, (name, self.user_id))
            conn.commit()
            QMessageBox.information(self, "Başarılı", "Sürücü başarıyla silindi!")
            self.load_drivers_table()
            self.load_drivers_combo()
        except sqlite3.Error as e:
            QMessageBox.warning(self, "Hata", f"Sürücü silinirken hata oluştu: {str(e)}")
        finally:
            conn.close()

    def load_trips_table(self):
        conn = sqlite3.connect('fleet_management.db')
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT t.plate_number, d.name, tr.start_point, tr.destination, 
                   tr.start_date, tr.status
            FROM trips tr
            JOIN trucks t ON tr.truck_id = t.id
            JOIN drivers d ON t.driver_id = d.id
            WHERE tr.user_id = ?
            ORDER BY tr.start_date DESC
        """, (self.user_id,))
        
        trips = cursor.fetchall()
        self.trips_table.setRowCount(len(trips))
        
        for row, trip in enumerate(trips):
            for col, value in enumerate(trip):
                self.trips_table.setItem(row, col, QTableWidgetItem(str(value or "")))
            
            # Rota butonu ekle
            route_btn = QPushButton("Rota Çiz")
            route_btn.setStyleSheet("""
                QPushButton {
                    background-color: #4CAF50;
                    color: white;
                    border: none;
                    padding: 5px 10px;
                    border-radius: 3px;
                    font-size: 11px;
                    min-width: 80px;
                }
                QPushButton:hover {
                    background-color: #45a049;
                }
            """)
            route_btn.clicked.connect(lambda checked, r=row: self.draw_route_for_row(r))
            self.trips_table.setCellWidget(row, 6, route_btn)
        
        conn.close()

    def draw_route_for_row(self, row):
        """Belirli bir satırdaki seferin rotasını çizer"""
        start_point = self.trips_table.item(row, 2).text()
        destination = self.trips_table.item(row, 3).text()
        
        if start_point and destination:
            self.trip_start_point.setText(start_point)
            self.trip_destination.setText(destination)
            self.draw_trip_route()

    def update_location_suggestions(self, line_edit):
        """Konum önerilerini günceller"""
        text = line_edit.text().strip()
        if len(text) < 2:  # En az 2 karakter girildiğinde önerileri göster
            return

        # Türkçe karakterleri düzelt
        text = text.replace('i', 'İ').replace('ı', 'I')
        
        # Konum listesinden filtrele
        filtered_locations = [location for location in self.locations if text.upper() in location.upper()]
        
        if line_edit == self.trip_start_point:
            self.start_completer.setModel(QStringListModel(filtered_locations))
        else:
            self.end_completer.setModel(QStringListModel(filtered_locations))

if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication

    # Önbellek dizinini ayarla
    cache_dir = os.path.join(os.path.expanduser("~"), "AppData", "Local", "python", "QtWebEngine", "Default")
    os.makedirs(cache_dir, exist_ok=True)
    
    # QtWebEngine ayarlarını yapılandır
    settings = QWebEngineSettings.globalSettings()
    settings.setAttribute(QWebEngineSettings.LocalStorageEnabled, True)
    settings.setAttribute(QWebEngineSettings.WebGLEnabled, True)
    settings.setAttribute(QWebEngineSettings.DnsPrefetchEnabled, True)
    
    app = QApplication(sys.argv)
    window = MainWindow("Admin", 1)  
    window.show()
    sys.exit(app.exec_())