import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import calendar
from datetime import datetime, date, timedelta
import os
import sys
from PIL import Image, ImageTk
import database
import exporter

# Tema Tanımları (Aydınlık & Karanlık)
THEMES = {
    "light": {
        "bg": "#F4F6F8",
        "card_bg": "#FFFFFF",
        "header_bg": "#0D2C3A",
        "header_fg": "#FFFFFF",
        "sub_fg": "#B0C4DE",
        "text_main": "#1A252C",
        "text_muted": "#5A6E79",
        "accent_orange": "#D9531E",
        "accent_hover": "#B84113",
        "stat_card_bg": "#163A4D",
        "border": "#DCDCDC",
        "success": "#2E7D32",
        "danger": "#C62828",
        "warning": "#F57F17",
        "highlight_today_bg": "#FFF3E0"
    },
    "dark": {
        "bg": "#10202A",
        "card_bg": "#182C38",
        "header_bg": "#08161E",
        "header_fg": "#FFFFFF",
        "sub_fg": "#90A4AE",
        "text_main": "#E8ECEF",
        "text_muted": "#B0BEC5",
        "accent_orange": "#F26522",
        "accent_hover": "#D84A07",
        "stat_card_bg": "#0D1E28",
        "border": "#2C3E50",
        "success": "#4CAF50",
        "danger": "#EF5350",
        "warning": "#FFCA28",
        "highlight_today_bg": "#332616"
    }
}

MONTH_NAMES = [
    "", "Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran",
    "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"
]
DAY_NAMES = ["Pzt", "Sal", "Çar", "Per", "Cum", "Cmt", "Paz"]

class MDFuarApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("MD Fuar Takip Sistemi")
        self.geometry("1150x780")
        self.minsize(1000, 700)

        # Veritabanını Başlat & Otomatik Yedek Al
        database.init_db()
        database.auto_backup_db()

        # Varsayılan Tema & Tarih
        self.current_theme_key = "light"
        self.theme = THEMES[self.current_theme_key]
        self.configure(bg=self.theme["bg"])

        today = date.today()
        self.current_year = today.year
        self.current_month = today.month
        self.selected_date = today
        self.selected_payment_status = tk.StringVar(value="PAID")

        # Logo Yükle
        self.logo_img = None
        self.load_app_icon()

        # Arayüz Bileşenleri
        self.create_header()
        self.create_main_content()
        self.create_bottom_summary()

        # Kapanış Olayı (Otomatik Yedekleme)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Verileri Yükle
        self.refresh_calendar()
        self.load_selected_date_record()
        self.update_monthly_summary()

    def load_app_icon(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        logo_path = os.path.join(base_dir, "assets", "logo.png")
        if os.path.exists(logo_path):
            try:
                img = Image.open(logo_path)
                self.logo_img = ImageTk.PhotoImage(img.resize((140, 45), Image.Resampling.LANCZOS))
                self.iconphoto(True, ImageTk.PhotoImage(img))
            except Exception as e:
                print("Logo yükleme hatası:", e)

    def toggle_theme(self):
        self.current_theme_key = "dark" if self.current_theme_key == "light" else "light"
        self.theme = THEMES[self.current_theme_key]
        self.configure(bg=self.theme["bg"])
        self.btn_theme.config(
            text="☀️ Aydınlık Mod" if self.current_theme_key == "dark" else "🌙 Karanlık Mod"
        )
        self.apply_theme_colors()

    def apply_theme_colors(self):
        t = self.theme
        self.configure(bg=t["bg"])
        self.header_frame.config(bg=t["header_bg"])
        self.title_box.config(bg=t["header_bg"])
        self.lbl_title.config(bg=t["header_bg"], fg=t["header_fg"])
        self.lbl_subtitle.config(bg=t["header_bg"], fg=t["sub_fg"])
        
        self.main_container.config(bg=t["bg"])
        self.left_panel.config(bg=t["card_bg"], highlightbackground=t["border"])
        self.right_panel.config(bg=t["card_bg"], highlightbackground=t["border"])
        
        self.lbl_selected_date_title.config(bg=t["card_bg"], fg=t["text_main"])
        self.form_frame.config(bg=t["card_bg"])
        self.btn_box.config(bg=t["card_bg"])

        # Form etiketleri
        for child in self.form_frame.winfo_children():
            if isinstance(child, tk.Label):
                if child != self.lbl_net_profit:
                    child.config(bg=t["card_bg"], fg=t["text_main"])
            elif isinstance(child, tk.Entry):
                child.config(bg=t["card_bg"], fg=t["text_main"], insertbackground=t["text_main"])
            elif isinstance(child, tk.Text):
                child.config(bg=t["card_bg"], fg=t["text_main"], insertbackground=t["text_main"])

        # Legend & Alt Özet
        self.legend_frame.config(bg=t["card_bg"])
        self.summary_container.config(bg=t["header_bg"])
        self.lbl_summary_title.config(bg=t["header_bg"])

        self.refresh_calendar()
        self.update_monthly_summary()

    def create_header(self):
        t = self.theme
        self.header_frame = tk.Frame(self, bg=t["header_bg"], height=70, padx=15, pady=10)
        self.header_frame.pack(fill="x", side="top")

        if self.logo_img:
            logo_label = tk.Label(self.header_frame, image=self.logo_img, bg=t["header_bg"])
            logo_label.pack(side="left", padx=(0, 15))

        self.title_box = tk.Frame(self.header_frame, bg=t["header_bg"])
        self.title_box.pack(side="left", fill="y")

        self.lbl_title = tk.Label(
            self.title_box, text="MD FUAR TAKİP SİSTEMİ", font=("Segoe UI", 16, "bold"), fg="white", bg=t["header_bg"]
        )
        self.lbl_title.pack(anchor="w")

        self.lbl_subtitle = tk.Label(
            self.title_box, text="Yövmiye, Hakediş, Cari Hesap ve Not Defteri", font=("Segoe UI", 9), fg=t["sub_fg"], bg=t["header_bg"]
        )
        self.lbl_subtitle.pack(anchor="w")

        # Sağ Üst Butonlar
        btn_container = tk.Frame(self.header_frame, bg=t["header_bg"])
        btn_container.pack(side="right")

        self.btn_theme = tk.Button(
            btn_container, text="🌙 Karanlık Mod", font=("Segoe UI", 9, "bold"), bg="#2C3E50", fg="white", bd=0, padx=10, pady=5, cursor="hand2", command=self.toggle_theme
        )
        self.btn_theme.pack(side="left", padx=4)

        btn_firm_summary = tk.Button(
            btn_container, text="💼 Firma Cari Özeti", font=("Segoe UI", 9, "bold"), bg="#1565C0", fg="white", bd=0, padx=10, pady=5, cursor="hand2", command=self.open_firm_summary_window
        )
        btn_firm_summary.pack(side="left", padx=4)

        btn_excel_report = tk.Button(
            btn_container, text="📊 Excel Raporu Al", font=("Segoe UI", 9, "bold"), bg="#2E7D32", fg="white", bd=0, padx=10, pady=5, cursor="hand2", command=self.open_excel_export_window
        )
        btn_excel_report.pack(side="left", padx=4)

        btn_all_records = tk.Button(
            btn_container, text="🔍 Tüm Kayıtlar", font=("Segoe UI", 9, "bold"), bg=t["accent_orange"], fg="white", bd=0, padx=10, pady=5, cursor="hand2", command=self.open_search_window
        )
        btn_all_records.pack(side="left", padx=4)

    def create_main_content(self):
        t = self.theme
        self.main_container = tk.Frame(self, bg=t["bg"], padx=15, pady=15)
        self.main_container.pack(fill="both", expand=True)

        # Sol Panel: Takvim
        self.left_panel = tk.Frame(self.main_container, bg=t["card_bg"], bd=1, relief="solid", highlightbackground=t["border"])
        self.left_panel.pack(side="left", fill="both", expand=False, padx=(0, 10))

        self.create_calendar_widget(self.left_panel)

        # Sağ Panel: Günün İş & Hesap Detay Formu
        self.right_panel = tk.Frame(self.main_container, bg=t["card_bg"], bd=1, relief="solid", highlightbackground=t["border"], padx=20, pady=15)
        self.right_panel.pack(side="right", fill="both", expand=True)

        self.create_entry_form(self.right_panel)

    def create_calendar_widget(self, parent):
        t = self.theme
        cal_header = tk.Frame(parent, bg=t["header_bg"], padx=10, pady=8)
        cal_header.pack(fill="x")

        self.btn_prev_month = tk.Button(
            cal_header, text="◄", font=("Segoe UI", 11, "bold"), bg=t["header_bg"], fg="white", bd=0, cursor="hand2", command=self.prev_month
        )
        self.btn_prev_month.pack(side="left")

        self.lbl_month_year = tk.Label(
            cal_header, text="", font=("Segoe UI", 13, "bold"), fg="white", bg=t["header_bg"]
        )
        self.lbl_month_year.pack(side="left", expand=True)

        self.btn_today = tk.Button(
            cal_header, text="Bugün", font=("Segoe UI", 9, "bold"), bg=t["accent_orange"], fg="white", bd=0, padx=6, pady=2, cursor="hand2", command=self.go_to_today
        )
        self.btn_today.pack(side="right", padx=(5, 5))

        self.btn_next_month = tk.Button(
            cal_header, text="►", font=("Segoe UI", 11, "bold"), bg=t["header_bg"], fg="white", bd=0, cursor="hand2", command=self.next_month
        )
        self.btn_next_month.pack(side="right")

        # Gün Başlıkları
        days_header = tk.Frame(parent, bg="#E9ECEF" if self.current_theme_key == "light" else "#1F3442", pady=4)
        days_header.pack(fill="x")
        for idx, day_name in enumerate(DAY_NAMES):
            fg_col = t["danger"] if idx >= 5 else t["text_main"]
            lbl = tk.Label(days_header, text=day_name, font=("Segoe UI", 10, "bold"), fg=fg_col, bg=days_header["bg"], width=5)
            lbl.pack(side="left", expand=True, fill="x")

        # Günlük Izgara
        self.grid_frame = tk.Frame(parent, bg=t["card_bg"], padx=5, pady=5)
        self.grid_frame.pack(fill="both", expand=True)

        # Takvim Lejantı
        self.legend_frame = tk.Frame(parent, bg=t["card_bg"], pady=6, padx=10)
        self.legend_frame.pack(fill="x", side="bottom")

        tk.Label(self.legend_frame, text="🟢 Ödendi", font=("Segoe UI", 8, "bold"), fg=t["success"], bg=t["card_bg"]).pack(side="left", padx=3)
        tk.Label(self.legend_frame, text="🟡 Alacak Var", font=("Segoe UI", 8, "bold"), fg=t["warning"], bg=t["card_bg"]).pack(side="left", padx=3)
        tk.Label(self.legend_frame, text="🔴 Bekliyor", font=("Segoe UI", 8, "bold"), fg=t["danger"], bg=t["card_bg"]).pack(side="left", padx=3)

    def refresh_calendar(self):
        t = self.theme
        for widget in self.grid_frame.winfo_children():
            widget.destroy()

        self.lbl_month_year.config(text=f"{MONTH_NAMES[self.current_month]} {self.current_year}")

        recorded_dates_map = database.get_recorded_dates_in_month(self.current_year, self.current_month)

        cal = calendar.Calendar(firstweekday=0)
        month_days = cal.monthdayscalendar(self.current_year, self.current_month)

        today = date.today()

        for row_idx, week in enumerate(month_days):
            for col_idx, day_num in enumerate(week):
                if day_num == 0:
                    lbl_empty = tk.Label(self.grid_frame, text="", bg=t["card_bg"], width=5, height=2)
                    lbl_empty.grid(row=row_idx, column=col_idx, sticky="nsew", padx=2, pady=2)
                else:
                    date_obj = date(self.current_year, self.current_month, day_num)
                    date_str = date_obj.strftime("%Y-%m-%d")

                    is_today = (date_obj == today)
                    is_selected = (date_obj == self.selected_date)
                    status = recorded_dates_map.get(date_str, None)
                    has_record = (status is not None)

                    bg_color = t["card_bg"]
                    fg_color = t["text_main"]
                    border_color = t["border"]
                    border_width = 1

                    if is_selected:
                        bg_color = t["header_bg"]
                        fg_color = "white"
                    elif is_today:
                        bg_color = t["highlight_today_bg"]
                        fg_color = t["accent_orange"]
                        border_color = t["accent_orange"]
                        border_width = 2
                    elif has_record:
                        if status == "PAID":
                            bg_color = "#E8F5E9" if self.current_theme_key == "light" else "#1B3E2B"
                            fg_color = t["success"]
                        elif status == "PARTIAL":
                            bg_color = "#FFF8E1" if self.current_theme_key == "light" else "#3E371B"
                            fg_color = t["warning"]
                        else: # PENDING
                            bg_color = "#FFEBEE" if self.current_theme_key == "light" else "#3E1B1B"
                            fg_color = t["danger"]

                    display_text = str(day_num)
                    if has_record and not is_selected:
                        badge = "🟢" if status == "PAID" else ("🟡" if status == "PARTIAL" else "🔴")
                        display_text += f" {badge}"

                    btn = tk.Button(
                        self.grid_frame,
                        text=display_text,
                        font=("Segoe UI", 11, "bold" if (is_selected or is_today or has_record) else "normal"),
                        bg=bg_color,
                        fg=fg_color,
                        activebackground=t["accent_orange"],
                        activeforeground="white",
                        bd=border_width,
                        relief="solid",
                        cursor="hand2",
                        command=lambda d=date_obj: self.on_date_click(d)
                    )
                    btn.grid(row=row_idx, column=col_idx, sticky="nsew", padx=2, pady=2)

        for i in range(7):
            self.grid_frame.columnconfigure(i, weight=1)
        for i in range(len(month_days)):
            self.grid_frame.rowconfigure(i, weight=1)

    def on_date_click(self, selected_date):
        self.selected_date = selected_date
        self.refresh_calendar()
        self.load_selected_date_record()

    def prev_month(self):
        if self.current_month == 1:
            self.current_month = 12
            self.current_year -= 1
        else:
            self.current_month -= 1
        self.refresh_calendar()
        self.update_monthly_summary()

    def next_month(self):
        if self.current_month == 12:
            self.current_month = 1
            self.current_year += 1
        else:
            self.current_month += 1
        self.refresh_calendar()
        self.update_monthly_summary()

    def go_to_today(self):
        today = date.today()
        self.current_year = today.year
        self.current_month = today.month
        self.selected_date = today
        self.refresh_calendar()
        self.load_selected_date_record()
        self.update_monthly_summary()

    def create_entry_form(self, parent):
        t = self.theme

        self.lbl_selected_date_title = tk.Label(
            parent, text="", font=("Segoe UI", 15, "bold"), fg=t["text_main"], bg=t["card_bg"]
        )
        self.lbl_selected_date_title.pack(anchor="w", pady=(0, 10))

        self.form_frame = tk.Frame(parent, bg=t["card_bg"])
        self.form_frame.pack(fill="both", expand=True)

        # 1. Firma / Fuar / Stant Adı
        tk.Label(self.form_frame, text="Firma / Fuar / Stant Adı:", font=("Segoe UI", 10, "bold"), fg=t["text_main"], bg=t["card_bg"]).grid(row=0, column=0, sticky="w", pady=5)
        self.ent_firm_name = tk.Entry(self.form_frame, font=("Segoe UI", 12), bd=1, relief="solid")
        self.ent_firm_name.grid(row=0, column=1, columnspan=3, sticky="ew", pady=5, padx=(10, 0))

        # 2. Yövmiye Sayısı
        tk.Label(self.form_frame, text="Yövmiye Sayısı:", font=("Segoe UI", 10, "bold"), fg=t["text_main"], bg=t["card_bg"]).grid(row=1, column=0, sticky="w", pady=5)
        self.ent_yovmiye = tk.Entry(self.form_frame, font=("Segoe UI", 12, "bold"), width=12, bd=1, relief="solid")
        self.ent_yovmiye.grid(row=1, column=1, sticky="w", pady=5, padx=(10, 0))
        self.ent_yovmiye.insert(0, "1")

        # 3. Alınan Ödeme (Hakediş)
        tk.Label(self.form_frame, text="Alınan Ödeme (₺):", font=("Segoe UI", 10, "bold"), fg=t["success"], bg=t["card_bg"]).grid(row=2, column=0, sticky="w", pady=5)
        self.ent_received = tk.Entry(self.form_frame, font=("Segoe UI", 12, "bold"), fg=t["success"], width=16, bd=1, relief="solid")
        self.ent_received.grid(row=2, column=1, sticky="w", pady=5, padx=(10, 0))
        self.ent_received.bind("<KeyRelease>", self.calculate_net_profit)

        # 4. İşçilere Ödenen / Masraf
        tk.Label(self.form_frame, text="İşçilere Ödenen (₺):", font=("Segoe UI", 10, "bold"), fg=t["danger"], bg=t["card_bg"]).grid(row=3, column=0, sticky="w", pady=5)
        self.ent_expense = tk.Entry(self.form_frame, font=("Segoe UI", 12, "bold"), fg=t["danger"], width=16, bd=1, relief="solid")
        self.ent_expense.grid(row=3, column=1, sticky="w", pady=5, padx=(10, 0))
        self.ent_expense.bind("<KeyRelease>", self.calculate_net_profit)

        # 5. Ödeme Durum Etiket Seçimi
        tk.Label(self.form_frame, text="Ödeme Durumu:", font=("Segoe UI", 10, "bold"), fg=t["text_main"], bg=t["card_bg"]).grid(row=4, column=0, sticky="w", pady=5)
        
        status_box = tk.Frame(self.form_frame, bg=t["card_bg"])
        status_box.grid(row=4, column=1, columnspan=3, sticky="w", pady=5, padx=(10, 0))

        rb_paid = tk.Radiobutton(status_box, text="🟢 Tamamı Ödendi", variable=self.selected_payment_status, value="PAID", font=("Segoe UI", 9, "bold"), fg=t["success"], bg=t["card_bg"], activebackground=t["card_bg"])
        rb_paid.pack(side="left", padx=(0, 10))

        rb_partial = tk.Radiobutton(status_box, text="🟡 Alacak Var (Kısmi)", variable=self.selected_payment_status, value="PARTIAL", font=("Segoe UI", 9, "bold"), fg=t["warning"], bg=t["card_bg"], activebackground=t["card_bg"])
        rb_partial.pack(side="left", padx=(0, 10))

        rb_pending = tk.Radiobutton(status_box, text="🔴 Ödeme Bekliyor", variable=self.selected_payment_status, value="PENDING", font=("Segoe UI", 9, "bold"), fg=t["danger"], bg=t["card_bg"], activebackground=t["card_bg"])
        rb_pending.pack(side="left")

        # 6. Net Kazanç (BÜYÜK RAKAM)
        tk.Label(self.form_frame, text="Kalan Net Kazanç:", font=("Segoe UI", 11, "bold"), fg=t["text_main"], bg=t["card_bg"]).grid(row=5, column=0, sticky="w", pady=8)
        self.lbl_net_profit = tk.Label(self.form_frame, text="₺0,00", font=("Segoe UI", 16, "bold"), fg=t["accent_orange"], bg=t["highlight_today_bg"], padx=12, pady=5, bd=1, relief="solid")
        self.lbl_net_profit.grid(row=5, column=1, columnspan=2, sticky="w", pady=8, padx=(10, 0))

        # 7. Günün Notları
        tk.Label(self.form_frame, text="Günün Notları:", font=("Segoe UI", 10, "bold"), fg=t["text_main"], bg=t["card_bg"]).grid(row=6, column=0, sticky="nw", pady=5)
        self.txt_notes = tk.Text(self.form_frame, font=("Segoe UI", 10), height=3, bd=1, relief="solid")
        self.txt_notes.grid(row=6, column=1, columnspan=3, sticky="ew", pady=5, padx=(10, 0))

        self.form_frame.columnconfigure(1, weight=1)
        self.form_frame.columnconfigure(3, weight=1)

        # Butonlar
        self.btn_box = tk.Frame(parent, bg=t["card_bg"], pady=10)
        self.btn_box.pack(fill="x", side="bottom")

        self.btn_save = tk.Button(
            self.btn_box, text="💾 KAYDET / GÜNCELLE", font=("Segoe UI", 11, "bold"), bg=t["accent_orange"], fg="white",
            activebackground=t["accent_hover"], activeforeground="white", bd=0, padx=15, pady=8, cursor="hand2", command=self.save_record
        )
        self.btn_save.pack(side="left", padx=(0, 10))

        self.btn_delete = tk.Button(
            self.btn_box, text="🗑️ KAYDI SİL", font=("Segoe UI", 10, "bold"), bg=t["danger"], fg="white",
            activebackground="#A00000", activeforeground="white", bd=0, padx=12, pady=8, cursor="hand2", command=self.delete_record
        )
        self.btn_delete.pack(side="left", padx=(0, 10))

        self.btn_clear = tk.Button(
            self.btn_box, text="🧹 TEMİZLE", font=("Segoe UI", 10), bg="#E0E0E0", fg="#1A252C",
            activebackground="#D0D0D0", bd=0, padx=12, pady=8, cursor="hand2", command=self.clear_form
        )
        self.btn_clear.pack(side="left")

    def calculate_net_profit(self, event=None):
        try:
            received = float(self.ent_received.get().replace(",", ".")) if self.ent_received.get().strip() else 0.0
        except ValueError:
            received = 0.0

        try:
            expense = float(self.ent_expense.get().replace(",", ".")) if self.ent_expense.get().strip() else 0.0
        except ValueError:
            expense = 0.0

        net = received - expense
        self.lbl_net_profit.config(text=f"₺{net:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

    def load_selected_date_record(self):
        date_str = self.selected_date.strftime("%Y-%m-%d")
        day_name = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"][self.selected_date.weekday()]
        date_formatted = f"{self.selected_date.day} {MONTH_NAMES[self.selected_date.month]} {self.selected_date.year} {day_name}"
        
        self.lbl_selected_date_title.config(text=f"📅 {date_formatted}")

        record = database.get_record(date_str)
        self.clear_form()

        if record:
            self.ent_firm_name.insert(0, record["firm_name"] or "")
            self.ent_yovmiye.delete(0, tk.END)
            self.ent_yovmiye.insert(0, str(record["yovmiye"]))
            self.ent_received.insert(0, str(record["amount_received"]))
            self.ent_expense.insert(0, str(record["worker_expense"]))
            self.selected_payment_status.set(record.get("payment_status", "PAID"))
            self.txt_notes.insert("1.0", record["notes"] or "")
            self.calculate_net_profit()
        else:
            self.ent_yovmiye.insert(0, "1")

    def clear_form(self):
        self.ent_firm_name.delete(0, tk.END)
        self.ent_yovmiye.delete(0, tk.END)
        self.ent_received.delete(0, tk.END)
        self.ent_expense.delete(0, tk.END)
        self.selected_payment_status.set("PAID")
        self.txt_notes.delete("1.0", tk.END)
        self.lbl_net_profit.config(text="₺0,00")

    def save_record(self):
        date_str = self.selected_date.strftime("%Y-%m-%d")
        firm_name = self.ent_firm_name.get().strip()

        try:
            yovmiye = float(self.ent_yovmiye.get().replace(",", ".")) if self.ent_yovmiye.get().strip() else 0.0
        except ValueError:
            messagebox.showerror("Hata", "Lütfen geçerli bir yövmiye sayısı girin!")
            return

        try:
            received = float(self.ent_received.get().replace(",", ".")) if self.ent_received.get().strip() else 0.0
        except ValueError:
            messagebox.showerror("Hata", "Lütfen geçerli bir alınan ödeme miktarı girin!")
            return

        try:
            expense = float(self.ent_expense.get().replace(",", ".")) if self.ent_expense.get().strip() else 0.0
        except ValueError:
            messagebox.showerror("Hata", "Lütfen geçerli bir masraf miktarı girin!")
            return

        status = self.selected_payment_status.get()
        notes = self.txt_notes.get("1.0", tk.END).strip()

        database.save_or_update_record(date_str, firm_name, yovmiye, received, expense, status, notes)

        messagebox.showinfo("Başarılı", f"{date_str} tarihli kayıt başarıyla kaydedildi!")
        self.refresh_calendar()
        self.update_monthly_summary()

    def delete_record(self):
        date_str = self.selected_date.strftime("%Y-%m-%d")
        record = database.get_record(date_str)
        if not record:
            messagebox.showwarning("Uyarı", "Bu tarihe ait silinecek bir kayıt bulunamadı.")
            return

        confirm = messagebox.askyesno("Kayıt Sil", f"{date_str} tarihli kaydı silmek istediğinize emin misiniz?")
        if confirm:
            database.delete_record(date_str)
            self.clear_form()
            self.refresh_calendar()
            self.update_monthly_summary()
            messagebox.showinfo("Silindi", "Kayıt başarıyla silindi.")

    def create_bottom_summary(self):
        t = self.theme
        self.summary_container = tk.Frame(self, bg=t["header_bg"], padx=15, pady=10)
        self.summary_container.pack(fill="x", side="bottom")

        self.lbl_summary_title = tk.Label(
            self.summary_container, text="AYLIK ÖZET", font=("Segoe UI", 11, "bold"), fg=t["accent_orange"], bg=t["header_bg"]
        )
        self.lbl_summary_title.pack(side="left", padx=(0, 15))

        cards_frame = tk.Frame(self.summary_container, bg=t["header_bg"])
        cards_frame.pack(side="left", fill="x", expand=True)

        self.card_yovmiye = self.create_stat_card(cards_frame, "📦 Toplam Yövmiye", "0,0 Yövmiye")
        self.card_yovmiye.pack(side="left", expand=True, fill="x", padx=4)

        self.card_received = self.create_stat_card(cards_frame, "💰 Toplam Hakediş", "₺0,00", fg=t["success"])
        self.card_received.pack(side="left", expand=True, fill="x", padx=4)

        self.card_expense = self.create_stat_card(cards_frame, "👷 Toplam İşçi/Masraf", "₺0,00", fg="#FFCDD2")
        self.card_expense.pack(side="left", expand=True, fill="x", padx=4)

        self.card_net = self.create_stat_card(cards_frame, "📈 Net Bakiye", "₺0,00", fg=t["accent_orange"])
        self.card_net.pack(side="left", expand=True, fill="x", padx=4)

    def create_stat_card(self, parent, title, value, fg="white"):
        t = self.theme
        card = tk.Frame(parent, bg=t["stat_card_bg"], padx=10, pady=5, bd=1, relief="solid")
        lbl_t = tk.Label(card, text=title, font=("Segoe UI", 8, "bold"), fg="#B0C4DE", bg=t["stat_card_bg"])
        lbl_t.pack(anchor="w")
        lbl_v = tk.Label(card, text=value, font=("Segoe UI", 13, "bold"), fg=fg, bg=t["stat_card_bg"])
        lbl_v.pack(anchor="w")
        card.lbl_val = lbl_v
        return card

    def update_monthly_summary(self):
        summary = database.get_monthly_summary(self.current_year, self.current_month)
        month_name = MONTH_NAMES[self.current_month]
        self.lbl_summary_title.config(text=f"📊 {month_name.upper()} {self.current_year} ÖZETİ")

        self.card_yovmiye.lbl_val.config(text=f"{summary['total_yovmiye']:.1f} Yövmiye")
        
        recv = summary['total_received']
        self.card_received.lbl_val.config(text=f"₺{recv:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        
        exp = summary['total_expense']
        self.card_expense.lbl_val.config(text=f"₺{exp:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        
        net = summary['total_net']
        self.card_net.lbl_val.config(text=f"₺{net:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

    def open_firm_summary_window(self):
        win = tk.Toplevel(self)
        win.title("MD Fuar Takip Sistemi - Firma Cari Borç / Alacak Özeti")
        win.geometry("900x520")
        t = self.theme
        win.configure(bg=t["bg"])

        top_bar = tk.Frame(win, bg=t["header_bg"], padx=15, pady=10)
        top_bar.pack(fill="x")
        tk.Label(top_bar, text="💼 FIRMALARA GÖRE CARİ HESAP VE ALACAK ÖZETİ", font=("Segoe UI", 12, "bold"), fg="white", bg=t["header_bg"]).pack(side="left")

        table_frame = tk.Frame(win, bg=t["bg"], padx=15, pady=15)
        table_frame.pack(fill="both", expand=True)

        columns = ("firm", "jobs", "yovmiye", "received", "expense", "net", "pending")
        tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)

        tree.heading("firm", text="Firma Adı")
        tree.heading("jobs", text="İş Sayısı")
        tree.heading("yovmiye", text="Toplam Yövmiye")
        tree.heading("received", text="Toplam Hakediş (₺)")
        tree.heading("expense", text="Toplam Masraf (₺)")
        tree.heading("net", text="Net Kazanç (₺)")
        tree.heading("pending", text="Alacaklı / Bekleyen Kayıt")

        tree.column("firm", width=200, anchor="w")
        tree.column("jobs", width=70, anchor="center")
        tree.column("yovmiye", width=100, anchor="center")
        tree.column("received", width=120, anchor="e")
        tree.column("expense", width=120, anchor="e")
        tree.column("net", width=120, anchor="e")
        tree.column("pending", width=140, anchor="center")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

        tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        summaries = database.get_firm_summary()
        for s in summaries:
            recv_fmt = f"₺{s['total_received']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            exp_fmt = f"₺{s['total_expense']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            net_fmt = f"₺{s['total_net']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            
            pending_str = "🟢 Tamamı Ödendi"
            if s["pending_count"] > 0 or s["partial_count"] > 0:
                pending_str = f"🟡 {s['pending_count'] + s['partial_count']} Alacaklı Kayıt"

            tree.insert("", "end", values=(
                s["firm_name"], s["total_jobs"], f"{s['total_yovmiye']:.1f}", recv_fmt, exp_fmt, net_fmt, pending_str
            ))

    def open_excel_export_window(self):
        win = tk.Toplevel(self)
        win.title("MD Fuar Takip Sistemi - Haftalık Excel Raporu Çıkar")
        win.geometry("500x320")
        t = self.theme
        win.configure(bg=t["bg"])

        top_bar = tk.Frame(win, bg=t["header_bg"], padx=15, pady=10)
        top_bar.pack(fill="x")
        tk.Label(top_bar, text="📊 HAFTALIK VEYA TARİH BAZLI EXCEL RAPORU", font=("Segoe UI", 11, "bold"), fg="white", bg=t["header_bg"]).pack(side="left")

        form = tk.Frame(win, bg=t["bg"], padx=20, pady=20)
        form.pack(fill="both", expand=True)

        today = date.today()
        start_default = (today - timedelta(days=6)).strftime("%Y-%m-%d")
        end_default = today.strftime("%Y-%m-%d")

        tk.Label(form, text="Başlangıç Tarihi (YYYY-AA-GG):", font=("Segoe UI", 10, "bold"), fg=t["text_main"], bg=t["bg"]).grid(row=0, column=0, sticky="w", pady=8)
        ent_start = tk.Entry(form, font=("Segoe UI", 11), width=15)
        ent_start.grid(row=0, column=1, sticky="w", pady=8, padx=10)
        ent_start.insert(0, start_default)

        tk.Label(form, text="Bitiş Tarihi (YYYY-AA-GG):", font=("Segoe UI", 10, "bold"), fg=t["text_main"], bg=t["bg"]).grid(row=1, column=0, sticky="w", pady=8)
        ent_end = tk.Entry(form, font=("Segoe UI", 11), width=15)
        ent_end.grid(row=1, column=1, sticky="w", pady=8, padx=10)
        ent_end.insert(0, end_default)

        tk.Label(form, text="Firma Filtresi (Opsiyonel):", font=("Segoe UI", 10, "bold"), fg=t["text_main"], bg=t["bg"]).grid(row=2, column=0, sticky="w", pady=8)
        ent_firm = tk.Entry(form, font=("Segoe UI", 11), width=25)
        ent_firm.grid(row=2, column=1, sticky="w", pady=8, padx=10)

        def do_export():
            s_date = ent_start.get().strip()
            e_date = ent_end.get().strip()
            f_name = ent_firm.get().strip()

            if not s_date or not e_date:
                messagebox.showerror("Hata", "Lütfen başlangıç ve bitiş tarihlerini girin!")
                return

            filepath = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel Dosyası", "*.xlsx"), ("Tüm Dosyalar", "*.*")],
                initialfile=f"MD_Fuar_Raporu_{s_date}_to_{e_date}.xlsx"
            )

            if filepath:
                try:
                    count = exporter.generate_weekly_excel_report(s_date, e_date, f_name, filepath)
                    messagebox.showinfo("Başarılı", f"Toplam {count} kayıt Excel dosyası olarak aktarıldı!\nDosya: {filepath}")
                    win.destroy()
                except Exception as ex:
                    messagebox.showerror("Hata", f"Excel raporu oluşturulurken hata oluştu:\n{ex}")

        btn_export = tk.Button(
            win, text="📥 EXCEL RAPORU OLUŞTUR VE KAYDET", font=("Segoe UI", 11, "bold"), bg=t["success"], fg="white",
            bd=0, padx=15, pady=10, cursor="hand2", command=do_export
        )
        btn_export.pack(pady=(0, 20))

    def open_search_window(self):
        search_win = tk.Toplevel(self)
        search_win.title("MD Fuar Takip Sistemi - Tüm Kayıtlar ve Arama")
        search_win.geometry("900x500")
        t = self.theme
        search_win.configure(bg=t["bg"])

        top_bar = tk.Frame(search_win, bg=t["header_bg"], padx=15, pady=10)
        top_bar.pack(fill="x")

        tk.Label(top_bar, text="Ara (Firma / Not / Tarih):", font=("Segoe UI", 10, "bold"), fg="white", bg=t["header_bg"]).pack(side="left", padx=(0, 10))
        ent_search = tk.Entry(top_bar, font=("Segoe UI", 11), width=30)
        ent_search.pack(side="left", padx=(0, 10))

        table_frame = tk.Frame(search_win, bg=t["bg"], padx=15, pady=15)
        table_frame.pack(fill="both", expand=True)

        columns = ("date", "firm", "yovmiye", "received", "expense", "net", "status", "notes")
        tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)

        tree.heading("date", text="Tarih")
        tree.heading("firm", text="Firma / Fuar Adı")
        tree.heading("yovmiye", text="Yövmiye")
        tree.heading("received", text="Alınan (₺)")
        tree.heading("expense", text="Masraf (₺)")
        tree.heading("net", text="Net Kazanç (₺)")
        tree.heading("status", text="Durum")
        tree.heading("notes", text="Notlar")

        tree.column("date", width=90, anchor="center")
        tree.column("firm", width=160, anchor="w")
        tree.column("yovmiye", width=70, anchor="center")
        tree.column("received", width=100, anchor="e")
        tree.column("expense", width=100, anchor="e")
        tree.column("net", width=100, anchor="e")
        tree.column("status", width=120, anchor="center")
        tree.column("notes", width=160, anchor="w")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

        tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        def load_data(query=""):
            for item in tree.get_children():
                tree.delete(item)
            records = database.search_records(query)
            for r in records:
                recv_fmt = f"₺{r['amount_received']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                exp_fmt = f"₺{r['worker_expense']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                net_fmt = f"₺{r['net_profit']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                st = r.get("payment_status", "PAID")
                st_tr = "🟢 Ödendi" if st == "PAID" else ("🟡 Alacak Var" if st == "PARTIAL" else "🔴 Bekliyor")
                tree.insert("", "end", values=(r["record_date"], r["firm_name"], r["yovmiye"], recv_fmt, exp_fmt, net_fmt, st_tr, r["notes"]))

        def on_search_change(event):
            load_data(ent_search.get().strip())

        ent_search.bind("<KeyRelease>", on_search_change)
        load_data()

        def on_double_click(event):
            selected_item = tree.selection()
            if selected_item:
                vals = tree.item(selected_item[0], "values")
                date_str = vals[0]
                try:
                    dt = datetime.strptime(date_str, "%Y-%m-%d").date()
                    self.current_year = dt.year
                    self.current_month = dt.month
                    self.selected_date = dt
                    self.refresh_calendar()
                    self.load_selected_date_record()
                    self.update_monthly_summary()
                    search_win.destroy()
                except Exception as ex:
                    print("Tarih ayrıştırma hatası:", ex)

        tree.bind("<Double-1>", on_double_click)

    def on_closing(self):
        try:
            database.auto_backup_db()
        except Exception as e:
            print("Kapanış yedeği hatası:", e)
        self.destroy()

if __name__ == "__main__":
    app = MDFuarApp()
    app.mainloop()
