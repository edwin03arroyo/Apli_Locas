import tkinter as tk
from tkinter import filedialog, messagebox
import os
import time
import threading
import psutil

# Listas para almacenar rutas y nombres de apps bloqueadas
rutas_bloqueadas = []
nombres_bloqueados = []
mensaje_mostrado_por_pid = set()  # Para evitar mensajes repetidos por proceso

def seleccionar_aplicacion():
    ruta = filedialog.askopenfilename(title="Selecciona la aplicación a bloquear", filetypes=[("Ejecutables", "*.exe")])
    if ruta and ruta not in rutas_bloqueadas:
        rutas_bloqueadas.append(ruta)
        nombre = os.path.basename(ruta).lower()
        nombres_bloqueados.append(nombre)
        lista_apps.insert(tk.END, os.path.basename(ruta))

def actualizar_temporizador(tiempo_restante_seg):
    global ventana_temporizador
    if tiempo_restante_seg < 0:
        messagebox.showinfo("Bloqueo terminado", "¡Ya puedes usar tus aplicaciones!")
        ventana_temporizador.destroy()
        root.destroy()
        return
    minutos, segundos = divmod(tiempo_restante_seg, 60)
    tiempo_formato = f"{minutos:02d}:{segundos:02d}"
    label_tiempo.config(text=tiempo_formato)
    ventana_temporizador.after(1000, actualizar_temporizador, tiempo_restante_seg - 1)

def monitorear_y_bloquear(tiempo_segundos):
    tiempo_fin = time.time() + tiempo_segundos
    while time.time() < tiempo_fin:
        for proc in psutil.process_iter(['pid', 'name', 'exe']):
            try:
                nombre_proc = proc.info['name']
                pid_proc = proc.info['pid']
                if nombre_proc and nombre_proc.lower() in nombres_bloqueados:
                    proc.kill()
                    # Mostrar mensaje solo una vez por proceso
                    if pid_proc not in mensaje_mostrado_por_pid:
                        mensaje_mostrado_por_pid.add(pid_proc)
                        root.after(0, lambda: messagebox.showwarning(
                            "Aplicación bloqueada",
                            "Por ahora no puedes abrir este aplicativo, concéntrate en estudiar."))
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        time.sleep(2)
    # Cuando termine el bloqueo cerramos todo
    root.after(0, lambda: (ventana_temporizador.destroy(), root.destroy()))

def iniciar_bloqueo():
    global ventana_temporizador
    try:
        horas = int(spin_horas.get())
        minutos = int(spin_minutos.get())
        if horas == 0 and minutos == 0:
            raise ValueError("El tiempo debe ser mayor a 0.")
        if not rutas_bloqueadas:
            messagebox.showerror("Error", "Debes seleccionar al menos una aplicación para bloquear.")
            return
        tiempo_total = horas * 3600 + minutos * 60
    except ValueError as e:
        messagebox.showerror("Error", str(e))
        return

    # Desactivar botones y ocultar ventana principal
    btn_buscar.config(state="disabled")
    spin_horas.config(state="disabled")
    spin_minutos.config(state="disabled")
    btn_iniciar.config(state="disabled")
    root.withdraw()  # Oculta la ventana principal

    # Crear ventana temporizador
    ventana_temporizador = tk.Toplevel()
    ventana_temporizador.title("Bloqueo en curso")
    ventana_temporizador.geometry("250x100")
    ventana_temporizador.protocol("WM_DELETE_WINDOW", lambda: None)  # No se puede cerrar
    label_info = tk.Label(ventana_temporizador, text="Tiempo restante:", font=("Arial", 12))
    label_info.pack(pady=5)
    global label_tiempo
    label_tiempo = tk.Label(ventana_temporizador, text="", font=("Arial", 24), fg="red")
    label_tiempo.pack()

    actualizar_temporizador(tiempo_total)

    # Iniciar monitoreo y bloqueo en hilo separado
    hilo_bloqueo = threading.Thread(target=monitorear_y_bloquear, args=(tiempo_total,), daemon=True)
    hilo_bloqueo.start()

# Interfaz principal
root = tk.Tk()
root.title("Bloqueador de Aplicaciones")
root.geometry("400x450")
root.protocol("WM_DELETE_WINDOW", lambda: None)  # Desactivar cerrar ventana

tk.Label(root, text="Selecciona las aplicaciones que quieres bloquear:").pack(pady=10)

btn_buscar = tk.Button(root, text="Buscar aplicación", command=seleccionar_aplicacion)
btn_buscar.pack()

lista_apps = tk.Listbox(root, height=6, width=45)
lista_apps.pack(pady=10)

tk.Label(root, text="Duración del bloqueo:").pack(pady=5)

frame_tiempo = tk.Frame(root)
frame_tiempo.pack()

tk.Label(frame_tiempo, text="Horas:").grid(row=0, column=0)
spin_horas = tk.Spinbox(frame_tiempo, from_=0, to=12, width=5)
spin_horas.grid(row=0, column=1, padx=5)

tk.Label(frame_tiempo, text="Minutos:").grid(row=0, column=2)
spin_minutos = tk.Spinbox(frame_tiempo, from_=0, to=59, width=5)
spin_minutos.grid(row=0, column=3, padx=5)

btn_iniciar = tk.Button(root, text="Iniciar Bloqueo", bg="red", fg="white", command=iniciar_bloqueo)
btn_iniciar.pack(pady=20)

root.mainloop()
