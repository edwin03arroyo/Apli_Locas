import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import time
import threading
import psutil

# Lista de rutas de aplicaciones bloqueadas
blocked_apps = []
is_blocking = False

# ----------------------------- FUNCIONES -----------------------------

def browse_app():
    path = filedialog.askopenfilename(title="Selecciona la aplicación", filetypes=[("Ejecutables", "*.exe")])
    if path:
        app_name = os.path.basename(path)
        blocked_apps.append((app_name, path))
        app_listbox.insert(tk.END, app_name)

def remove_app():
    selected = app_listbox.curselection()
    if selected:
        index = selected[0]
        app_listbox.delete(index)
        del blocked_apps[index]

def format_time(seconds):
    h = seconds // 3600
    m = (seconds % 3600) // 60
    return f"{h:02d}:{m:02d}"

def show_timer(seconds):
    for remaining in range(seconds, 0, -1):
        timer_label.config(text=f"Tiempo restante: {format_time(remaining)}")
        time.sleep(1)
    stop_blocking()

def block_loop(duration_seconds):
    global is_blocking
    is_blocking = True
    # Ocultar ventana principal
    root.withdraw()
    # Mostrar ventana de temporizador
    timer_window.deiconify()

    threading.Thread(target=show_timer, args=(duration_seconds,), daemon=True).start()

    end_time = time.time() + duration_seconds
    while time.time() < end_time and is_blocking:
        for proc in psutil.process_iter(['name', 'exe']):
            try:
                for app_name, app_path in blocked_apps:
                    if proc.info['exe'] and os.path.normcase(proc.info['exe']) == os.path.normcase(app_path):
                        proc.kill()
                        show_warning(app_name)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        time.sleep(2)

def show_warning(app_name):
    warning = tk.Toplevel()
    warning.title("Aplicación bloqueada")
    warning.geometry("400x100")
    warning.attributes('-topmost', True)
    label = tk.Label(warning, text=f"No puedes abrir {app_name} ahora.\nConcéntrate en estudiar 🧠", font=("Arial", 12))
    label.pack(pady=10)
    warning.after(3000, warning.destroy)

def start_blocking():
    if not blocked_apps:
        messagebox.showwarning("Advertencia", "Debes agregar al menos una aplicación.")
        return

    hours = int(hour_var.get())
    minutes = int(minute_var.get())
    total_seconds = (hours * 3600) + (minutes * 60)
    if total_seconds == 0:
        messagebox.showwarning("Advertencia", "El tiempo debe ser mayor que 0.")
        return

    # Desactivar botón cerrar durante el bloqueo
    root.protocol("WM_DELETE_WINDOW", lambda: None)
    threading.Thread(target=block_loop, args=(total_seconds,), daemon=True).start()

def stop_blocking():
    global is_blocking
    is_blocking = False
    timer_window.withdraw()
    root.deiconify()
    root.protocol("WM_DELETE_WINDOW", root.destroy)
    timer_label.config(text="")

# ----------------------------- INTERFAZ PRINCIPAL -----------------------------

root = tk.Tk()
root.title("Bloqueador de Aplicaciones")
root.geometry("400x500")

# Aplicaciones
frame_apps = tk.LabelFrame(root, text="Aplicaciones a bloquear")
frame_apps.pack(padx=10, pady=10, fill="both", expand=True)

app_listbox = tk.Listbox(frame_apps, height=10)
app_listbox.pack(padx=5, pady=5, fill="both", expand=True)

btn_frame = tk.Frame(frame_apps)
btn_frame.pack()

tk.Button(btn_frame, text="Agregar aplicación", command=browse_app).pack(side="left", padx=5)
tk.Button(btn_frame, text="Quitar aplicación", command=remove_app).pack(side="left", padx=5)

# Tiempo
frame_time = tk.LabelFrame(root, text="Duración del bloqueo")
frame_time.pack(padx=10, pady=10, fill="x")

hour_var = tk.StringVar(value="0")
minute_var = tk.StringVar(value="30")

ttk.Label(frame_time, text="Horas:").grid(row=0, column=0, padx=5, pady=5)
ttk.Spinbox(frame_time, from_=0, to=12, width=5, textvariable=hour_var).grid(row=0, column=1)

ttk.Label(frame_time, text="Minutos:").grid(row=0, column=2, padx=5, pady=5)
ttk.Spinbox(frame_time, from_=0, to=59, width=5, textvariable=minute_var).grid(row=0, column=3)

# Botón iniciar
tk.Button(root, text="Iniciar", command=start_blocking, bg="green", fg="white").pack(pady=20)

# ----------------------------- VENTANA TEMPORIZADOR -----------------------------

timer_window = tk.Toplevel()
timer_window.title("Bloqueo activo")
timer_window.geometry("300x100")
timer_window.withdraw()
timer_window.protocol("WM_DELETE_WINDOW", lambda: None)

timer_label = tk.Label(timer_window, text="", font=("Arial", 16))
timer_label.pack(pady=20)

# ----------------------------- INICIAR -----------------------------

root.mainloop()
