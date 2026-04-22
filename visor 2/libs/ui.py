import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
from .image_processor import ImageProcessor


class ImageViewerGUI:
    """Clase encargada de construir y controlar la interfaz del visor."""

    def __init__(self, root):
        """Recibe la ventana raiz y prepara todo el estado de la interfaz."""
        self.root = root
        self.root.title("Visor de Imágenes")
        self.processor = ImageProcessor() #carga el procesador de imagenes
        
        self.image_path_var = tk.StringVar() #guarda la ruta de la imagen principal seleccionada.

        ## ----- / variables iniciales de la imagen / ----- ##
        self.brightness_var = tk.IntVar(value=0) #brillo
        self.contrast_var = tk.IntVar(value=0) #contraste

        self.rotation_var = tk.IntVar(value=0) #rotación en grados

        self.fusion_alpha_var = tk.DoubleVar(value=0.0) #transparencia de la imagen fusionada
        self.fusion_mode_var = tk.StringVar(value="normal") #modo de fusión

        self.zone_mode_var = tk.StringVar(value="none") #indicación de zonas claras, oscuras o ninguna

        self.rgb_red_var = tk.BooleanVar(value=True) #canal rojo
        self.rgb_green_var = tk.BooleanVar(value=True) #canal verde
        self.rgb_blue_var = tk.BooleanVar(value=True) #canal azul
        self.cmy_cyan_var = tk.BooleanVar(value=False) #canal cian
        self.cmy_magenta_var = tk.BooleanVar(value=False) #canal magenta
        self.cmy_yellow_var = tk.BooleanVar(value=False) #canal amarillo

        self.zoom_scale_var = tk.DoubleVar(value=1.0) #zoom

        self.threshold_var = tk.IntVar(value=128) #umbral de binarización
        self.apply_binary_var = tk.BooleanVar(value=False) #binarización
        self.apply_negative_var = tk.BooleanVar(value=False) #negativo

        self.display_image = None #evita que tkinter libere la imagen seleccionada

        self._build_layout() #construye la interfaz grafica

    def _build_layout(self):
        """Construye visualmente la ventana y todos sus controles."""
        self.root.geometry("1280x720") #tamaño inicial de la ventana
        title_frame = ttk.Frame(self.root) #frame para el titulo
        title_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5) #ubica el frame en la parte superior
        
        ## ---------- / Parte superior / ---------- ##

        #titulo de programa
        title_label = ttk.Label(
            title_frame,
            text="Visor de Imágenes",
            anchor="center",
            foreground="black",
            font=("Arial", 18, "bold"),
        )
        #centra horizontalmente el titulo
        title_label.pack(fill=tk.X)

        #frame que agrupa ruta y botones de archivo.
        path_frame = ttk.Frame(self.root)
        path_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

        path_label = ttk.Label(path_frame, text="Archivo de imagen:") #etiqueta para el campo de ruta
        path_label.pack(side=tk.LEFT)

        path_entry = ttk.Entry(path_frame, textvariable=self.image_path_var) #campo de texto para la ruta
        path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        #se deja expandible
        path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        explore_button = ttk.Button(path_frame, text="Explorar", command=self._on_explore) #boton para explorar el archivo
        explore_button.pack(side=tk.LEFT, padx=2)

        load_button = ttk.Button(path_frame, text="Cargar", command=self._on_load) #boton para cargar la imagen principal
        load_button.pack(side=tk.LEFT, padx=2)

        save_button = ttk.Button(path_frame, text="Guardar", command=self._on_save) #boton para guardar la imagen procesada
        save_button.pack(side=tk.LEFT, padx=2)

        #boton para fusionar imagenes
        fusion_button = ttk.Button(
            path_frame,
            text="Fusionar Imágenes",
            command=self._on_load_second_image,
        )
        fusion_button.pack(side=tk.LEFT, padx=2)

        ## ---------- / Parte Principal / ---------- ##

        main_frame = ttk.Frame(self.root)
        main_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=5)

        image_frame = ttk.Frame(main_frame) #crea el frame para la imagen principal
        image_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True) #ubica el frame a la izquierda y le permite crecer
        image_frame.columnconfigure(0, weight=1) #le permite expandirse en la columna
        image_frame.rowconfigure(0, weight=1) #le permite expandirse en la fila principal

        self.canvas = tk.Canvas(image_frame, bg="white") #crea el canvas para la visualización
        self.canvas.grid(row=0, column=0, sticky="nsew") #coloca el canvas llenando toda la celda disponible
        self.canvas.bind("<Configure>", self._on_canvas_resize) #vincula el cambio de tamaño del canvas para redibujar la imagen

        ### NAVEGACIÓN DE IMÁGEN ###    
        #barra horizontal para navegar la imagen ampliada
        self.horizontal_scrollbar = ttk.Scrollbar(
            image_frame,
            orient=tk.HORIZONTAL,
            command=self.canvas.xview,
        )
        #barra vertical para navegar la imagen ampliada
        self.vertical_scrollbar = ttk.Scrollbar(
            image_frame,
            orient=tk.VERTICAL,
            command=self.canvas.yview,
        )
        #conecta el canvas con ambas barras de desplazamiento
        self.canvas.configure(
            xscrollcommand=self.horizontal_scrollbar.set,
            yscrollcommand=self.vertical_scrollbar.set,
        )
        
        self.horizontal_scrollbar.grid(row=1, column=0, sticky="ew") #coloca la barra horizontal en la fila inferior
        self.vertical_scrollbar.grid(row=0, column=1, sticky="ns") #coloca la barra vertical en la columna derecha
        self.horizontal_scrollbar.grid_remove() #oculta la barra horizontal mientras no sea necesaria
        self.vertical_scrollbar.grid_remove() #oculta la barra vertical mientras no sea necesaria

        #crea y ubica el frame para los controles lateral
        controls_frame = ttk.Frame(main_frame, width=260)
        controls_frame.pack(side=tk.RIGHT, fill=tk.Y)
        
        ### BRILLO ###
        #crea y ubica la etiqueta del control de brillo
        brightness_label = ttk.Label(controls_frame, text="Brillo:")
        brightness_label.pack(anchor="w", pady=(0, 2))

        #slider para controlar el brillo de la imagen
        brightness_scale = ttk.Scale(
            controls_frame,
            from_=-100,
            to=100,
            orient=tk.HORIZONTAL,
            variable=self.brightness_var,
            command=self._on_live_change,
        )
        brightness_scale.pack(fill=tk.X, pady=(0, 5))

        ### CONTRASTE ###
        #crea y ubica la etiqueta del control de contraste
        contrast_label = ttk.Label(controls_frame, text="Contraste:")
        contrast_label.pack(anchor="w", pady=(0, 2))
        #slider para controlar el contraste de la imagen
        contrast_scale = ttk.Scale(
            controls_frame,
            from_=-100,
            to=100,
            orient=tk.HORIZONTAL,
            variable=self.contrast_var,
            command=self._on_live_change,
        )
        contrast_scale.pack(fill=tk.X, pady=(0, 5))

        ### ROTACIÓN ###
        #crea y ubica la etiqueta del control de rotación
        rotation_label = ttk.Label(controls_frame, text="Rotación (°):")
        rotation_label.pack(anchor="w", pady=(5, 2))
        #slider para controlar el angulo de rotación
        rotation_scale = ttk.Scale(
            controls_frame,
            from_=0,
            to=360,
            orient=tk.HORIZONTAL,
            variable=self.rotation_var,
            command=self._on_live_change,
        )
        rotation_scale.pack(fill=tk.X, pady=(0, 5))

        ### TRANSPARENCIA FUSIÓN ###
        #crea y ubica la etiqueta del control de fusion
        fusion_label = ttk.Label(controls_frame, text="Transparencia Fusión:")
        fusion_label.pack(anchor="w", pady=(5, 2))
        #slider para controla cuanto participa la segunda imagen.
        fusion_scale = ttk.Scale(
            controls_frame,
            from_=0.0,
            to=1.0,
            orient=tk.HORIZONTAL,
            variable=self.fusion_alpha_var,
            command=self._on_live_change,
        )
        fusion_scale.pack(fill=tk.X, pady=(0, 5))
        
        ### MODO FUSIÓN ###
        #crea y ubica la etiqueta del selector de modo de fusion
        fusion_mode_label = ttk.Label(controls_frame, text="Modo de Fusión:")
        fusion_mode_label.pack(anchor="w", pady=(0, 2))
        #crea un combobox con los modos disponibles de superposicion
        fusion_mode_combo = ttk.Combobox(
            controls_frame,
            textvariable=self.fusion_mode_var,
            values=["normal", "multiplicacion", "adicion", "diferencia"],
            state="readonly",
        )
        fusion_mode_combo.pack(fill=tk.X, pady=(0, 5))
        #actualiza la imagen cuando el usuario cambia el modo
        fusion_mode_combo.bind("<<ComboboxSelected>>", self._on_entry_commit) 

        ### ZONAS ###
        #crea y ubica el frame para los controles de zonas
        zones_frame = ttk.LabelFrame(controls_frame, text="Zonas")
        zones_frame.pack(fill=tk.X, pady=5)
        
        #crea la opcion para no aplicar filtro de zonas.
        no_zone_radio = ttk.Radiobutton(
            zones_frame,
            text="Sin filtro",
            value="none",
            variable=self.zone_mode_var,
            command=self._on_live_change,
        )
        no_zone_radio.pack(anchor="w") #ubica la opcion dentro del grupo
        #crea la opcion para resaltar zonas claras.
        light_radio = ttk.Radiobutton(
            zones_frame,
            text="Zonas Claras",
            value="light",
            variable=self.zone_mode_var,
            command=self._on_live_change,
        )
        light_radio.pack(anchor="w") #ubica la opcion dentro del grupo
        #crea la opcion para resaltar zonas oscuras.
        dark_radio = ttk.Radiobutton(
            zones_frame,
            text="Zonas Oscuras",
            value="dark",
            variable=self.zone_mode_var,
            command=self._on_live_change,
        )
        dark_radio.pack(anchor="w") #ubica la opcion dentro del grupo

        ### RGB ###
        #crea y ubica el frame para los controles de canales RGB
        rgb_frame = ttk.LabelFrame(controls_frame, text="Canales RGB")
        rgb_frame.pack(fill=tk.X, pady=5)

        #crea el check del canal rojo.
        rgb_r = ttk.Checkbutton(
            rgb_frame,
            text="Rojo",
            variable=self.rgb_red_var,
            command=self._on_live_change,
        )
        rgb_r.pack(anchor="w") #ubica el check dentro del grupo
        #crea el check del canal verde.
        rgb_g = ttk.Checkbutton(
            rgb_frame,
            text="Verde",
            variable=self.rgb_green_var,
            command=self._on_live_change,
        )
        rgb_g.pack(anchor="w") #ubica el check dentro del grupo
        #crea el check del canal azul.
        rgb_b = ttk.Checkbutton(
            rgb_frame,
            text="Azul",
            variable=self.rgb_blue_var,
            command=self._on_live_change,
        )
        rgb_b.pack(anchor="w") #ubica el check dentro del grupo

        ### CMY ###
        #crea y ubica el frame para los controles de canales CMY
        cmy_frame = ttk.LabelFrame(controls_frame, text="Canales CMY")
        cmy_frame.pack(fill=tk.X, pady=5)

        #crea el check del canal cian.
        cmy_c = ttk.Checkbutton(
            cmy_frame,
            text="Cian",
            variable=self.cmy_cyan_var,
            command=self._on_live_change,
        )
        cmy_c.pack(anchor="w") #ubica el check dentro del grupo
        #crea el check del canal magenta.
        cmy_m = ttk.Checkbutton(
            cmy_frame,
            text="Magenta",
            variable=self.cmy_magenta_var,
            command=self._on_live_change,
        )
        cmy_m.pack(anchor="w") #ubica el check dentro del grupo
        #crea el check del canal amarillo.
        cmy_y = ttk.Checkbutton(
            cmy_frame,
            text="Amarillo",
            variable=self.cmy_yellow_var,
            command=self._on_live_change,
        )
        cmy_y.pack(anchor="w") #ubica el check dentro del grupo

        ### ZOOM ###
        #crea y ubica el frame para los controles de zoom
        zoom_frame = ttk.LabelFrame(controls_frame, text="Zoom")
        zoom_frame.pack(fill=tk.X, pady=5)

        #crea y ubica un frame interno para alinear botones y etiqueta.
        zoom_controls_frame = ttk.Frame(zoom_frame)
        zoom_controls_frame.pack(fill=tk.X, pady=2)

        #crea y ubica el boton para reducir el zoom.    
        zoom_out_button = ttk.Button(zoom_controls_frame, text="-", width=4, command=self._zoom_out)
        zoom_out_button.pack(side=tk.LEFT)

        #crea y ubica la etiqueta que muestra el porcentaje actual de zoom.
        self.zoom_label = ttk.Label(zoom_controls_frame, text="100%", anchor="center")
        self.zoom_label.pack(side=tk.LEFT, expand=True, padx=6)

        #crea y ubica el boton que restaura el zoom al 100 por ciento.
        zoom_reset_button = ttk.Button(zoom_controls_frame, text="100%", width=6, command=self._zoom_reset)
        zoom_reset_button.pack(side=tk.LEFT, padx=2)

        #crea y ubica el boton para aumentar el zoom.
        zoom_in_button = ttk.Button(zoom_controls_frame, text="+", width=4, command=self._zoom_in)
        zoom_in_button.pack(side=tk.LEFT)

        ### BINARYIZACION Y NEGATIVO ###
        #crea y ubica el frame para los controles de binarizacion y negativo
        binary_frame = ttk.LabelFrame(controls_frame, text="Binarización y Negativo")
        binary_frame.pack(fill=tk.X, pady=5)
        #crea y ubica el check para activar la binarizacion.
        binary_check = ttk.Checkbutton(
            binary_frame,
            text="Binarizar",
            variable=self.apply_binary_var,
            command=self._on_live_change,
        )
        binary_check.pack(anchor="w") #muestra el check en el grupo.
        #crea y ubica la etiqueta que describe el slider de umbral.
        threshold_label = ttk.Label(binary_frame, text="Umbral:")
        threshold_label.pack(anchor="w")
        #crea y ubica el slider que define el umbral de binarizacion.
        threshold_scale = ttk.Scale(
            binary_frame,
            from_=0,
            to=255,
            orient=tk.HORIZONTAL,
            variable=self.threshold_var,
            command=self._on_live_change,
        )
        threshold_scale.pack(fill=tk.X, pady=(0, 4)) #lo muestra en el grupo.

        #crea y ubica la etiqueta que refleja numericamente el umbral.
        self.threshold_value_label = ttk.Label(binary_frame, text="128")
        self.threshold_value_label.pack(anchor="w")
        #crea el check para activar el negativo.
        negative_check = ttk.Checkbutton(
            binary_frame,
            text="Negativo",
            variable=self.apply_negative_var,
            command=self._on_live_change,
        )
        negative_check.pack(anchor="w") #muestra el check en el grupo.

        ## ---------- / Parte Inferior / ---------- ##

        #crea y ubica el frame inferior para acciones globales.
        bottom_frame = ttk.Frame(self.root)
        bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=5)

        #crea y ubica el boton que abre la ventana del histograma.
        histogram_button = ttk.Button(bottom_frame, text="Histograma", command=self._on_histogram)
        histogram_button.pack(side=tk.LEFT, padx=5)
        
        #crea y ubica el boton que fuerza una actualizacion manual.
        update_button = ttk.Button(bottom_frame, text="Actualizar", command=self._on_update)
        update_button.pack(side=tk.LEFT)

        #crea y ubica el boton para volver a la imagen original.
        restore_button = ttk.Button(
            bottom_frame,
            text="Restaurar Original",
            command=self._on_restore_original,
        )
        restore_button.pack(side=tk.LEFT, padx=5)

    def _on_explore(self):
        """Abre el explorador de archivos para elegir la imagen principal."""
        filetypes = [("Imágenes", "*.jpg *.jpeg *.png *.bmp"), ("Todos los archivos", "*.*")] #extensiones permitidas
        filename = filedialog.askopenfilename(title="Seleccionar imagen", filetypes=filetypes) #abre el explorador de archivos
        if filename:
            self.image_path_var.set(filename) #actualiza la ruta visible

    def _on_load(self):
        """Carga la imagen principal seleccionada y la muestra en pantalla."""
        path = self.image_path_var.get().strip() #obtiene la ruta visible
        if not path: #Si no hay ruta visible, muestra error
            messagebox.showerror("Error", "Seleccione un archivo de imagen.")
            return

        try:
            array = self.processor.load_main_image(path) #carga la imagen principal
        except Exception as exc:
            #si falla la carga, muestra error y cancela la operacion
            messagebox.showerror("Error", f"No se pudo cargar la imagen.\n{exc}")
            return

        self._show_array_on_canvas(array) #dibuja la imagen en el canvas
        self._on_update(show_errors=False) #actualiza los controles

    def _on_save(self):
        """Guarda en disco la imagen procesada actual."""
        if self.processor.image_array is None: #si no hay imagen procesada, muestra error
            messagebox.showerror("Error", "No hay imagen para guardar.")
            return

        filetypes = [("Imagen PNG", "*.png"), ("Imagen JPG", "*.jpg *.jpeg"), ("Bitmap", "*.bmp")] #formatos permitidos

        #abre el cuadro de dialogo para elegir nombre y ruta de salida.
        filename = filedialog.asksaveasfilename(
            title="Guardar imagen",
            defaultextension=".png",
            filetypes=filetypes,
        )
        #si el usuario cancela, se abandona la operacion.
        if not filename:
            return

        try:
            self.processor.save_image(filename) #guarda la imagen en disco
        except Exception as exc:
            #en caso de algun error, muestra error y cancela la operacion
            messagebox.showerror("Error", f"No se pudo guardar la imagen.\n{exc}")

    def _on_load_second_image(self):
        """Carga una segunda imagen para realizar fusion."""
        filetypes = [("Imágenes", "*.jpg *.jpeg *.png *.bmp"), ("Todos los archivos", "*.*")] #extensiones permitidas
        #abre el dialogo de seleccion para la imagen secundaria.
        filename = filedialog.askopenfilename(
            title="Seleccionar segunda imagen",
            filetypes=filetypes,
        )
        #si el usuario cancela, se abandona la operacion.
        if not filename:
            return

        try:
            self.processor.load_second_image(filename) #carga la imagen secundaria
        except Exception as exc:
            #si falla la carga, muestra error y cancela la operacion
            messagebox.showerror("Error", f"No se pudo cargar la segunda imagen.\n{exc}")
            return
        self._on_update(show_errors=False) #actualiza los controles
        messagebox.showinfo("Información", "Segunda imagen cargada para la fusión.")

    def _on_update(self, show_errors=True):
        """Lee los controles actuales y recalcula la imagen mostrada."""
        #si aun no hay imagen principal, no se intenta procesar nada.
        if self.processor.original_image_array is None:
            return

        try:
            #crea un diccionario simple con todos los parametros.
            config = self._build_processing_config()
            #aplica la cadena completa de transformaciones.
            array = self.processor.apply_transformations(config)
        except Exception as exc:
            #si se permite mostrar errores, se informa el problema al usuario.
            if show_errors:
                messagebox.showerror("Error", f"No se pudo actualizar la imagen.\n{exc}")
            return

        #actualiza la imagen visible en el canvas.
        self._show_array_on_canvas(array)

    def _on_histogram(self):
        """Solicita al procesador mostrar el histograma actual."""
        try:
            #genera y muestra el histograma de la imagen procesada.
            self.processor.show_histogram()
        except Exception as exc:
            #si algo falla, se muestra un cuadro de error.
            messagebox.showerror("Error", f"No se pudo generar el histograma.\n{exc}")

    def _on_restore_original(self):
        """Restaura la imagen original y reinicia los controles."""
        try:
            #recupera una copia limpia de la imagen original.
            array = self.processor.restore_original_image()
        except Exception as exc:
            #si falla la restauracion, se informa el problema.
            messagebox.showerror("Error", f"No se pudo restaurar la imagen.\n{exc}")
            return

        #reinicia los controles al estado base del programa.
        self._reset_controls()
        #dibuja la imagen original en pantalla.
        self._show_array_on_canvas(array)

    def _build_processing_config(self):
        """Empaqueta todos los valores de la interfaz en un diccionario."""
        return {
            "brightness": int(round(self.brightness_var.get())), #redondea y convierte el brillo a entero.
            "contrast": int(round(self.contrast_var.get())), #redondea y convierte el contraste a entero.
            "rotation": int(round(self.rotation_var.get())), #redondea la rotacion para trabajar con grados enteros. 
            "fusion_alpha": float(self.fusion_alpha_var.get()), #obtiene el valor actual del control de fusion.
            "fusion_mode": self.fusion_mode_var.get(), #obtiene el modo de la superposicion elegido.
            "zone_mode": self.zone_mode_var.get(), #obtiene el filtro actual de zonas.
            "rgb_red": self.rgb_red_var.get(), #consulta si el canal rojo esta activo.
            "rgb_green": self.rgb_green_var.get(), #consulta si el canal verde esta activo.
            "rgb_blue": self.rgb_blue_var.get(), #consulta si el canal azul esta activo.
            "cmy_cyan": self.cmy_cyan_var.get(), #consulta si el canal cian esta activo.
            "cmy_magenta": self.cmy_magenta_var.get(), #consulta si el canal magenta esta activo.
            "cmy_yellow": self.cmy_yellow_var.get(), #consulta si el canal amarillo esta activo.
            "zoom_scale": float(self.zoom_scale_var.get()), #obtiene el factor de zoom de la vita.
            "threshold": int(self.threshold_var.get()), #obtiene el umbral de binarizacion.
            "apply_binary": self.apply_binary_var.get(), #indica si se aplica binarizacion.
            "apply_negative": self.apply_negative_var.get(), #indica si se aplica el negativo.
        }

    def _on_live_change(self, _value=None):
        """Actualiza la vista cuando cambia un slider o check."""
        self._refresh_status_labels() #refresca las etiquetas numericas visibles.
        self._on_update(show_errors=False) #actualiza los controles

    def _on_entry_commit(self, _event=None):
        """Actualiza la vista al confirmar un valor de lista."""
        self._on_live_change() #actualiza la vista en vivo

    def _on_canvas_resize(self, _event=None):
        """Redibuja la imagen cuando cambia el tamano del canvas."""
        if self.processor.image_array is not None: #si hay una imagen procesada cargada
            self._show_array_on_canvas(self.processor.image_array) #dibuja la imagen en pantalla.

    def _zoom_in(self):
        """Aumenta el zoom de la vista en pasos de 25 por ciento."""
        current_scale = self.zoom_scale_var.get() #obtiene el factor de zoom actual.
        self.zoom_scale_var.set(min(4.0, current_scale + 0.25)) #incrementa el zoom en 25%
        self._on_live_change()

    def _zoom_out(self):
        """Disminuye el zoom de la vista en pasos de 25 por ciento."""
        current_scale = self.zoom_scale_var.get() #obtiene el factor de zoom actual.
        self.zoom_scale_var.set(max(0.25, current_scale - 0.25))#decrementa el zoom en 25%
        self._on_live_change()

    def _zoom_reset(self):
        """Restablece el zoom al 100 por ciento."""
        self.zoom_scale_var.set(1.0) #fija el zoom al 100%
        self._on_live_change()

    def _refresh_status_labels(self):
        """Sincroniza etiquetas numericas de zoom y umbral."""
        zoom_percent = int(round(self.zoom_scale_var.get() * 100)) #redondea el factor de zoom actual a porcentaje entero.
        threshold_value = int(round(self.threshold_var.get())) #redondea el valor actual del umbral para mostrarlo.
        self.zoom_label.config(text=f"{zoom_percent}%") #actualiza el texto de la etiqueta de zoom.
        self.threshold_value_label.config(text=str(threshold_value)) #actualiza el texto de la etiqueta de umbral.

    def _reset_controls(self):
        """Devuelve todos los controles al estado inicial del visor."""
        self.brightness_var.set(0) #restaura el brillo al valor neutro.
        self.contrast_var.set(0) #restaura el contraste al valor neutro.
        self.rotation_var.set(0) #reinicia la rotacion a cero grados.
        self.fusion_alpha_var.set(0.0) #elimina la presencia de la segunda imagen en la fusion.
        self.fusion_mode_var.set("normal") #vuelve a usar el modo de fusion basico.
        self.zone_mode_var.set("none") #desactiva cualquier resaltado de zonas.
        self.rgb_red_var.set(True) #reactiva el canal rojo.
        self.rgb_green_var.set(True) #reactiva el canal verde.
        self.rgb_blue_var.set(True) #reactiva el canal azul.
        self.cmy_cyan_var.set(False) #desactiva el canal cian.
        self.cmy_magenta_var.set(False) #desactiva el canal magenta.
        self.cmy_yellow_var.set(False) #desactiva el canal amarillo.
        self.zoom_scale_var.set(1.0) #restaura el zoom al 100%. 
        self.threshold_var.set(128) #restaura el umbral al valor medio.
        self.apply_binary_var.set(False) #desactiva la binarizacion.
        self.apply_negative_var.set(False) #desactiva el negativo.
        self._refresh_status_labels() #actualiza las etiquetas asociadas a estos valores.

    def _show_array_on_canvas(self, array):
        """Convierte un arreglo en imagen visible y la dibuja en el canvas."""
        if array is None: #si no hay una imagen valida
            return
        
        height = array.shape[0] #obtiene la altura original de la imagen.
        width = array.shape[1] #obtiene el ancho original de la imagen.
        canvas_width = self.canvas.winfo_width() #consulta el ancho actual disponible en el canvas.
        canvas_height = self.canvas.winfo_height() #consulta el alto actual disponible en el canvas.

        #si el canvas es muy pequeño, se usa un valor predeterminado para el dibujo.
        if canvas_width <= 1 or canvas_height <= 1:
            canvas_width = 800
            canvas_height = 500

        base_scale = min(canvas_width / width, canvas_height / height) #calcula la escala base que hace encajar la imagen en el canvas.
        zoom_scale = float(self.zoom_scale_var.get()) #obtiene el factor de zoom actual.
        display_scale = base_scale * zoom_scale #calcula la escala final combinando ajuste base y zoom.
        #calcula el ancho y alto final que tendra la imagen en pantalla.
        new_width = max(1, int(width * display_scale))
        new_height = max(1, int(height * display_scale))

        image = Image.fromarray(array) #convierte el arrego de NumPy en una imagen PIL.
        image = image.resize((new_width, new_height), Image.LANCZOS) #redimensiona la imagen segun la escala calculada.
        self.display_image = ImageTk.PhotoImage(image) #convierte la imagen PIL en un objeto compatible con Tkinter.

        #limpia el canvas
        self.canvas.delete("all")
        #decide si hacen falta scrollbars cuando el zoom supera el tamano visible.
        use_scrollbars = zoom_scale > 1.0 and (new_width > canvas_width or new_height > canvas_height)

        if use_scrollbars: #si la imagen ampliada ya no cabe completamente en el canvas
            #muestra las barras de desplazamiento
            self._set_scrollbars_visibility(True)
            self.canvas.create_image(0, 0, image=self.display_image, anchor="nw") #dibuja la imagen desde la esquina superior izquierda
            self.canvas.configure(scrollregion=(0, 0, new_width, new_height)) #actualiza la region desplazable del canvas
            self._center_canvas_view(new_width, new_height, canvas_width, canvas_height) #centra la vista inicial
        else: #si no se necesitan scrollbars
            self._set_scrollbars_visibility(False) #oculta las barras de desplazamiento
            #dibuja la imagen centrada dentro del canvas
            self.canvas.create_image(
                canvas_width // 2,
                canvas_height // 2,
                image=self.display_image,
                anchor="center",
            )
            self.canvas.configure(scrollregion=(0, 0, canvas_width, canvas_height)) #redefine la region visible para el tamano actual del canvas
            self.canvas.xview_moveto(0) #vuelve el desplazamiento horizontal a 0
            self.canvas.yview_moveto(0) #vuelve el desplazamiento vertical a 0

    def _set_scrollbars_visibility(self, visible):
        """Muestra u oculta las barras de desplazamiento del visor."""
        if visible: #muestra las barras de desplazamiento
            self.horizontal_scrollbar.grid()
            self.vertical_scrollbar.grid()
        else: #oculta las barras de desplazamiento
            self.horizontal_scrollbar.grid_remove()
            self.vertical_scrollbar.grid_remove()

    def _center_canvas_view(self, content_width, content_height, view_width, view_height):
        """Centra la ventana visible del canvas sobre la imagen ampliada."""
        if content_width > view_width: #si la imagen ampliada sobrepasa el ancho visible del canvas
            max_offset_x = content_width - view_width #calcula el desplazamiento maximo posible en horizontal para centrar la vista
            offset_x = max_offset_x / 2.0 #tomar la mitad del desplazamiento maximo para centrar horizontalmente
            self.canvas.xview_moveto(offset_x / content_width) #mueve la vista horizontalmente usando proporcion del contenido para centrar horizontalmente
        else: #si no sobrepasa el ancho visible del canvas
            self.canvas.xview_moveto(0) #vuelve el desplazamiento horizontal a 0

        if content_height > view_height: #si la imagen ampliada sobrepasa el alto visible del canvas
            max_offset_y = content_height - view_height #calcula el desplazamiento maximo posible en vertical para centrar la vista
            offset_y = max_offset_y / 2.0 #tomar la mitad del desplazamiento maximo para centrar verticalmente usando proporcion del contenido.
            self.canvas.yview_moveto(offset_y / content_height) #mueve la vista verticalmente usando proporcion del contenido para centrar verticalmente
        else: #si no sobrepasa el alto visible del canvas
            self.canvas.yview_moveto(0) #vuelve el desplazamiento vertical a 0
