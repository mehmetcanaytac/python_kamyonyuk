def kamyonu_ekle():
    plaka = entry_plaka.get()
    surucu = entry_surucu.get()
    kapasite = entry_kapasite.get()
    yuk_adi = entry_yuk_adi.get()
    yuk_agirlik = entry_yuk_agirlik.get()
    
    # Boş alan kontrolü
    if not plaka or not surucu or not kapasite or not yuk_adi or not yuk_agirlik:
        messagebox.showwarning("Hata", "Tüm alanları doldurun!")
    else:
        veri_ekle(plaka, surucu, kapasite, yuk_adi, yuk_agirlik)  # Veritabanına ekle
        # Arayüzde de gösterelim
        tree.insert("", "end", values=(plaka, surucu, kapasite, yuk_adi, yuk_agirlik))
    
    # Alanları temizle
    entry_plaka.delete(0, tk.END)
    entry_surucu.delete(0, tk.END)
    entry_kapasite.delete(0, tk.END)
    entry_yuk_adi.delete(0, tk.END)
    entry_yuk_agirlik.delete(0, tk.END)
