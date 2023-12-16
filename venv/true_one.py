import tkinter as tk
from tkinter import ttk
import random
from collections import deque
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import math

class SistemaControl(tk.Tk):
    def __init__(self):
        super().__init__()

        self.aire_encendido = False

        self.title("Simulación de Control de Temperatura")
        self.geometry("800x600")

        canvas = tk.Canvas(self)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        canvas.configure(yscrollcommand=scrollbar.set)

        frame = ttk.Frame(canvas)
        canvas.create_window((0, 0), window=frame, anchor="nw")

        self.figura = Figure(figsize=(5, 4), dpi=100)
        self.grafico = self.figura.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figura, master=frame)
        self.canvas.get_tk_widget().grid(row=0, column=0, columnspan=3, rowspan=8)

        ttk.Label(frame, text="Temperatura actual:").grid(row=0, column=3, pady=10)
        self.temperatura_var = tk.StringVar(value= "30.0 °C")
        ttk.Entry(frame, textvariable=self.temperatura_var, state="readonly").grid(row=0, column=4, pady=10)

        # ttk.Label(frame, text="Humedad actual:").grid(row=1, column=3, pady=10)
        # self.humedad_var = tk.StringVar(value= "50.0 %")
        # ttk.Entry(frame, textvariable=self.humedad_var, state="readonly").grid(row=1, column=4, pady=10)

        ttk.Label(frame, text="Rango de Temperatura (min-max):").grid(row=2, column=3, pady=10)
        self.temperatura_rango_var = tk.StringVar(value="20-24")
        ttk.Entry(frame, textvariable=self.temperatura_rango_var).grid(row=2, column=4, pady=10)

        # ttk.Label(frame, text="Rango de Humedad (min-max):").grid(row=3, column=3, pady=10)
        # self.humedad_rango_var = tk.StringVar(value="60-70")
        # ttk.Entry(frame, textvariable=self.humedad_rango_var).grid(row=3, column=4, pady=10)

        ttk.Label(frame, text="Constante Proporcional (Kp):").grid(row=4, column=3, pady=10)
        self.kp_var = tk.DoubleVar(value=0.1)
        ttk.Entry(frame, textvariable=self.kp_var).grid(row=4, column=4, pady=10)

        ttk.Label(frame, text="Constante Derivativa (Kd):").grid(row=5, column=3, pady=10)
        self.kd_var = tk.DoubleVar(value=0.1)
        ttk.Entry(frame, textvariable=self.kd_var).grid(row=5, column=4, pady=10)

        ttk.Label(frame, text="Probabilidad de Perturbación:").grid(row=6, column=3, pady=10)
        self.perturbacion_prob_var = tk.DoubleVar(value=0.1)
        ttk.Entry(frame, textvariable=self.perturbacion_prob_var).grid(row=6, column=4, pady=10)

        ttk.Label(frame, text="Valores de Ambiente:").grid(row=7, column=3, pady=10)

        ttk.Label(frame, text="Temperatura Ambiente:").grid(row=8, column=3, pady=10)
        self.temperatura_ambiente_var = tk.DoubleVar(value=30)
        ttk.Entry(frame, textvariable=self.temperatura_ambiente_var).grid(row=8, column=4, pady=10)

        # ttk.Label(frame, text="Humedad Inicial:").grid(row=9, column=3, pady=10)
        # self.humedad_ambiente_var = tk.DoubleVar(value=60)
        # ttk.Entry(frame, textvariable=self.humedad_ambiente_var).grid(row=9, column=4, pady=10)


        self.estado_label = ttk.Label(frame, text="Estado: Esperando actualización")
        self.estado_label.grid(row=11, column=0, columnspan=5, pady=10)

        self.valores_anteriores = {"temperatura": float(self.temperatura_var.get()[:-2])}
        self.errores_anteriores = {"temperatura": 0}
        self.tiempo = 0
        self.datos_temperatura = deque(maxlen=20)
        self.datos_humedad = deque(maxlen=20)
        self.actualizar_cada_segundo()

    def actualizar_cada_segundo(self):
        temperatura_actual = float(self.temperatura_var.get()[:-2])
        # humedad_actual = float(self.humedad_var.get()[:-2])

        print(temperatura_actual)
        # print(humedad_actual)

        if random.random() < self.perturbacion_prob_var.get():
            temperatura_actual += random.uniform(0, 1)
            # humedad_actual += random.uniform(0, 1)

        self.datos_temperatura.append(temperatura_actual)
        # self.datos_humedad.append(humedad_actual)

        self.grafico.clear()
        self.grafico.plot(range(self.tiempo - len(self.datos_temperatura) + 1, self.tiempo + 1), self.datos_temperatura, 'b-', label='Temperatura actual')
        # self.grafico.plot(range(self.tiempo - len(self.datos_humedad) + 1, self.tiempo + 1), self.datos_humedad, 'r-', label='Humedad actual')

        temperatura_rango = self.obtener_rango(self.temperatura_rango_var.get())
        # humedad_rango = self.obtener_rango(self.humedad_rango_var.get())
        self.grafico.axhline(y=temperatura_rango[0], color='r', linestyle='--', label='Temp Min')
        self.grafico.axhline(y=temperatura_rango[1], color='r', linestyle='--', label='Temp Max')
        # self.grafico.axhline(y=humedad_rango[0], color='g', linestyle='--', label='Hum Min')
        # self.grafico.axhline(y=humedad_rango[1], color='g', linestyle='--', label='Hum Max')

        self.grafico.legend()
        self.grafico.set_xlabel('Tiempo')
        self.grafico.set_ylabel('Valor')
        self.canvas.draw()

        kp = self.kp_var.get()
        kd = self.kd_var.get()

        error_temperatura = temperatura_actual - ((temperatura_rango[0] + temperatura_rango[1]) / 2)
        # error_humedad = humedad_actual - ((humedad_rango[0] + humedad_rango[1]) / 2)

        derivada_error_temperatura = error_temperatura - self.errores_anteriores["temperatura"]
        # derivada_error_humedad = error_humedad - self.errores_anteriores["humedad"]

        control_temperatura = kp * error_temperatura + kd * derivada_error_temperatura
        # control_humedad = kp * error_humedad + kd * derivada_error_humedad

        temperatura_ambiente = self.temperatura_ambiente_var.get()

        if temperatura_actual > temperatura_rango[1]:
            self.estado_label.config(text="Estado: Aire Acondicionado encendido")
            self.aire_encendido = True

        if control_temperatura < 0 or temperatura_actual < temperatura_rango[0]:
            self.estado_label.config(text="Estado: Aire Acondicionado apagado")
            self.aire_encendido = False

        if self.aire_encendido:
            temperatura_actual -= control_temperatura
        
        if self.aire_encendido == False:
            temperatura_actual = temperatura_ambiente + (temperatura_actual - temperatura_ambiente) * math.exp(-0.001)

            

        self.errores_anteriores["temperatura"] = error_temperatura
        # self.errores_anteriores["humedad"] = error_humedad

        self.temperatura_var.set(f"{temperatura_actual:.2f} °C")
        # self.humedad_var.set(f"{humedad_actual:.2f} %")

        self.tiempo += 1
        self.after(500, self.actualizar_cada_segundo)

    def obtener_rango(self, rango_str):
        try:
            min_val, max_val = map(float, rango_str.split("-"))
            return min_val, max_val
        except ValueError:
            return 0, 0


if __name__ == "__main__":
    app = SistemaControl()
    app.mainloop()
