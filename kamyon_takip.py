import tkinter as tk
from tkinter import Menu, ttk, messagebox
import json

import sqlite3  # Veritabanı için SQLite kütüphanesini ekleyin

# Veritabanı bağlantısını kuran fonksiyon
def veritabani_baglan():
    conn = sqlite3.connect("kamyonlar.db")  # Veritabanı dosyası
    return conn

# Veritabanına kamyon bilgisi ekleyen fonksiyon
def veri_ekle(plaka, surucu, kapasite, yuk_adi, yuk_agirlik):
    conn = veritabani_baglan()
    cursor = conn.cursor()
    
    try:
        # Veriyi ekleyin
        cursor.execute("INSERT INTO kamyonlar (plaka, surucu, kapasite, yuk_adi, yuk_agirlik) VALUES (?, ?, ?, ?, ?)",
                       (plaka, surucu, kapasite, yuk_adi, yuk_agirlik))
        conn.commit()
        messagebox.showinfo("Başarılı", "Kamyon bilgisi veritabanına eklendi.")
    except sqlite3.IntegrityError:
        messagebox.showerror("Hata", "Bu plakaya sahip bir kamyon zaten mevcut!")
    finally:
        conn.close()


# Giriş ekranı fonksiyonu
def giris_ekrani():
    giris_window = tk.Toplevel(root)
    giris_window.title("Kullanıcı Girişi")
    giris_window.geometry("300x300")
    giris_window.configure(bg="#1E3D59")

    # Başlık
    lbl_baslik = tk.Label(giris_window, text="Kamyon Takip Sistemi", font=("Arial", 16, "bold"), fg="white", bg="#1E3D59")
    lbl_baslik.pack(pady=20)

    # Kullanıcı adı
    lbl_kullanici = tk.Label(giris_window, text="Kullanıcı Adı:", font=("Arial", 12), fg="white", bg="#1E3D59")
    lbl_kullanici.pack(pady=5)
    entry_kullanici = tk.Entry(giris_window, font=("Arial", 12), width=25)
    entry_kullanici.pack(pady=5)

    # Şifre
    lbl_sifre = tk.Label(giris_window, text="Şifre:", font=("Arial", 12), fg="white", bg="#1E3D59")
    lbl_sifre.pack(pady=5)
    entry_sifre = tk.Entry(giris_window, show='*', font=("Arial", 12), width=25)
    entry_sifre.pack(pady=5)

    # Giriş fonksiyonu
    def giris_yap():
        if entry_kullanici.get() == "admin" and entry_sifre.get() == "1234":
            messagebox.showinfo("Başarılı", "Giriş başarılı!")
            giris_window.destroy()
            root.deiconify()
        else:
            messagebox.showwarning("Hata", "Geçersiz kullanıcı adı veya şifre!")

    # Giriş butonu
    btn_giris = tk.Button(giris_window, text="Giriş Yap", command=giris_yap, font=("Arial", 12), bg="#E63946", fg="white", width=15)
    btn_giris.pack(pady=20)

# Ana pencere oluşturma
root = tk.Tk()
root.title("Kamyon Yük ve Takip Otomasyonu")
root.geometry("750x550")
root.configure(bg="#F1FAEE")
root.withdraw()

# Menü oluşturma
menubar = Menu(root)
root.config(menu=menubar)

# Dosya menüsü
dosya_menu = Menu(menubar, tearoff=0)
menubar.add_cascade(label="Dosya", menu=dosya_menu)
dosya_menu.add_command(label="Veri Yükle")
dosya_menu.add_command(label="Veri Kaydet")
dosya_menu.add_separator()
dosya_menu.add_command(label="Çıkış", command=root.quit)

# Yardım menüsü
yardim_menu = Menu(menubar, tearoff=0)
menubar.add_cascade(label="Yardım", menu=yardim_menu)
yardim_menu.add_command(label="Hakkında")

# Kamyon bilgileri çerçevesi
frame = tk.Frame(root, bg="#F1FAEE")
frame.pack(pady=20)

# Bilgi giriş alanları
tk.Label(frame, text="Plaka", font=("Arial", 12), bg="#F1FAEE").grid(row=0, column=0, padx=10, pady=5)
entry_plaka = tk.Entry(frame, font=("Arial", 12), width=25)
entry_plaka.grid(row=0, column=1, padx=10, pady=5)

tk.Label(frame, text="Sürücü", font=("Arial", 12), bg="#F1FAEE").grid(row=1, column=0, padx=10, pady=5)
entry_surucu = tk.Entry(frame, font=("Arial", 12), width=25)
entry_surucu.grid(row=1, column=1, padx=10, pady=5)

tk.Label(frame, text="Kapasite (ton)", font=("Arial", 12), bg="#F1FAEE").grid(row=2, column=0, padx=10, pady=5)
entry_kapasite = tk.Entry(frame, font=("Arial", 12), width=25)
entry_kapasite.grid(row=2, column=1, padx=10, pady=5)

tk.Label(frame, text="Yük Adı", font=("Arial", 12), bg="#F1FAEE").grid(row=3, column=0, padx=10, pady=5)
entry_yuk_adi = tk.Entry(frame, font=("Arial", 12), width=25)
entry_yuk_adi.grid(row=3, column=1, padx=10, pady=5)

tk.Label(frame, text="Yük Ağırlığı (ton)", font=("Arial", 12), bg="#F1FAEE").grid(row=4, column=0, padx=10, pady=5)
entry_yuk_agirlik = tk.Entry(frame, font=("Arial", 12), width=25)
entry_yuk_agirlik.grid(row=4, column=1, padx=10, pady=5)

# Listeyi kaydetme fonksiyonu
def listeyi_kaydet():
    kamyon_bilgileri = []
    for row_id in tree.get_children():
        kamyon_bilgileri.append(tree.item(row_id)["values"])
    with open("kamyon_bilgileri.json", "w") as dosya:
        json.dump(kamyon_bilgileri, dosya)
    messagebox.showinfo("Başarılı", "Bilgiler kaydedildi!")

# Liste ve kaydetme penceresi açma fonksiyonu
def listele_kaydet_penceresi():
    listele_window = tk.Toplevel(root)
    listele_window.title("Kamyon Bilgilerini Listele ve Kaydet")
    listele_window.geometry("750x400")

    # Listeleme alanı
    tree_listele = ttk.Treeview(listele_window, columns=("plaka", "surucu", "kapasite", "yuk_adi", "yuk_agirlik"), show="headings")
    tree_listele.heading("plaka", text="Plaka")
    tree_listele.heading("surucu", text="Sürücü")
    tree_listele.heading("kapasite", text="Kapasite (ton)")
    tree_listele.heading("yuk_adi", text="Yük Adı")
    tree_listele.heading("yuk_agirlik", text="Yük Ağırlığı (ton)")
    tree_listele.pack(pady=20)

    # Listeyi doldurma
    for row_id in tree.get_children():
        tree_listele.insert("", "end", values=tree.item(row_id)["values"])

    # Kaydetme butonu
    btn_kaydet = tk.Button(listele_window, text="Listeyi Kaydet", command=listeyi_kaydet, font=("Arial", 12), bg="#457B9D", fg="white", width=15)
    btn_kaydet.pack(pady=10)

# Kamyon ekleme fonksiyonu
def kamyonu_ekle():
    plaka = entry_plaka.get()
    surucu = entry_surucu.get()
    kapasite = entry_kapasite.get()
    yuk_adi = entry_yuk_adi.get()
    yuk_agirlik = entry_yuk_agirlik.get()
    if not plaka or not surucu or not kapasite or not yuk_adi or not yuk_agirlik:
        messagebox.showwarning("Hata", "Tüm alanları doldurun!")
    else:
        tree.insert("", "end", values=(plaka, surucu, kapasite, yuk_adi, yuk_agirlik))
        messagebox.showinfo("Başarılı", "Kamyon bilgileri eklendi!")
        entry_plaka.delete(0, tk.END)
        entry_surucu.delete(0, tk.END)
        entry_kapasite.delete(0, tk.END)
        entry_yuk_adi.delete(0, tk.END)
        entry_yuk_agirlik.delete(0, tk.END)

# Ekleme butonu
btn_ekle = tk.Button(root, text="Kamyonu Ekle", command=kamyonu_ekle, font=("Arial", 12), bg="#457B9D", fg="white", width=15)
btn_ekle.pack(pady=10)

# Listele ve Kaydet penceresini açan buton
btn_listele_kaydet = tk.Button(root, text="Listele ve Kaydet", command=listele_kaydet_penceresi, font=("Arial", 12), bg="#1D3557", fg="white", width=15)
btn_listele_kaydet.pack(pady=10)

# Listeleme alanı
tree = ttk.Treeview(root, columns=("plaka", "surucu", "kapasite", "yuk_adi", "yuk_agirlik"), show="headings")
tree.heading("plaka", text="Plaka")
tree.heading("surucu", text="Sürücü")
tree.heading("kapasite", text="Kapasite (ton)")
tree.heading("yuk_adi", text="Yük Adı")
tree.heading("yuk_agirlik", text="Yük Ağırlığı (ton)")
tree.pack(pady=20)

# Giriş ekranını göster
giris_ekrani()

# Uygulamayı başlat
root.mainloop()

