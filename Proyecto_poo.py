#!/usr/bin/python3
# -*- coding: utf-8 -*-

import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox as mssg
from tkinter import filedialog
from datetime import datetime
from db_handler import DatabaseHandler  # Importa el módulo para manejo de la base de datos
import csv
import re  # Para validaciones con expresiones regulares

# --------------------------
# Funciones para el placeholder
# --------------------------
def on_entry_click(event, widget, placeholder):
    """
    Función que se ejecuta al hacer clic en un widget Entry.
    Si el contenido es igual al placeholder, se borra y se cambia el color a negro para permitir la entrada.
    """
    if widget.get() == placeholder:
        widget.delete(0, "end")
        widget.config(foreground="black")

def on_focusout(event, widget, placeholder):
    """
    Función que se ejecuta cuando el widget Entry pierde el foco.
    Si el campo queda vacío, se inserta nuevamente el placeholder y se configura el color en gris.
    """
    if widget.get().strip() == "":
        widget.insert(0, placeholder)
        widget.config(foreground="gray")

# --------------------------
# Clase para Tooltips
# --------------------------
class CreateToolTip(object):
    """
    Crea un tooltip (mensaje emergente) para un widget dado.
    """
    def __init__(self, widget, text='widget info'):
        # Inicializa el tooltip asociando el widget y el texto a mostrar.
        self.widget = widget
        self.text = text
        self.waittime = 500     # Tiempo de espera en milisegundos antes de mostrar el tooltip
        self.wraplength = 180   # Ancho máximo en píxeles para envolver el texto
        # Asocia eventos del widget para mostrar y ocultar el tooltip
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)
        self.widget.bind("<ButtonPress>", self.leave)
        self.id = None  # Identificador del evento programado
        self.tw = None  # Referencia a la ventana del tooltip

    def enter(self, event=None):
        # Al entrar el cursor en el widget, se programa la aparición del tooltip.
        self.schedule()

    def leave(self, event=None):
        # Al salir el cursor, se cancela la programación y se oculta el tooltip.
        self.unschedule()
        self.hidetip()

    def schedule(self):
        # Programa la aparición del tooltip después de un retardo definido.
        self.unschedule()  # Cancela cualquier programación previa
        self.id = self.widget.after(self.waittime, self.showtip)

    def unschedule(self):
        # Cancela la programación del tooltip si existe.
        id_ = self.id
        self.id = None
        if id_:
            self.widget.after_cancel(id_)

    def showtip(self, event=None):
        """
        Muestra el tooltip en una ventana toplevel sin bordes.
        Calcula la posición en pantalla basándose en el widget.
        """
        x, y, cx, cy = self.widget.bbox("insert")  # Obtiene la posición del cursor en el widget
        x += self.widget.winfo_rootx() + 25  # Calcula la posición X absoluta
        y += self.widget.winfo_rooty() + 20  # Calcula la posición Y absoluta
        self.tw = tk.Toplevel(self.widget)  # Crea la ventana toplevel para el tooltip
        self.tw.wm_overrideredirect(True)  # Elimina los bordes de la ventana
        self.tw.wm_geometry("+%d+%d" % (x, y))  # Posiciona la ventana en pantalla
        # Crea una etiqueta en la ventana del tooltip con formato específico
        label = tk.Label(self.tw, text=self.text, justify='left',
                         background="#ffffe0", relief='solid', borderwidth=1,
                         wraplength=self.wraplength)
        label.pack(ipadx=1)

    def hidetip(self):
        # Oculta y destruye la ventana del tooltip si está visible.
        if self.tw:
            self.tw.destroy()
        self.tw = None

# --------------------------
# Clase Principal: Participantes
# --------------------------
class Participantes:
    # Ruta a la base de datos SQLite
    db_path = r"C:/Users/jorge/OneDrive/Documentos/Proyecto Poo/Participantes.db"
    # Instancia del manejador de la base de datos
    db_handler = DatabaseHandler(db_path)

    def __init__(self, master=None):
        """
        Constructor de la clase.
        Inicializa la ventana principal, configura la interfaz y crea los componentes de la aplicación.
        """
        # Crea la ventana principal o una ventana secundaria
        self.win = tk.Tk() if master is None else tk.Toplevel()
        self.win.title("Conferencia MACSS y la Ingeniería de Requerimientos")
        self.win.configure(background="#E8F6F3")
        self.win.geometry("1024x480")
        self.win.resizable(True, True)
        
        # Configuración del grid principal de la ventana
        self.win.grid_rowconfigure(0, weight=1)
        self.win.grid_rowconfigure(1, weight=0)
        self.win.grid_rowconfigure(2, weight=0)  # Espacio para la barra de estado
        self.win.grid_columnconfigure(0, weight=1)
        
        # Creación del marco principal que contiene el formulario y el TreeView
        self.main_frame = tk.Frame(self.win, bg="#E8F6F3")
        self.main_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(1, weight=2)
        
        # --- Sección del Formulario (lado izquierdo) ---
        self.form_frame = tk.Frame(self.main_frame, bg="#E8F6F3")
        self.form_frame.grid(row=0, column=0, sticky="nsew", padx=(0,10))
        
        # LabelFrame que agrupa los campos de entrada
        self.lblfrm_Datos = tk.LabelFrame(self.form_frame, text=" Inscripción ", font=("Helvetica", 13, "bold"), bg="#E8F6F3")
        self.lblfrm_Datos.pack(fill="both", expand=True)
        
        # Campo Identificación (solo números y máximo 15 caracteres)
        self.lblId = ttk.Label(self.lblfrm_Datos, text="Identificación", width=12)
        self.lblId.grid(column=0, row=0, padx=5, pady=10, sticky="w")
        vcmd = (self.win.register(self.validar_identificacion), '%P')  # Registra la función de validación
        self.entryId = tk.Entry(self.lblfrm_Datos, width=30, justify="left", relief="groove",
                                validate="key", validatecommand=vcmd)
        self.entryId.grid(column=1, row=0, padx=5, pady=10, sticky="w")
        CreateToolTip(self.entryId, "Ingrese el ID (máximo 15 caracteres, solo números).")
        
        # Campo Nombre (solo letras)
        self.lblNombre = ttk.Label(self.lblfrm_Datos, text="Nombre", width=12)
        self.lblNombre.grid(column=0, row=1, padx=5, pady=10, sticky="w")
        vcmdNombre = (self.win.register(self.validar_nombre), '%P')
        self.entryNombre = tk.Entry(self.lblfrm_Datos, width=30, justify="left", relief="groove",
                                    validate="key", validatecommand=vcmdNombre)
        self.entryNombre.grid(column=1, row=1, padx=5, pady=10, sticky="w")
        
        # Campo Dirección con placeholder
        placeholder_direccion = "Calle, número, barrio..."
        self.lblDireccion = ttk.Label(self.lblfrm_Datos, text="Dirección", width=12)
        self.lblDireccion.grid(column=0, row=2, padx=5, pady=10, sticky="w")
        self.entryDireccion = tk.Entry(self.lblfrm_Datos, width=30, justify="left", relief="groove", foreground="gray")
        self.entryDireccion.insert(0, placeholder_direccion)  # Inserta el placeholder inicialmente
        self.entryDireccion.bind("<FocusIn>", lambda e: on_entry_click(e, self.entryDireccion, placeholder_direccion))
        self.entryDireccion.bind("<FocusOut>", lambda e: on_focusout(e, self.entryDireccion, placeholder_direccion))
        self.entryDireccion.grid(column=1, row=2, padx=5, pady=10, sticky="w")
        
        # Campo Celular (solo números)
        self.lblCelular = ttk.Label(self.lblfrm_Datos, text="Celular", width=12)
        self.lblCelular.grid(column=0, row=3, padx=5, pady=10, sticky="w")
        vcmdCelular = (self.win.register(self.validar_numeros), '%P')
        self.entryCelular = tk.Entry(self.lblfrm_Datos, width=30, justify="left", relief="groove",
                                     validate="key", validatecommand=vcmdCelular)
        self.entryCelular.grid(column=1, row=3, padx=5, pady=10, sticky="w")
        
        # Campo Entidad (entrada simple sin validación específica)
        self.lblEntidad = ttk.Label(self.lblfrm_Datos, text="Entidad", width=12)
        self.lblEntidad.grid(column=0, row=4, padx=5, pady=10, sticky="w")
        self.entryEntidad = tk.Entry(self.lblfrm_Datos, width=30, justify="left", relief="groove")
        self.entryEntidad.grid(column=1, row=4, padx=5, pady=10, sticky="w")
        
        # Campo Fecha (se valida el formato y que no sea anterior a la fecha actual)
        self.lblFecha = ttk.Label(self.lblfrm_Datos, text="Fecha", width=12)
        self.lblFecha.grid(column=0, row=5, padx=5, pady=10, sticky="w")
        self.entryFecha = tk.Entry(self.lblfrm_Datos, width=30, justify="left", relief="groove")
        self.entryFecha.grid(column=1, row=5, padx=5, pady=10, sticky="w")
        self.entryFecha.bind("<FocusOut>", self.valida_Fecha)
        CreateToolTip(self.entryFecha, "Ingrese la fecha en formato dd/mm/aaaa y que no sea anterior a hoy.")
        
        # Campo Departamento (combobox para seleccionar el departamento)
        self.lblDepartamento = ttk.Label(self.lblfrm_Datos, text="Departamento")
        self.lblDepartamento.grid(column=0, row=6, padx=5, pady=10, sticky="w")
        self.comboDepartamento = ttk.Combobox(self.lblfrm_Datos, state="readonly")
        self.comboDepartamento.grid(column=1, row=6, padx=5, pady=10, sticky="w")
        self.comboDepartamento.bind("<<ComboboxSelected>>", self.actualiza_ciudades)
        
        # Campo Ciudad (combobox que se llena dinámicamente según el departamento seleccionado)
        self.lblCiudad = ttk.Label(self.lblfrm_Datos, text="Ciudad")
        self.lblCiudad.grid(column=0, row=7, padx=5, pady=10, sticky="w")
        self.comboCiudad = ttk.Combobox(self.lblfrm_Datos, state="readonly")
        self.comboCiudad.grid(column=1, row=7, padx=5, pady=10, sticky="w")
        
        # Carga la lista de departamentos desde la base de datos
        self.cargar_Nombre_Departamento()
        
        # --------------------------
        # Sección del TreeView y búsqueda (lado derecho)
        # --------------------------
        self.tree_frame = tk.Frame(self.main_frame, bg="#E8F6F3")
        self.tree_frame.grid(row=0, column=1, sticky="nsew")
        self.tree_frame.grid_rowconfigure(1, weight=1)
        self.tree_frame.grid_columnconfigure(0, weight=1)
        
        # Marco para el campo de búsqueda dinámico
        self.search_frame = tk.Frame(self.tree_frame, bg="#E8F6F3")
        self.search_frame.grid(row=0, column=0, sticky="ew")
        lblBuscar = tk.Label(self.search_frame, text="Buscar:", bg="#E8F6F3", font=("Helvetica", 10))
        lblBuscar.pack(side="left", padx=5, pady=5)
        self.entryBuscar = tk.Entry(self.search_frame, width=30)
        self.entryBuscar.pack(side="left", padx=5, pady=5)
        self.entryBuscar.bind("<KeyRelease>", self.filtra_registros)
        
        # Configuración del TreeView para mostrar los registros
        self.style = ttk.Style()
        self.style.configure("estilo.Treeview",
                             highlightthickness=0, bd=0,
                             background='#F5F5F5',
                             font=('Calibri Light', 10))
        self.style.configure("estilo.Treeview.Heading",
                             background='#AEDFF7',
                             font=('Calibri Light', 10, 'bold')) 
        self.style.layout("estilo.Treeview",
                          [('estilo.Treeview.treearea', {'sticky': 'nswe'})])
        
        self.treeDatos = ttk.Treeview(self.tree_frame, height=10, style="estilo.Treeview")
        self.treeDatos.grid(row=1, column=0, sticky="nsew")
        self.treeDatos["columns"] = ("Nombre", "Dirección", "Celular", "Entidad", "Fecha", "Ciudad", "Departamento")
        self.treeDatos.column('#0', anchor="w", stretch=True, width=40)
        self.treeDatos.column('Nombre', anchor="w", stretch=True, width=100)
        self.treeDatos.column('Dirección', anchor="w", stretch=True, width=100)
        self.treeDatos.column('Celular', anchor="w", stretch=True, width=80)
        self.treeDatos.column('Entidad', anchor="w", stretch=True, width=100)
        self.treeDatos.column('Fecha', anchor="w", stretch=True, width=80)
        self.treeDatos.column('Ciudad', anchor="w", stretch=True, width=80)
        self.treeDatos.column('Departamento', anchor="w", stretch=True, width=100)
        self.treeDatos.heading('#0', text='Id')
        self.treeDatos.heading('Nombre', text='Nombre')
        self.treeDatos.heading('Dirección', text='Dirección')
        self.treeDatos.heading('Celular', text='Celular')
        self.treeDatos.heading('Entidad', text='Entidad')
        self.treeDatos.heading('Fecha', text='Fecha')
        self.treeDatos.heading('Ciudad', text='Ciudad')
        self.treeDatos.heading('Departamento', text='Departamento')
        
        # Agrega una barra de desplazamiento vertical al TreeView
        self.scrollbar = ttk.Scrollbar(self.tree_frame, orient='vertical', command=self.treeDatos.yview)
        self.treeDatos.configure(yscroll=self.scrollbar.set)
        self.scrollbar.grid(row=1, column=1, sticky="ns")
        
        # --------------------------
        # Sección de Botones (parte inferior)
        # --------------------------
        self.button_frame = tk.Frame(self.win, bg="#E8F6F3")
        self.button_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=10)
        self.button_frame.grid_columnconfigure((0,1,2,3,4,5), weight=1)
        
        # Configuración de estilos personalizados para los botones
        self.customStyle = ttk.Style()
        self.customStyle.theme_use('clam')
        self.customStyle.configure("Custom.TButton", font=("Helvetica", 10, "bold"),
                                     foreground="white", background="#4CAF50", padding=6)
        self.customStyle.configure("Hover.TButton", font=("Helvetica", 10, "bold"),
                                     foreground="white", background="#388E3C", padding=6)
        self.customStyle.map("Custom.TButton",
                               background=[("active", "#388E3C")])
        
        # Botón Consultar: consulta un registro por su ID
        self.btnConsultar = ttk.Button(self.button_frame, text="🔍 Consultar", style="Custom.TButton",
                                       command=self.consulta_Registro)
        self.btnConsultar.grid(row=0, column=0, padx=5, pady=5)
        self.btnConsultar.bind("<Enter>", lambda e: e.widget.configure(style="Hover.TButton"))
        self.btnConsultar.bind("<Leave>", lambda e: e.widget.configure(style="Custom.TButton"))
        CreateToolTip(self.btnConsultar, "Consultar registro por ID.")
        
        # Botón Grabar: inserta o actualiza un registro en la base de datos
        self.btnGrabar = ttk.Button(self.button_frame, text="💾 Grabar", style="Custom.TButton")
        self.btnGrabar.grid(row=0, column=1, padx=5, pady=5)
        self.btnGrabar.bind("<1>", self.adiciona_Registro, add="+")
        self.btnGrabar.bind("<Enter>", lambda e: e.widget.configure(style="Hover.TButton"))
        self.btnGrabar.bind("<Leave>", lambda e: e.widget.configure(style="Custom.TButton"))
        CreateToolTip(self.btnGrabar, "Grabar nuevo registro.")
        
        # Botón Editar: carga el registro seleccionado en el formulario para editarlo
        self.btnEditar = ttk.Button(self.button_frame, text="✏️ Editar", style="Custom.TButton")
        self.btnEditar.grid(row=0, column=2, padx=5, pady=5)
        self.btnEditar.bind("<1>", self.edita_tablaTreeView, add="+")
        self.btnEditar.bind("<Enter>", lambda e: e.widget.configure(style="Hover.TButton"))
        self.btnEditar.bind("<Leave>", lambda e: e.widget.configure(style="Custom.TButton"))
        CreateToolTip(self.btnEditar, "Editar registro seleccionado (Ctrl+E).")
        
        # Botón Eliminar: elimina el/los registro(s) seleccionado(s)
        self.btnEliminar = ttk.Button(self.button_frame, text="❌ Eliminar", style="Custom.TButton")
        self.btnEliminar.grid(row=0, column=3, padx=5, pady=5)
        self.btnEliminar.bind("<1>", self.elimina_Registro, add="+")
        self.btnEliminar.bind("<Enter>", lambda e: e.widget.configure(style="Hover.TButton"))
        self.btnEliminar.bind("<Leave>", lambda e: e.widget.configure(style="Custom.TButton"))
        CreateToolTip(self.btnEliminar, "Eliminar registro(s) seleccionados.")
        
        # Botón Cancelar: limpia todos los campos del formulario
        self.btnCancelar = ttk.Button(self.button_frame, text="🚫 Cancelar", style="Custom.TButton",
                                      command=self.limpia_Campos)
        self.btnCancelar.grid(row=0, column=4, padx=5, pady=5)
        self.btnCancelar.bind("<Enter>", lambda e: e.widget.configure(style="Hover.TButton"))
        self.btnCancelar.bind("<Leave>", lambda e: e.widget.configure(style="Custom.TButton"))
        CreateToolTip(self.btnCancelar, "Cancelar operación y limpiar campos.")
        
        # Botón Exportar: exporta la información a un archivo CSV
        self.btnExportar = ttk.Button(self.button_frame, text="📤 Exportar", style="Custom.TButton",
                                      command=self.export_data)
        self.btnExportar.grid(row=0, column=5, padx=5, pady=5)
        self.btnExportar.bind("<Enter>", lambda e: e.widget.configure(style="Hover.TButton"))
        self.btnExportar.bind("<Leave>", lambda e: e.widget.configure(style="Custom.TButton"))
        CreateToolTip(self.btnExportar, "Exportar información de participantes a CSV.")
        
        # Barra de estado para mostrar mensajes y notificaciones al usuario
        self.status_bar = tk.Label(self.win, text="Listo", bd=1, relief=tk.SUNKEN, anchor='w', bg="#E8F6F3")
        self.status_bar.grid(row=2, column=0, sticky="ew", padx=10, pady=(0,5))
        
        # Carga inicial de los registros en el TreeView
        self.lee_tablaTreeView()
        
        # Atajos de teclado: Ctrl+N para nuevo registro y Ctrl+E para editar
        self.win.bind("<Control-n>", self.nuevo_registro)
        self.win.bind("<Control-e>", self.edita_tablaTreeView)

    # --------------------------
    # Métodos para la gestión del formulario y la base de datos
    # --------------------------
    def nuevo_registro(self, event=None):
        """Prepara la interfaz para ingresar un nuevo registro."""
        self.limpia_Campos()  # Limpia todos los campos
        self.entryId.focus_set()  # Coloca el foco en el campo de identificación
        self.status_bar.config(text="Preparado para nuevo registro.")

    def cargar_Nombre_Departamento(self):
        """
        Consulta la base de datos para obtener la lista de departamentos disponibles y los carga en el combobox.
        """
        query = "SELECT DISTINCT Nombre_Departamento FROM t_ciudades ORDER BY Nombre_Departamento"
        resultados = self.run_Query(query)
        if resultados is None:
            mssg.showerror("Error", "No se pudo cargar la lista de departamentos.")
            self.status_bar.config(text="Error al cargar departamentos.")
            return
        filas = resultados.fetchall()
        departamentos = [fila[0] for fila in filas]
        print("Depuración - Departamentos cargados:", departamentos)
        if not departamentos:
            mssg.showwarning("Información", "No se encontraron departamentos en la base de datos.")
        self.comboDepartamento["values"] = departamentos
        if departamentos:
            self.comboDepartamento.current(0)
            self.actualiza_ciudades()

    def actualiza_ciudades(self, event=None):
        """
        Actualiza el combobox de ciudades basado en el departamento seleccionado.
        Ejecuta una consulta SQL para obtener las ciudades correspondientes.
        """
        departamento_seleccionado = self.comboDepartamento.get()
        print("Departamento seleccionado:", departamento_seleccionado)
        query = "SELECT Nombre_Ciudad FROM t_ciudades WHERE Nombre_Departamento = ? ORDER BY Nombre_Ciudad"
        resultados = self.run_Query(query, (departamento_seleccionado,))
        if resultados is None:
            mssg.showerror("Error", "No se pudo cargar las ciudades.")
            self.status_bar.config(text="Error al cargar ciudades.")
            return
        filas = resultados.fetchall()
        ciudades = [fila[0] for fila in filas]
        if not ciudades:
            mssg.showwarning("Información", "No se encontraron ciudades para el departamento seleccionado.")
        self.comboCiudad["values"] = ciudades
        self.comboCiudad.set("")

    def valida(self):
        """
        Verifica que el campo de identificación no esté vacío.
        Retorna True si contiene datos, False de lo contrario.
        """
        return len(self.entryId.get()) != 0

    def run(self):
        """
        Inicia el bucle principal de la interfaz gráfica.
        """
        self.win.mainloop()

    def validar_identificacion(self, nuevo_valor):
        """
        Valida el campo de identificación:
         - Permite solo dígitos.
         - Máximo 15 caracteres.
         - Resalta el campo en verde si es correcto, rojo si hay error.
        """
        if nuevo_valor == "":
            self.entryId.config(highlightthickness=1, highlightbackground="green", highlightcolor="green")
            return True
        if not nuevo_valor.isdigit():
            self.entryId.config(highlightthickness=1, highlightbackground="red", highlightcolor="red")
            return False
        if len(nuevo_valor) > 15:
            mssg.showwarning("Advertencia", "La identificación no puede exceder 15 caracteres. Se han eliminado los caracteres adicionales.")
            self.entryId.config(highlightthickness=1, highlightbackground="red", highlightcolor="red")
            return False
        self.entryId.config(highlightthickness=1, highlightbackground="green", highlightcolor="green")
        return True

    def validar_numeros(self, nuevo_valor):
        """
        Valida que el valor ingresado contenga únicamente dígitos.
        """
        if nuevo_valor == "":
            return True
        return nuevo_valor.isdigit()

    def validar_nombre(self, nuevo_valor):
        """
        Valida que el nombre contenga solo letras, espacios, acentos y la letra ñ.
        Se utiliza una expresión regular para la validación.
        """
        if nuevo_valor == "":
            return True
        patron = r'^[A-Za-zÁÉÍÓÚáéíóúÑñ\s]+$'
        return re.fullmatch(patron, nuevo_valor) is not None

    def valida_Fecha(self, event=None):
        """
        Valida que la fecha ingresada esté en formato dd/mm/aaaa y no sea anterior a la fecha actual.
        Si la fecha es inválida, muestra un mensaje de error y limpia el campo.
        """
        date_str = self.entryFecha.get().strip()
        if date_str == "":
            return
        try:
            dt = datetime.strptime(date_str, "%d/%m/%Y")
        except ValueError:
            mssg.showerror("Error de Fecha", "Ingrese una fecha válida en formato dd/mm/aaaa.")
            self.entryFecha.delete(0, "end")
            self.status_bar.config(text="Error: fecha inválida.")
            return "break"
        
        today = datetime.today().date()
        if dt.date() < today:
            mssg.showerror("Error de Fecha", "La fecha no puede ser en el pasado.")
            self.entryFecha.delete(0, "end")
            self.status_bar.config(text="Error: la fecha es anterior a hoy.")
            return "break"

    def lee_tablaTreeView(self):
        """
        Carga todos los registros de la base de datos en el TreeView sin aplicar filtros.
        """
        # Elimina todos los registros actuales del TreeView
        for linea in self.treeDatos.get_children():
            self.treeDatos.delete(linea)
        query = """SELECT p.Id, p.Nombre, p."Dirección", p.Celular, p.Entidad, p.Fecha, p.Ciudad,
                          (SELECT Nombre_Departamento FROM t_ciudades WHERE Nombre_Ciudad = p.Ciudad LIMIT 1) AS Departamento
                   FROM t_participantes p
                   ORDER BY p.Id DESC"""
        db_rows = self.run_Query(query)
        if db_rows is None:
            self.status_bar.config(text="Error al leer la base de datos.")
            return
        # Inserta cada registro en el TreeView
        for row in db_rows:
            self.treeDatos.insert('', 0, text=row[0],
                                  values=[row[1], row[2], row[3], row[4], row[5], row[6], row[7]])
        self.status_bar.config(text="Registros cargados.")

    def filtra_registros(self, event=None):
        """
        Filtra dinámicamente los registros del TreeView en función del texto ingresado en el campo de búsqueda.
        """
        filtro = self.entryBuscar.get().strip()
        # Elimina registros actuales del TreeView
        for linea in self.treeDatos.get_children():
            self.treeDatos.delete(linea)
        query = """SELECT p.Id, p.Nombre, p."Dirección", p.Celular, p.Entidad, p.Fecha, p.Ciudad,
                      (SELECT Nombre_Departamento FROM t_ciudades WHERE Nombre_Ciudad = p.Ciudad LIMIT 1) AS Departamento
               FROM t_participantes p"""
        parametros = ()
        # Si se ingresa un filtro, se modifica la consulta para buscar coincidencias en varios campos
        if filtro:
            query += """ WHERE 
                        p.Id LIKE ? OR 
                        p.Nombre LIKE ? OR 
                        p."Dirección" LIKE ? OR 
                        p.Celular LIKE ? OR 
                        p.Entidad LIKE ? OR 
                        p.Fecha LIKE ? OR 
                        p.Ciudad LIKE ?"""
            filtro_param = f"%{filtro}%"
            parametros = (filtro_param,) * 7
        query += " ORDER BY p.Id DESC"
    
        db_rows = self.run_Query(query, parametros)
        if db_rows is None:
            self.status_bar.config(text="Error al aplicar filtro.")
            return
        # Inserta los registros filtrados en el TreeView
        for row in db_rows:
            self.treeDatos.insert('', 0, text=row[0],
                                  values=[row[1], row[2], row[3], row[4], row[5], row[6], row[7]])
        self.status_bar.config(text=f"Filtro aplicado: '{filtro}'" if filtro else "Mostrando todos los registros.")

    def carga_Datos(self):
        """
        Carga los datos del registro seleccionado en el TreeView hacia los campos del formulario para permitir su edición.
        """
        selected_item = self.treeDatos.selection()[0]
        item_data = self.treeDatos.item(selected_item)
        valores = item_data['values']
        # Habilita el campo de identificación y lo carga con el valor del registro seleccionado
        self.entryId.configure(state='normal')
        self.entryId.delete(0, 'end')
        self.entryId.insert(0, item_data['text'])
        self.entryId.configure(state='readonly')
        # Carga cada uno de los campos del formulario con los datos del registro
        self.entryNombre.delete(0, 'end')
        self.entryNombre.insert(0, valores[0])
        self.entryDireccion.delete(0, 'end')
        self.entryDireccion.insert(0, valores[1])
        self.entryCelular.delete(0, 'end')
        self.entryCelular.insert(0, valores[2])
        self.entryEntidad.delete(0, 'end')
        self.entryEntidad.insert(0, valores[3])
        self.entryFecha.delete(0, 'end')
        self.entryFecha.insert(0, valores[4])
        self.comboCiudad.set(valores[5])
        self.comboDepartamento.set(valores[6])

    def limpia_Campos(self):
        """
        Limpia y restablece todos los campos del formulario a su estado inicial.
        """
        self.entryId.configure(state='normal')
        self.entryId.delete(0, 'end')
        self.entryNombre.delete(0, 'end')
        # Reinicia el campo Dirección con el placeholder predeterminado
        placeholder_direccion = "Calle, número, barrio..."
        self.entryDireccion.delete(0, 'end')
        self.entryDireccion.insert(0, placeholder_direccion)
        self.entryDireccion.config(foreground="gray")
        self.entryCelular.delete(0, 'end')
        self.entryEntidad.delete(0, 'end')
        self.entryFecha.delete(0, 'end')
        self.comboDepartamento.set("")
        self.comboCiudad.set("")
        self.status_bar.config(text="Campos limpiados.")

    def run_Query(self, query, parametros=()):
        """
        Ejecuta una consulta SQL utilizando el manejador de base de datos.
        Imprime la consulta en consola para facilitar la depuración.
        """
        print("Ejecutando consulta:", query)
        return self.db_handler.execute_query(query, parametros)
    
    def adiciona_Registro(self, event=None):
        """
        Inserta o actualiza un registro en la base de datos.
        - Verifica si el registro ya existe (según el ID).
        - Si existe, pregunta si se desea actualizar; de lo contrario, inserta un nuevo registro.
        """
        id_participante = self.entryId.get().strip()
        if not self.valida():
            mssg.showerror("Error", "No puede dejar la identificación vacía")
            self.status_bar.config(text="Error: identificación vacía.")
            return
        ciudad_seleccionada = self.comboCiudad.get().strip()
        if not ciudad_seleccionada:
            mssg.showerror("Error", "Debe seleccionar una ciudad")
            self.status_bar.config(text="Error: ciudad no seleccionada.")
            return
        # Verifica si ya existe un registro con el mismo ID
        query_check = "SELECT COUNT(*) FROM t_participantes WHERE Id = ?"
        resultado = self.run_Query(query_check, (id_participante,))
        if resultado is None:
            self.status_bar.config(text="Error al verificar existencia.")
            return
        existe = resultado.fetchone()[0] > 0

        if existe:
            # Si el registro ya existe, solicita confirmación para actualizarlo
            confirmacion = mssg.askyesno("Confirmación", "Este participante ya existe. ¿Desea actualizar sus datos?")
            if not confirmacion:
                self.status_bar.config(text="Actualización cancelada.")
                return
            query = '''UPDATE t_participantes 
                       SET Nombre = ?, "Dirección" = ?, Celular = ?, Entidad = ?, Fecha = ?, Ciudad = ? 
                       WHERE Id = ?'''
            parametros = (self.entryNombre.get(), self.entryDireccion.get(),
                          self.entryCelular.get(), self.entryEntidad.get(), 
                          self.entryFecha.get(), ciudad_seleccionada, id_participante)
            self.run_Query(query, parametros)
            mssg.showinfo('Éxito', 'Registro actualizado con éxito')
            self.entryId.configure(state='readonly')
            self.status_bar.config(text="Registro actualizado con éxito.")
        else:
            # Si el registro no existe, solicita confirmación para agregarlo
            confirmacion = mssg.askyesno("Confirmación", "¿Desea agregar este nuevo registro?")
            if not confirmacion:
                self.status_bar.config(text="Operación de grabación cancelada.")
                return
            query = '''INSERT INTO t_participantes 
                       (Id, Nombre, "Dirección", Celular, Entidad, Fecha, Ciudad)
                       VALUES (?, ?, ?, ?, ?, ?, ?)'''
            parametros = (id_participante, self.entryNombre.get(), 
                          self.entryDireccion.get(), self.entryCelular.get(), 
                          self.entryEntidad.get(), self.entryFecha.get(), ciudad_seleccionada)
            self.run_Query(query, parametros)
            mssg.showinfo('Éxito', f'Registro {id_participante} agregado')
            self.status_bar.config(text="Registro agregado exitosamente.")

        # Después de insertar o actualizar, se limpian los campos y se actualiza el TreeView
        self.limpia_Campos()
        self.lee_tablaTreeView()

    def edita_tablaTreeView(self, event=None):
        """
        Prepara el formulario para editar el registro seleccionado.
        Si no se selecciona ningún ítem, se muestra un mensaje de error.
        """
        try:
            self.limpia_Campos()
            self.actualiza = True
            self.carga_Datos()  # Carga los datos del registro seleccionado en el formulario
            self.status_bar.config(text="Registro cargado para edición.")
        except IndexError:
            mssg.showerror("¡Atención!", "Por favor seleccione un ítem de la tabla.")
            self.status_bar.config(text="Error: no se seleccionó ningún ítem.")

    def elimina_Registro(self, event=None):
        """
        Elimina uno o varios registros seleccionados en el TreeView.
        Solicita confirmación al usuario antes de proceder.
        """
        seleccionados = self.treeDatos.selection()
        if not seleccionados:
            mssg.showwarning("¡Atención!", "Por favor seleccione al menos un participante para eliminar.")
            self.status_bar.config(text="Error: no se seleccionó ningún participante.")
            return
        confirmacion = mssg.askyesno("Confirmación", "¿Está seguro de que desea eliminar los participantes seleccionados?")
        if confirmacion:
            try:
                for item in seleccionados:
                    id_participante = self.treeDatos.item(item)['text']
                    query = "DELETE FROM t_participantes WHERE Id = ?"
                    self.run_Query(query, (id_participante,))
                    self.treeDatos.delete(item)
                mssg.showinfo("Éxito", "Participante(s) eliminado(s) correctamente.")
                self.status_bar.config(text="Participante(s) eliminado(s) correctamente.")
            except Exception as e:
                mssg.showerror("Error", f"No se pudo eliminar el/los participante(s). Error: {str(e)}")
                self.status_bar.config(text="Error al eliminar participantes.")

    def consulta_Registro(self):
        """
        Consulta un registro específico basado en el ID/NIT ingresado en el formulario.
        Carga el resultado en el TreeView y en los campos del formulario.
        """
        id_participante = self.entryId.get().strip()
        if id_participante == "":
            mssg.showerror("Error", "Debe ingresar el Id o NIT del participante para consultar.")
            self.status_bar.config(text="Error: no se ingresó Id para consultar.")
            return
        query = """SELECT p.Id, p.Nombre, p."Dirección", p.Celular, p.Entidad, p.Fecha, p.Ciudad,
                          (SELECT Nombre_Departamento FROM t_ciudades WHERE Nombre_Ciudad = p.Ciudad LIMIT 1) AS Departamento
                   FROM t_participantes p
                   WHERE p.Id = ?"""
        resultado = self.run_Query(query, (id_participante,))
        if resultado is None:
            self.status_bar.config(text="Error en la consulta.")
            return
        registro = resultado.fetchone()
        # Limpia el TreeView para mostrar solo el registro consultado
        for linea in self.treeDatos.get_children():
            self.treeDatos.delete(linea)
        if registro:
            self.treeDatos.insert('', 0, text=registro[0],
                                  values=[registro[1], registro[2], registro[3], registro[4],
                                          registro[5], registro[6], registro[7]])
            # Carga los datos en el formulario
            self.entryId.configure(state='normal')
            self.entryId.delete(0, 'end')
            self.entryId.insert(0, registro[0])
            self.entryId.configure(state='readonly')
            self.entryNombre.delete(0, 'end')
            self.entryNombre.insert(0, registro[1])
            self.entryDireccion.delete(0, 'end')
            self.entryDireccion.insert(0, registro[2])
            self.entryCelular.delete(0, 'end')
            self.entryCelular.insert(0, registro[3])
            self.entryEntidad.delete(0, 'end')
            self.entryEntidad.insert(0, registro[4])
            self.entryFecha.delete(0, 'end')
            self.entryFecha.insert(0, registro[5])
            self.comboCiudad.set(registro[6])
            if registro[7]:
                self.comboDepartamento.set(registro[7])
            else:
                # Si no se obtiene el departamento, se consulta a la tabla t_ciudades
                dep_query = "SELECT Nombre_Departamento FROM t_ciudades WHERE Nombre_Ciudad = ?"
                dep_result = self.run_Query(dep_query, (registro[6],))
                dep = dep_result.fetchone() if dep_result else None
                self.comboDepartamento.set(dep[0] if dep else "")
            self.status_bar.config(text="Consulta realizada con éxito.")
        else:
            mssg.showinfo("Consulta", "No se encontró ningún participante con el Id/NIT ingresado.")
            self.status_bar.config(text="Consulta sin resultados.")

    def export_data(self):
        """
        Exporta la información de participantes a un archivo CSV.
        Solicita al usuario la ubicación del archivo y escribe la cabecera y los registros.
        """
        query = """SELECT p.Id, p.Nombre, p."Dirección", p.Celular, p.Entidad, p.Fecha, p.Ciudad,
                          (SELECT Nombre_Departamento FROM t_ciudades WHERE Nombre_Ciudad = p.Ciudad LIMIT 1) AS Departamento
                   FROM t_participantes p
                   ORDER BY p.Id DESC"""
        db_rows = self.run_Query(query)
        if db_rows is None:
            self.status_bar.config(text="Error al obtener datos para exportar.")
            mssg.showerror("Error", "No se pudo obtener los datos para exportar.")
            return
        registros = db_rows.fetchall()
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files","*.csv")])
        if not file_path:
            self.status_bar.config(text="Exportación cancelada.")
            return
        try:
            with open(file_path, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                # Escribe la cabecera del CSV
                writer.writerow(["Id", "Nombre", "Dirección", "Celular", "Entidad", "Fecha", "Ciudad", "Departamento"])
                for row in registros:
                    writer.writerow(row)
            self.status_bar.config(text=f"Datos exportados exitosamente a {file_path}")
            mssg.showinfo("Éxito", f"Datos exportados exitosamente a {file_path}")
        except Exception as e:
            self.status_bar.config(text="Error al exportar datos.")
            mssg.showerror("Error", f"No se pudo exportar los datos. Error: {str(e)}")

# --------------------------
# Bloque Principal: Ejecución de la aplicación
# --------------------------
if __name__ == "__main__":
    app = Participantes()
    app.run()
