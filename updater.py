import customtkinter as ctk
import tkinter as tk
import threading, time, requests, os, winsound
import xml.etree.ElementTree as ET
from PIL import Image, ImageTk

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

REMOTE_XML = "https://raw.githubusercontent.com/jesusquijada34/packagemaker/main/details.xml"
LOCAL_XML = "details.xml"
SOUND_PATH = "assets/afterdelay.wav"
CLOSE_ICON_PATH = "assets/close-btn.png"

class PackagemakerUpdater(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("440x200")
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.configure(fg_color="#0d1117")  # GitHub Dark sólido

        roboto_path = os.path.join(os.getcwd(), "Roboto-Regular.ttf")
        self.roboto = ctk.CTkFont(family="Roboto", size=14) if os.path.exists(roboto_path) else ctk.CTkFont(family="Segoe UI", size=14)

        # Botón cerrar
        if os.path.exists(CLOSE_ICON_PATH):
            close_img = Image.open(CLOSE_ICON_PATH).resize((18, 18))
            self.close_icon = ImageTk.PhotoImage(close_img)
            self.close_btn = tk.Button(self, image=self.close_icon, command=self.fade_out, bd=0, bg="#0d1117", activebackground="#0d1117")
            self.close_btn.place(x=410, y=10)

        # Título y mensaje
        self.title_label = ctk.CTkLabel(self, text="PACKAGEMAKER UPDATER", font=ctk.CTkFont(size=16, weight="bold"), text_color="#2ecc71")
        self.title_label.place(x=20, y=30)

        self.message_label = ctk.CTkLabel(self, text="Packagemaker está listo para recibir actualizaciones remotas\ndesde github.", font=self.roboto, text_color="#2ecc71")
        self.message_label.place(x=20, y=70)

        # Botón verde embestido
        self.ok_btn = ctk.CTkButton(self, text="OK", command=self.fade_out, fg_color="#2ecc71", text_color="white", font=self.roboto, width=100, corner_radius=8)
        self.ok_btn.place(x=320, y=150)

        self.after(100, self.mostrar_inferior_derecha)
        self.reproducir_sonido()

    def mostrar_inferior_derecha(self):
        w, h = self.winfo_width(), self.winfo_height()
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"{w}x{h}+{sw-w-20}+{sh-h-40}")

    def fade_out(self):
        self.withdraw()
        self.iniciar_verificacion()

    def reproducir_sonido(self):
        if os.path.exists(SOUND_PATH):
            winsound.PlaySound(SOUND_PATH, winsound.SND_FILENAME | winsound.SND_ASYNC)

    def mostrar_actualizacion(self, version):
        self.message_label.configure(text=f"🚀 Nueva versión {version} disponible.")
        self.ok_btn.destroy()

        self.instalar_btn = ctk.CTkButton(self, text="Instalar", command=self.instalar, fg_color="#2ecc71", text_color="white", font=self.roboto, corner_radius=8)
        self.later_btn = ctk.CTkButton(self, text="Ahora no", command=self.fade_out, fg_color="#3c3f44", text_color="#2ecc71", font=self.roboto, corner_radius=8)

        self.instalar_btn.place(x=100, y=150)
        self.later_btn.place(x=240, y=150)
        self.deiconify()

    def instalar(self):
        print("Instalando actualización embestida…")
        self.fade_out()

    def iniciar_verificacion(self):
        def ciclo():
            while True:
                local = leer_version(LOCAL_XML)
                remoto = leer_version_remota()
                if remoto and remoto != local:
                    self.after(0, lambda: self.mostrar_actualizacion(remoto))
                time.sleep(10)
        threading.Thread(target=ciclo, daemon=True).start()

def leer_version(path):
    try:
        tree = ET.parse(path)
        return tree.getroot().findtext("version", "")
    except:
        return ""

def leer_version_remota():
    try:
        r = requests.get(REMOTE_XML, timeout=10)
        root = ET.fromstring(r.text)
        return root.findtext("version", "")
    except:
        return ""

if __name__ == "__main__":
    app = PackagemakerUpdater()
    app.mainloop()
