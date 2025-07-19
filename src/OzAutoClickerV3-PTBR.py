import tkinter as tk
from tkinter import ttk, messagebox
import pyautogui
import time
import keyboard
import threading
from pynput import mouse

class AutoClickerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("AutoClicker Pro - Dark Edition")
        self.root.geometry("550x750")
        self.root.resizable(False, False)

        self.colors = {
            'bg': '#1e1e1e',
            'fg': '#ffffff',
            'accent': '#ff3333',
            'success': '#4caf50',
            'warning': '#ff9800',
            'danger': '#f44336',
            'card': '#2d2d2d',
            'border': '#404040'
        }

        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.01

        self.clicking = False
        self.click_delay = tk.DoubleVar(value=1.0)
        self.click_position = None
        self.start_key = tk.StringVar(value="F6")
        self.stop_key = tk.StringVar(value="F7")
        self.click_type = tk.StringVar(value="left")
        self.click_mode = tk.StringVar(value="single")
        self.click_count = tk.IntVar(value=0)
        self.max_clicks = tk.IntVar(value=100)
        self.position_mode = tk.StringVar(value="timer")
        self.follow_mouse = tk.BooleanVar(value=False)
        
        # Variáveis para captura de teclas
        self.capturing_start_key = False
        self.capturing_stop_key = False

        self.setup_dark_theme()
        self.setup_gui()
        self.setup_hotkeys()

        self.position_mode.trace_add("write", lambda *_: self.on_position_mode_change())
        self.on_position_mode_change()

    def setup_dark_theme(self):
        self.root.configure(bg=self.colors['bg'])
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Dark.TCombobox',
                        fieldbackground=self.colors['card'],
                        background=self.colors['card'],
                        foreground=self.colors['fg'],
                        bordercolor=self.colors['border'],
                        arrowcolor=self.colors['fg'])

    def setup_gui(self):
        frame = tk.Frame(self.root, bg=self.colors['bg'])
        frame.pack(fill='both', expand=True, padx=20, pady=20)

        title = tk.Label(frame, text="🖱️ OzAutoClickerV3", fg=self.colors['accent'],
                         bg=self.colors['bg'], font=('Arial', 18, 'bold'))
        title.pack(pady=10)

        # Modo de posição
        modes = tk.Frame(frame, bg=self.colors['card'], relief='solid', bd=2)
        modes.pack(fill='x', pady=10, padx=5)
        modes.configure(highlightbackground=self.colors['border'], highlightthickness=1)

        tk.Label(modes, text="Modo de seleção de posição:", bg=self.colors['card'],
                 fg=self.colors['fg'], font=('Arial', 10, 'bold')).pack(anchor='w', padx=15, pady=(10, 5))

        for text, val in [
            ("⏱️ Timer (5s)", "timer"),
            ("🖱️ Clique do usuário", "click"),
            ("🎯 Seguir cursor em tempo real", "follow")
        ]:
            tk.Radiobutton(modes, text=text, variable=self.position_mode, value=val,
                           bg=self.colors['card'], fg=self.colors['fg'],
                           selectcolor=self.colors['accent'],
                           activebackground=self.colors['card'],
                           highlightthickness=0, bd=0).pack(anchor='w', padx=25, pady=2)

        # Adicionar padding na parte inferior do frame modes
        tk.Label(modes, text="", bg=self.colors['card'], height=1).pack()

        self.position_label = tk.Label(frame, text="Posição: Não definida",
                                       bg=self.colors['card'], fg=self.colors['danger'],
                                       font=('Arial', 10, 'bold'), relief='solid', bd=1,
                                       highlightbackground=self.colors['border'], highlightthickness=1,
                                       pady=8)
        self.position_label.pack(fill='x', pady=10, padx=5)

        self.pos_button = tk.Button(
            frame, text="🎯 Definir Posição",
            command=self.set_position,
            bg=self.colors['accent'], fg='white',
            font=('Arial', 11, 'bold'),
            relief='flat', bd=0,
            highlightthickness=0,
            pady=8
        )
        self.pos_button.pack(pady=8)

        # Seção de teclas personalizadas
        keys_frame = tk.Frame(frame, bg=self.colors['card'], relief='solid', bd=2)
        keys_frame.pack(fill='x', pady=10, padx=5)
        keys_frame.configure(highlightbackground=self.colors['border'], highlightthickness=1)

        tk.Label(keys_frame, text="⌨️ Configuração de Teclas:", bg=self.colors['card'],
                 fg=self.colors['fg'], font=('Arial', 10, 'bold')).pack(anchor='w', padx=15, pady=(10, 5))

        # Tecla de início
        start_key_frame = tk.Frame(keys_frame, bg=self.colors['card'])
        start_key_frame.pack(fill='x', padx=15, pady=8)
        
        tk.Label(start_key_frame, text="▶️ Iniciar:", bg=self.colors['card'],
                 fg=self.colors['fg'], font=('Arial', 9)).pack(side='left')
        
        self.start_key_label = tk.Label(start_key_frame, text=self.start_key.get(),
                                        bg=self.colors['bg'], fg=self.colors['success'],
                                        font=('Arial', 9, 'bold'), relief='solid', bd=1,
                                        width=10, highlightthickness=0, pady=4)
        self.start_key_label.pack(side='left', padx=(10, 5))
        
        tk.Button(start_key_frame, text="🔧 Alterar",
                  command=self.capture_start_key,
                  bg=self.colors['warning'], fg='white',
                  font=('Arial', 8, 'bold'),
                  relief='flat', bd=0, highlightthickness=0,
                  pady=3).pack(side='left')

        # Tecla de parada
        stop_key_frame = tk.Frame(keys_frame, bg=self.colors['card'])
        stop_key_frame.pack(fill='x', padx=15, pady=(0, 10))
        
        tk.Label(stop_key_frame, text="⏹️ Parar:", bg=self.colors['card'],
                 fg=self.colors['fg'], font=('Arial', 9)).pack(side='left', padx=(0, 5))
        
        self.stop_key_label = tk.Label(stop_key_frame, text=self.stop_key.get(),
                                       bg=self.colors['bg'], fg=self.colors['danger'],
                                       font=('Arial', 9, 'bold'), relief='solid', bd=1,
                                       width=10, highlightthickness=0, pady=4)
        self.stop_key_label.pack(side='left', padx=(10, 5))
        
        tk.Button(stop_key_frame, text="🔧 Alterar",
                  command=self.capture_stop_key,
                  bg=self.colors['warning'], fg='white',
                  font=('Arial', 8, 'bold'),
                  relief='flat', bd=0, highlightthickness=0,
                  pady=3).pack(side='left')

        # Controle de clique
        control_frame = tk.Frame(frame, bg=self.colors['card'], relief='solid', bd=2)
        control_frame.pack(fill='x', pady=10, padx=5)
        control_frame.configure(highlightbackground=self.colors['border'], highlightthickness=1)

        tk.Label(control_frame, text="⏱️ Intervalo entre cliques:", bg=self.colors['card'],
                 fg=self.colors['fg'], font=('Arial', 10, 'bold')).pack(anchor='w', padx=15, pady=(10, 5))
        
        scale_frame = tk.Frame(control_frame, bg=self.colors['card'])
        scale_frame.pack(fill='x', padx=15, pady=(0, 10))
        
        tk.Scale(scale_frame, from_=0.01, to=5.0, resolution=0.01, variable=self.click_delay,
                 orient='horizontal', bg=self.colors['card'], fg=self.colors['fg'],
                 troughcolor=self.colors['bg'], activebackground=self.colors['accent'],
                 highlightthickness=0, bd=0).pack(fill='x')

        # Botões de controle
        tk.Button(frame, text="▶️ Iniciar Autoclicker", command=self.start_clicking,
                  bg=self.colors['success'], fg='white',
                  font=('Arial', 12, 'bold'),
                  relief='flat', bd=0, highlightthickness=0,
                  pady=10).pack(fill='x', pady=(20, 5), padx=5)

        tk.Button(frame, text="⏹️ Parar Autoclicker", command=self.stop_clicking,
                  bg=self.colors['danger'], fg='white',
                  font=('Arial', 12, 'bold'),
                  relief='flat', bd=0, highlightthickness=0,
                  pady=10).pack(fill='x', padx=5)

        # Status
        self.clicks_label = tk.Label(frame, text="Cliques realizados: 0",
                                     fg=self.colors['fg'], bg=self.colors['bg'],
                                     font=('Arial', 10))
        self.clicks_label.pack(pady=10)
        
        # Status das teclas
        self.hotkey_status = tk.Label(frame, 
                                      text=f"📌 Teclas ativas: {self.start_key.get()} (iniciar) | {self.stop_key.get()} (parar)",
                                      fg=self.colors['accent'], bg=self.colors['bg'],
                                      font=('Arial', 8))
        self.hotkey_status.pack(pady=5)

    def capture_start_key(self):
        if self.capturing_start_key or self.capturing_stop_key:
            return
            
        self.capturing_start_key = True
        self.start_key_label.config(text="Pressione...", fg=self.colors['warning'])
        
        def capture_key():
            try:
                # Desabilita hotkeys temporariamente
                keyboard.unhook_all()
                
                # Captura a próxima tecla pressionada
                event = keyboard.read_event()
                while event.event_type != keyboard.KEY_DOWN:
                    event = keyboard.read_event()
                
                new_key = event.name.upper()
                
                # Validação da tecla
                if new_key in ['ESC', 'ESCAPE']:
                    self.start_key_label.config(text=self.start_key.get(), fg=self.colors['success'])
                    self.capturing_start_key = False
                    self.setup_hotkeys()
                    return
                
                # Atualiza a tecla
                self.start_key.set(new_key)
                self.start_key_label.config(text=new_key, fg=self.colors['success'])
                self.update_hotkey_status()
                
                # Reabilita hotkeys
                self.setup_hotkeys()
                
            except Exception as e:
                print(f"Erro ao capturar tecla: {e}")
                self.start_key_label.config(text=self.start_key.get(), fg=self.colors['success'])
            
            self.capturing_start_key = False

        threading.Thread(target=capture_key, daemon=True).start()

    def capture_stop_key(self):
        if self.capturing_start_key or self.capturing_stop_key:
            return
            
        self.capturing_stop_key = True
        self.stop_key_label.config(text="Pressione...", fg=self.colors['warning'])
        
        def capture_key():
            try:
                # Desabilita hotkeys temporariamente
                keyboard.unhook_all()
                
                # Captura a próxima tecla pressionada
                event = keyboard.read_event()
                while event.event_type != keyboard.KEY_DOWN:
                    event = keyboard.read_event()
                
                new_key = event.name.upper()
                
                # Validação da tecla
                if new_key in ['ESC', 'ESCAPE']:
                    self.stop_key_label.config(text=self.stop_key.get(), fg=self.colors['danger'])
                    self.capturing_stop_key = False
                    self.setup_hotkeys()
                    return
                
                # Atualiza a tecla
                self.stop_key.set(new_key)
                self.stop_key_label.config(text=new_key, fg=self.colors['danger'])
                self.update_hotkey_status()
                
                # Reabilita hotkeys
                self.setup_hotkeys()
                
            except Exception as e:
                print(f"Erro ao capturar tecla: {e}")
                self.stop_key_label.config(text=self.stop_key.get(), fg=self.colors['danger'])
            
            self.capturing_stop_key = False

        threading.Thread(target=capture_key, daemon=True).start()

    def update_hotkey_status(self):
        self.hotkey_status.config(
            text=f"📌 Teclas ativas: {self.start_key.get()} (iniciar) | {self.stop_key.get()} (parar)"
        )

    def on_position_mode_change(self):
        mode = self.position_mode.get()
        if mode == "follow":
            self.pos_button.config(state="disabled")
            self.set_follow_mode()
        else:
            self.pos_button.config(state="normal")
            self.follow_mouse.set(False)
            self.click_position = None
            self.position_label.config(text="Posição: Não definida", fg=self.colors['danger'])

    def set_position(self):
        mode = self.position_mode.get()
        if mode == "timer":
            self.set_position_timer()
        elif mode == "click":
            self.set_position_click()

    def set_position_timer(self):
        self.pos_button.config(state="disabled")

        def countdown():
            for i in range(5, 0, -1):
                self.position_label.config(text=f"⏱️ Aguardando... {i}s", fg=self.colors['warning'])
                self.root.update()
                time.sleep(1)
            pos = pyautogui.position()
            self.click_position = pos
            self.position_label.config(text=f"✅ Posição: ({pos.x}, {pos.y})", fg=self.colors['success'])
            self.pos_button.config(state="normal")

        threading.Thread(target=countdown, daemon=True).start()

    def set_position_click(self):
        self.pos_button.config(state="disabled")
        self.position_label.config(text="🖱️ Clique com o mouse em qualquer lugar...",
                                   fg=self.colors['warning'])

        def wait_for_click():
            self.root.iconify()
            time.sleep(0.5)
            pos = []

            def on_click(x, y, button, pressed):
                if pressed:
                    pos.append((x, y))
                    return False

            with mouse.Listener(on_click=on_click) as listener:
                listener.join()

            self.root.deiconify()
            if pos:
                self.click_position = pyautogui.Point(pos[0][0], pos[0][1])
                self.position_label.config(text=f"✅ Posição: {pos[0]}", fg=self.colors['success'])
            else:
                self.position_label.config(text="❌ Erro ao capturar clique", fg=self.colors['danger'])

            self.pos_button.config(state="normal")

        threading.Thread(target=wait_for_click, daemon=True).start()

    def set_follow_mode(self):
        self.click_position = "follow"
        self.position_label.config(text="🎯 Modo: Seguindo cursor", fg=self.colors['success'])

    def setup_hotkeys(self):
        try:
            keyboard.unhook_all()
            keyboard.add_hotkey(self.start_key.get().lower(), self.start_clicking)
            keyboard.add_hotkey(self.stop_key.get().lower(), self.stop_clicking)
        except Exception as e:
            print(f"Erro ao configurar hotkeys: {e}")

    def start_clicking(self):
        if self.clicking:
            return
        if not self.click_position:
            messagebox.showwarning("⚠️ Aviso", "Defina uma posição primeiro!")
            return
        self.clicking = True
        self.click_count.set(0)
        threading.Thread(target=self._click_loop, daemon=True).start()

    def stop_clicking(self):
        self.clicking = False

    def _click_loop(self):
        while self.clicking:
            try:
                if self.click_position == "follow":
                    pos = pyautogui.position()
                else:
                    pos = self.click_position
                pyautogui.click(pos.x, pos.y, button=self.click_type.get())
                self.click_count.set(self.click_count.get() + 1)
                self.clicks_label.config(text=f"Cliques realizados: {self.click_count.get()}")
                time.sleep(self.click_delay.get())
            except Exception as e:
                print(f"Erro: {e}")
                self.stop_clicking()
                break

def main():
    root = tk.Tk()
    app = AutoClickerGUI(root)

    def on_close():
        app.clicking = False
        keyboard.unhook_all()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_close)
    root.mainloop()

if __name__ == "__main__":
    print("🖱️ OzAutoClickerV3 - Custom Keys Edition")
    print("Dependências: pip install pyautogui keyboard pynput")
    print("💡 Pressione ESC durante a captura para cancelar")
    main()