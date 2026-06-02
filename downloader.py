import customtkinter as ctk
import yt_dlp
import threading
from pathlib import Path

# Font ve Tasarım Sabitleri
READABLE_FONT = ("Courier New", 16, "bold")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.deiconify()
        self.overrideredirect(True)
        self.geometry("400x320")
        self.attributes("-transparentcolor", "#000001")
        self.configure(fg_color="#000001")

        # Ana Kapsayıcı
        self.main_frame = ctk.CTkFrame(self, width=400, height=320, corner_radius=25, fg_color="#1a1a1a")
        self.main_frame.place(x=0, y=0)

        # ÜST BAR
        self.title_bar = ctk.CTkFrame(self.main_frame, width=400, height=35, corner_radius=0, fg_color="transparent")
        self.title_bar.place(x=0, y=0)
        self.title_bar.bind("<Button-1>", self.start_move)
        self.title_bar.bind("<B1-Motion>", self.do_move)

        ctk.CTkButton(self.title_bar, text="⚙", width=40, height=30, fg_color="transparent", font=READABLE_FONT, command=self.toggle_settings).place(x=5, y=2)
        ctk.CTkButton(self.title_bar, text="×", width=40, height=30, fg_color="transparent", hover_color="#ff4444", font=READABLE_FONT, command=self.on_closing).place(x=355, y=2)

        # İÇERİK (Hizalamayı sabitledim)
        self.content_frame = ctk.CTkFrame(self.main_frame, width=400, height=285, fg_color="transparent")
        self.content_frame.place(x=0, y=35)
        
        self.entry = ctk.CTkEntry(self.content_frame, placeholder_text="> URL...", width=300, height=40, corner_radius=0, font=READABLE_FONT, justify="center")
        self.entry.place(x=50, y=20)
        
        self.radio_var = ctk.StringVar(value="MP3")
        self.rb1 = ctk.CTkRadioButton(self.content_frame, text="MP3", variable=self.radio_var, value="MP3", font=READABLE_FONT)
        self.rb1.place(x=100, y=80)
        self.rb2 = ctk.CTkRadioButton(self.content_frame, text="MP4", variable=self.radio_var, value="MP4", font=READABLE_FONT)
        self.rb2.place(x=220, y=80)
        
        self.btn = ctk.CTkButton(self.content_frame, text="[ EXECUTE ]", width=200, height=40, corner_radius=0, font=READABLE_FONT, command=self.start_thread)
        self.btn.place(x=100, y=130)
        
        self.progress = ctk.CTkProgressBar(self.content_frame, width=200, height=4, corner_radius=0)
        self.progress.place(x=100, y=185)
        self.progress.set(0)

        # AYARLAR (Başlangıçta gizli)
        self.settings_frame = ctk.CTkFrame(self.main_frame, width=400, height=285, fg_color="#1a1a1a")
        self.settings_frame.place(x=400, y=35)
        
        self.dark_switch = ctk.CTkSwitch(self.settings_frame, text="DARK MODE", font=READABLE_FONT, command=self.update_colors)
        self.dark_switch.select()
        self.dark_switch.place(x=100, y=50)
        self.matrix_switch = ctk.CTkSwitch(self.settings_frame, text="MATRIX MODE", font=READABLE_FONT, command=self.update_colors)
        self.matrix_switch.place(x=100, y=100)
        
        self.update_colors()

    def update_colors(self):
        is_dark = self.dark_switch.get()
        is_matrix = self.matrix_switch.get()
        
        bg = "#000000" if is_matrix else ("#1a1a1a" if is_dark else "#e0e0e0")
        txt = "#00FF41" if is_matrix else ("white" if is_dark else "#2c3e50")
        accent = "#00FF41" if is_matrix else ("#ffffff" if is_dark else "#2c3e50")
        entry_bg = "#333333" if is_matrix else "#cccccc"
        
        self.main_frame.configure(fg_color=bg)
        self.settings_frame.configure(fg_color=bg)
        self.entry.configure(text_color=txt, border_color=txt, placeholder_text_color=txt, fg_color=entry_bg)
        
        # Radyo butonları artık Light mod dahil her zaman görünür
        for w in [self.rb1, self.rb2]:
            w.configure(text_color=txt, border_color=accent, fg_color=accent)
            
        for w in [self.dark_switch, self.matrix_switch]:
            w.configure(text_color=txt, fg_color=bg)
            
        self.btn.configure(fg_color=accent, text_color=bg)
        self.progress.configure(progress_color=accent, fg_color=bg)

    def hook(self, d):
        if d['status'] == 'downloading':
            try:
                p = float(d.get('_percent_str', '0%').replace('%', '')) / 100
                self.progress.set(p)
            except: pass

    def start_thread(self): threading.Thread(target=self.run_process, daemon=True).start()

    def run_process(self):
        url = self.entry.get()
        if not url:
            self.entry.configure(placeholder_text="Link ekleyiniz!")
            return
            
        self.btn.configure(state="disabled", text="[ LOADING... ]")
        try:
            masaustu = Path.home() / "Desktop"
            fmt = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best' if self.radio_var.get() == "MP4" else 'bestaudio/best'
            ydl_opts = {'quiet': True, 'progress_hooks': [self.hook], 'outtmpl': str(masaustu / '%(title)s.%(ext)s'), 'format': fmt}
            if self.radio_var.get() == "MP3": ydl_opts['postprocessors'] = [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '320'}]
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url if "http" in url else f"ytsearch1:{url}"])
        finally:
            self.progress.set(0)
            self.btn.configure(state="normal", text="[ EXECUTE ]")

    def start_move(self, event): self.x, self.y = event.x, event.y
    def do_move(self, event): self.geometry(f"+{self.winfo_x()+(event.x-self.x)}+{self.winfo_y()+(event.y-self.y)}")
    def toggle_settings(self):
        x = 0 if self.settings_frame.winfo_x() >= 400 else 400
        self.settings_frame.place(x=x, y=35)
    def on_closing(self): self.destroy()

if __name__ == "__main__":
    app = App()
    app.mainloop()