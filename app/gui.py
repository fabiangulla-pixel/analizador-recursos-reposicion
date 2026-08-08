"""
gui.py
Ventana principal de la aplicación. Construida con tkinter.
Diseño pensado para usuarios no técnicos.
El análisis se ejecuta en un hilo separado para no congelar la interfaz.
"""

import os
import sys
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk

from app.pipeline import ejecutar_analisis

# ── Colores y fuentes ────────────────────────────────────────────────────────
COLOR_FONDO = "#F5F5F5"
COLOR_ACENTO = "#2C5F8A"
COLOR_BOTON = "#2C5F8A"
COLOR_BOTON_TEXTO = "#FFFFFF"
COLOR_EXITO = "#2E7D32"
COLOR_ERROR = "#C62828"
COLOR_ADVERTENCIA = "#F57F17"
FUENTE_TITULO = ("Segoe UI", 14, "bold")
FUENTE_LABEL = ("Segoe UI", 10)
FUENTE_BOTON = ("Segoe UI", 10, "bold")
FUENTE_LOG = ("Consolas", 9)


class AplicacionRecursos(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Analizador de Recursos de Reposición")
        self.geometry("780x680")
        self.resizable(True, True)
        self.configure(bg=COLOR_FONDO)
        self.minsize(680, 580)

        self._ruta_base: str | None = None
        self._carpeta_recursos: str | None = None
        self._carpeta_salida: str | None = None
        self._analizando = False

        self._construir_ui()

    # ── Construcción de la UI ────────────────────────────────────────────────

    def _construir_ui(self):
        # Título
        frame_titulo = tk.Frame(self, bg=COLOR_ACENTO)
        frame_titulo.pack(fill="x")
        tk.Label(
            frame_titulo,
            text="Analizador de Recursos de Reposición",
            font=FUENTE_TITULO,
            bg=COLOR_ACENTO,
            fg="white",
            pady=12,
        ).pack()

        # Contenedor principal
        main = tk.Frame(self, bg=COLOR_FONDO, padx=20, pady=15)
        main.pack(fill="both", expand=True)

        # ── Sección de entradas ──
        frame_inputs = tk.LabelFrame(
            main,
            text="  Archivos de entrada  ",
            bg=COLOR_FONDO,
            font=FUENTE_LABEL,
            fg=COLOR_ACENTO,
            padx=10,
            pady=10,
        )
        frame_inputs.pack(fill="x", pady=(0, 10))

        self._campo_base, self._btn_base = self._fila_selector(
            frame_inputs,
            etiqueta="Resolución sancionatoria base:",
            tooltip="Seleccione el archivo PDF, DOCX o TXT de la resolución base.",
            comando=self._seleccionar_base,
            fila=0,
        )
        self._campo_recursos, self._btn_recursos = self._fila_selector(
            frame_inputs,
            etiqueta="Carpeta de recursos de reposición:",
            tooltip="Seleccione la carpeta que contiene los recursos (PDF, DOCX, TXT).",
            comando=self._seleccionar_carpeta_recursos,
            fila=1,
            es_carpeta=True,
        )
        self._campo_salida, self._btn_salida = self._fila_selector(
            frame_inputs,
            etiqueta="Carpeta de resultados:",
            tooltip="Seleccione la carpeta donde se guardarán los archivos generados.",
            comando=self._seleccionar_carpeta_salida,
            fila=2,
            es_carpeta=True,
        )

        # ── Barra de progreso ──
        frame_progreso = tk.Frame(main, bg=COLOR_FONDO)
        frame_progreso.pack(fill="x", pady=(5, 0))

        self._lbl_estado = tk.Label(
            frame_progreso,
            text="Listo. Seleccione los archivos y presione Ejecutar análisis.",
            font=FUENTE_LABEL,
            bg=COLOR_FONDO,
            fg="#555555",
            anchor="w",
        )
        self._lbl_estado.pack(fill="x")

        self._progresbar = ttk.Progressbar(
            frame_progreso, orient="horizontal", mode="determinate", length=100
        )
        self._progresbar.pack(fill="x", pady=(4, 0))
        self._progresbar["value"] = 0

        # ── Botones ──
        frame_botones = tk.Frame(main, bg=COLOR_FONDO)
        frame_botones.pack(fill="x", pady=12)

        self._btn_ejecutar = tk.Button(
            frame_botones,
            text="▶  Ejecutar análisis",
            font=FUENTE_BOTON,
            bg=COLOR_BOTON,
            fg=COLOR_BOTON_TEXTO,
            activebackground="#1A4A6E",
            activeforeground="white",
            relief="flat",
            padx=18,
            pady=8,
            cursor="hand2",
            command=self._iniciar_analisis,
        )
        self._btn_ejecutar.pack(side="left", padx=(0, 10))

        self._btn_abrir = tk.Button(
            frame_botones,
            text="📂  Abrir resultados",
            font=FUENTE_BOTON,
            bg="#555555",
            fg="white",
            activebackground="#333333",
            activeforeground="white",
            relief="flat",
            padx=18,
            pady=8,
            cursor="hand2",
            state="disabled",
            command=self._abrir_carpeta_salida,
        )
        self._btn_abrir.pack(side="left")

        # ── Log / estado detallado ──
        frame_log = tk.LabelFrame(
            main,
            text="  Registro de actividad  ",
            bg=COLOR_FONDO,
            font=FUENTE_LABEL,
            fg=COLOR_ACENTO,
            padx=10,
            pady=8,
        )
        frame_log.pack(fill="both", expand=True)

        self._area_log = scrolledtext.ScrolledText(
            frame_log,
            font=FUENTE_LOG,
            bg="#1E1E1E",
            fg="#D4D4D4",
            insertbackground="white",
            relief="flat",
            state="disabled",
            wrap="word",
        )
        self._area_log.pack(fill="both", expand=True)
        self._area_log.tag_config("error", foreground="#FF6B6B")
        self._area_log.tag_config("ok", foreground="#69DB7C")
        self._area_log.tag_config("info", foreground="#74C0FC")

    def _fila_selector(self, parent, etiqueta, tooltip, comando, fila, es_carpeta=False):
        """Crea una fila de: etiqueta + campo de texto + botón seleccionar."""
        lbl = tk.Label(parent, text=etiqueta, font=FUENTE_LABEL, bg=COLOR_FONDO, anchor="w")
        lbl.grid(row=fila * 2, column=0, columnspan=3, sticky="w", pady=(6, 0))

        campo = tk.Entry(parent, font=FUENTE_LABEL, relief="solid", bd=1, fg="#333333")
        campo.grid(row=fila * 2 + 1, column=0, sticky="ew", padx=(0, 6), pady=(2, 0))

        icono = "📁" if es_carpeta else "📄"
        btn = tk.Button(
            parent,
            text=f"{icono} Seleccionar",
            font=FUENTE_LABEL,
            bg="#E0E0E0",
            fg="#333333",
            relief="flat",
            padx=10,
            pady=4,
            cursor="hand2",
            command=comando,
        )
        btn.grid(row=fila * 2 + 1, column=1, sticky="w", pady=(2, 0))

        parent.columnconfigure(0, weight=1)
        return campo, btn

    # ── Selección de archivos y carpetas ────────────────────────────────────

    def _seleccionar_base(self):
        ruta = filedialog.askopenfilename(
            title="Seleccionar resolución sancionatoria base",
            filetypes=[
                ("Documentos", "*.pdf *.docx *.txt"),
                ("PDF", "*.pdf"),
                ("Word", "*.docx"),
                ("Texto", "*.txt"),
                ("Todos", "*.*"),
            ],
        )
        if ruta:
            self._ruta_base = ruta
            self._set_campo(self._campo_base, ruta)
            self._log(f"Base seleccionada: {os.path.basename(ruta)}", "info")

    def _seleccionar_carpeta_recursos(self):
        carpeta = filedialog.askdirectory(title="Seleccionar carpeta de recursos de reposición")
        if carpeta:
            self._carpeta_recursos = carpeta
            self._set_campo(self._campo_recursos, carpeta)
            self._log(f"Carpeta de recursos: {carpeta}", "info")

    def _seleccionar_carpeta_salida(self):
        carpeta = filedialog.askdirectory(title="Seleccionar carpeta de resultados")
        if carpeta:
            self._carpeta_salida = carpeta
            self._set_campo(self._campo_salida, carpeta)
            self._log(f"Carpeta de salida: {carpeta}", "info")

    # ── Ejecución del análisis ───────────────────────────────────────────────

    def _iniciar_analisis(self):
        if self._analizando:
            return

        # Validaciones básicas
        if not self._ruta_base or not os.path.isfile(self._ruta_base):
            messagebox.showerror("Falta archivo", "Seleccione el archivo de la resolución base.")
            return
        if not self._carpeta_recursos or not os.path.isdir(self._carpeta_recursos):
            messagebox.showerror(
                "Falta carpeta", "Seleccione la carpeta de recursos de reposición."
            )
            return
        if not self._carpeta_salida:
            messagebox.showerror("Falta carpeta", "Seleccione la carpeta de resultados.")
            return

        self._analizando = True
        self._btn_ejecutar.config(state="disabled", text="⏳  Analizando...")
        self._btn_abrir.config(state="disabled")
        self._progresbar["value"] = 0
        self._log("─" * 60)
        self._log("Iniciando análisis...", "info")

        # Ejecutar en hilo separado
        hilo = threading.Thread(target=self._hilo_analisis, daemon=True)
        hilo.start()

    def _hilo_analisis(self):
        resultado = ejecutar_analisis(
            ruta_base=self._ruta_base,
            carpeta_recursos=self._carpeta_recursos,
            carpeta_salida=self._carpeta_salida,
            callback_progreso=self._callback_progreso,
        )
        # Volver al hilo principal para actualizar la UI
        self.after(0, lambda: self._finalizar_analisis(resultado))

    def _callback_progreso(self, mensaje: str, porcentaje: int):
        """Llamado desde el hilo del análisis. Actualiza la GUI de forma segura."""
        self.after(0, lambda m=mensaje, p=porcentaje: self._actualizar_progreso(m, p))

    def _actualizar_progreso(self, mensaje: str, porcentaje: int):
        self._lbl_estado.config(text=mensaje)
        self._progresbar["value"] = porcentaje
        self._log(mensaje, "info")

    def _finalizar_analisis(self, resultado: dict):
        self._analizando = False
        self._btn_ejecutar.config(state="normal", text="▶  Ejecutar análisis")

        if "error" in resultado:
            self._progresbar["value"] = 0
            self._lbl_estado.config(text="Error durante el análisis.", fg=COLOR_ERROR)
            self._log(f"ERROR: {resultado['error']}", "error")
            messagebox.showerror(
                "Error en el análisis",
                f"Ocurrió un error:\n\n{resultado['error']}\n\nRevise el registro de actividad.",
            )
        else:
            self._progresbar["value"] = 100
            self._lbl_estado.config(text="✔ Análisis completado correctamente.", fg=COLOR_EXITO)
            self._log(
                f"✔ Análisis completado: {resultado['total_argumentos']} argumentos, "
                f"{resultado['total_grupos']} grupos.",
                "ok",
            )
            self._btn_abrir.config(state="normal")
            messagebox.showinfo(
                "Análisis completado",
                f"El análisis finalizó correctamente.\n\n"
                f"• Argumentos procesados: {resultado['total_argumentos']}\n"
                f"• Grupos identificados: {resultado['total_grupos']}\n\n"
                f"Resultados guardados en:\n{resultado['carpeta_salida']}",
            )

    # ── Abrir carpeta de resultados ──────────────────────────────────────────

    def _abrir_carpeta_salida(self):
        # macOS necesita su propia rama: `xdg-open` es de freedesktop y no
        # existe ahí, así que la versión anterior abría la carpeta en Windows y
        # en Linux, pero en Mac fallaba en silencio. El comando es `open`.
        if self._carpeta_salida and os.path.isdir(self._carpeta_salida):
            import subprocess

            try:
                if sys.platform == "win32":
                    os.startfile(self._carpeta_salida)
                elif sys.platform == "darwin":
                    subprocess.Popen(["open", self._carpeta_salida])
                else:
                    subprocess.Popen(["xdg-open", self._carpeta_salida])
            except OSError:
                # Un visor ausente no debe tumbar la interfaz: abrir la carpeta
                # es una cortesía al terminar, no el resultado del trabajo.
                pass

    # ── Utilidades de UI ─────────────────────────────────────────────────────

    def _set_campo(self, campo: tk.Entry, valor: str):
        campo.config(state="normal")
        campo.delete(0, "end")
        campo.insert(0, valor)
        campo.config(state="readonly")

    def _log(self, mensaje: str, tag: str = ""):
        self._area_log.config(state="normal")
        if tag:
            self._area_log.insert("end", mensaje + "\n", tag)
        else:
            self._area_log.insert("end", mensaje + "\n")
        self._area_log.see("end")
        self._area_log.config(state="disabled")
