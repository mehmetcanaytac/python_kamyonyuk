import tkinter as tk

# Giriş penceresi
def giris_penceresi():
    # Yeni pencere oluştur
    giris_window = tk.Toplevel(root)
    giris_window.title("Kullanıcı Girişi")
    giris_window.geometry("300x200")

    # Kullanıcı adı
    lbl_kullanici = tk.Label(giris_window, text="Kullanıcı Adı:")
    lbl_kullanici.pack(pady=10)
    entry_kullanici = tk.Entry(giris_window)
    entry_kullanici.pack(pady=5)

    # Şifre
    lbl_sifre = tk.Label(giris_window, text="Şifre:")
    lbl_sifre.pack(pady=10)
    entry_sifre = tk.Entry(giris_window, show='*')
    entry_sifre.pack(pady=5)

    def giris_yap():
        kullanici = entry_kullanici.get()
        sifre = entry_sifre.get()
        # Kullanıcı adı ve şifre kontrolü
        if kullanici == "admin" and sifre == "1234":  # Bu kısmı kendi ihtiyaçlarınıza göre düzenleyebilirsiniz
            messagebox.showinfo("Başarılı", "Giriş başarılı!")
            giris_window.destroy()  # Giriş penceresini kapat
            root.deiconify()  # Ana pencereyi göster
        else:
            messagebox.showwarning("Hata", "Geçersiz kullanıcı adı veya şifre!")

    # Giriş yap butonu
    btn_giris = tk.Button(giris_window, text="Giriş Yap", command=giris_yap)
    btn_giris.pack(pady=20)

# Pencere oluşturma
root = tk.Tk()
root.title("Kamyon Yük ve Takip Otomasyonu")
root.geometry("400x300")

# Etiket ekleyelim
label = tk.Label(root, text="Merhaba, Tkinter arayüzü!")
label.pack(pady=20)

# Tkinter ana döngüsü
root.mainloop()
