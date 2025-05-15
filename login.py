from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox,
                             QTabWidget, QFormLayout)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QRegExpValidator
from PyQt5.QtCore import QRegExp
import sqlite3
from database import hash_password, verify_password
from main_window import MainWindow
import tkinter as tk
from tkinter import messagebox

class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Kamyon Takip Sistemi")
        self.setFixedSize(800, 600)
        
        # Ana widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(20)

        # Sekmeler
        self.tabs = QTabWidget()
        self.tabs.addTab(self.create_login_tab(), "Giriş")
        self.tabs.addTab(self.create_register_tab(), "Kayıt Ol")
        layout.addWidget(self.tabs)

        # Genel stil ayarları
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
                padding: 10px;
                border-radius: 5px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QLineEdit {
                padding: 8px;
                border: 1px solid #cccccc;
                border-radius: 5px;
                font-size: 14px;
            }
            QLabel {
                color: #333;
                font-size: 14px;
            }
        """)

    def create_login_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(20)

        # Başlık
        title_label = QLabel("Giriş Yap")
        title_label.setFont(QFont("Arial", 18, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        # Form
        form = QFormLayout()
        form.setSpacing(15)

        # Kullanıcı adı
        self.login_username = QLineEdit()
        self.login_username.setPlaceholderText("Kullanıcı adınızı girin")
        form.addRow("Kullanıcı Adı:", self.login_username)

        # Şifre
        self.login_password = QLineEdit()
        self.login_password.setPlaceholderText("Şifrenizi girin")
        self.login_password.setEchoMode(QLineEdit.Password)
        form.addRow("Şifre:", self.login_password)

        # Giriş butonu
        login_btn = QPushButton("Giriş Yap")
        login_btn.clicked.connect(self.login)
        form.addRow("", login_btn)

        layout.addLayout(form)
        layout.addStretch()

        return tab

    def create_register_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(20)

        # Başlık
        title_label = QLabel("Kayıt Ol")
        title_label.setFont(QFont("Arial", 18, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        # Form
        form = QFormLayout()
        form.setSpacing(15)

        # Kullanıcı adı
        self.register_username = QLineEdit()
        self.register_username.setPlaceholderText("Kullanıcı adı oluşturun")
        form.addRow("Kullanıcı Adı:", self.register_username)

        # Şifre
        self.register_password = QLineEdit()
        self.register_password.setPlaceholderText("Şifre oluşturun")
        self.register_password.setEchoMode(QLineEdit.Password)
        form.addRow("Şifre:", self.register_password)

        # Şifre tekrar
        self.register_password_confirm = QLineEdit()
        self.register_password_confirm.setPlaceholderText("Şifrenizi tekrar girin")
        self.register_password_confirm.setEchoMode(QLineEdit.Password)
        form.addRow("Şifre Tekrar:", self.register_password_confirm)

        # Kayıt butonu
        register_btn = QPushButton("Kayıt Ol")
        register_btn.clicked.connect(self.register)
        form.addRow("", register_btn)

        layout.addLayout(form)
        layout.addStretch()

        return tab

    def login(self):
        username = self.login_username.text()
        password = self.login_password.text()

        if not username or not password:
            QMessageBox.warning(self, "Hata", "Lütfen tüm alanları doldurun!")
            return

        conn = sqlite3.connect('fleet_management.db')
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT id, password FROM users 
                WHERE username = ?
            """, (username,))
            
            result = cursor.fetchone()
            
            if result and result[1] == password:  # Basit şifre kontrolü
                user_id = result[0]
                self.main_window = MainWindow(username, user_id)
                self.main_window.show()
                self.close()
            else:
                QMessageBox.warning(self, "Hata", "Kullanıcı adı veya şifre hatalı!")
        except sqlite3.Error as e:
            QMessageBox.warning(self, "Hata", f"Giriş yapılırken hata oluştu: {str(e)}")
        finally:
            conn.close()

    def register(self):
        username = self.register_username.text()
        password = self.register_password.text()
        password_confirm = self.register_password_confirm.text()

        if not all([username, password, password_confirm]):
            QMessageBox.warning(self, "Hata", "Lütfen tüm alanları doldurun!")
            return

        if password != password_confirm:
            QMessageBox.warning(self, "Hata", "Şifreler eşleşmiyor!")
            return

        conn = sqlite3.connect('fleet_management.db')
        cursor = conn.cursor()

        try:
            # Kullanıcı adı kontrolü
            cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
            if cursor.fetchone():
                QMessageBox.warning(self, "Hata", "Bu kullanıcı adı zaten kullanılıyor!")
                return

            # Yeni kullanıcı ekle
            cursor.execute("""
                INSERT INTO users (username, password)
                VALUES (?, ?)
            """, (username, password))  # Şifreyi direkt kaydet
            
            conn.commit()
            QMessageBox.information(self, "Başarılı", "Kayıt başarıyla tamamlandı!")
            
            # Form alanlarını temizle
            self.register_username.clear()
            self.register_password.clear()
            self.register_password_confirm.clear()
            
            # Giriş sekmesine geç
            self.tabs.setCurrentIndex(0)
            
        except sqlite3.Error as e:
            QMessageBox.warning(self, "Hata", f"Kayıt yapılırken hata oluştu: {str(e)}")
        finally:
            conn.close()

if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec_())