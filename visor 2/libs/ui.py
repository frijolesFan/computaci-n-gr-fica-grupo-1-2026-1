"""Interfaz grafica principal del visor de imagenes."""

# Se importa Tkinter como base para construir la interfaz grafica.
import tkinter as tk
# Se importan widgets tematicos, dialogos de archivo y cuadros de mensaje.
from tkinter import ttk, filedialog, messagebox
# Se importan utilidades de PIL para convertir arreglos en imagenes visibles.
from PIL import Image, ImageTk
# Se importa la clase que concentra toda la logica de procesamiento.
from .image_processor import ImageProcessor


class ImageViewerGUI:
    """Clase encargada de construir y controlar la interfaz del visor."""

    def __init__(self, root):
        """Recibe la ventana raiz y prepara todo el estado de la interfaz."""
        # Se guarda la ventana principal para reutilizarla desde otros metodos.
        self.root = root
        # Se define el titulo visible de la ventana.
        self.root.title("Visor de Imágenes")
        # Se crea una instancia del procesador que manipula las imagenes.
        self.processor = ImageProcessor()

        # Esta variable guarda la ruta de la imagen principal seleccionada.
        self.image_path_var = tk.StringVar()
        # Esta variable guarda el valor actual del brillo.
        self.brightness_var = tk.IntVar(value=0)
        # Esta variable guarda el valor actual del contraste.
        self.contrast_var = tk.IntVar(value=0)
        # Esta variable guarda el angulo de rotacion en grados.
        self.rotation_var = tk.IntVar(value=0)
        # Esta variable controla que tanto influye la segunda imagen en la fusion.
        self.fusion_alpha_var = tk.DoubleVar(value=0.0)
        # Esta variable guarda el modo de fusion elegido por el usuario.
        self.fusion_mode_var = tk.StringVar(value="normal")
        # Esta variable indica si se resaltan zonas claras, oscuras o ninguna.
        self.zone_mode_var = tk.StringVar(value="none")
        # Esta variable indica si el canal rojo se mantiene activo.
        self.rgb_red_var = tk.BooleanVar(value=True)
        # Esta variable indica si el canal verde se mantiene activo.
        self.rgb_green_var = tk.BooleanVar(value=True)
        # Esta variable indica si el canal azul se mantiene activo.
        self.rgb_blue_var = tk.BooleanVar(value=True)
        # Esta variable indica si se desea mostrar el canal cian.
        self.cmy_cyan_var = tk.BooleanVar(value=False)
        # Esta variable indica si se desea mostrar el canal magenta.
        self.cmy_magenta_var = tk.BooleanVar(value=False)
        # Esta variable indica si se desea mostrar el canal amarillo.
        self.cmy_yellow_var = tk.BooleanVar(value=False)
        # Esta variable guarda el factor de zoom aplicado a la vista.
        self.zoom_scale_var = tk.DoubleVar(value=1.0)
        # Esta variable guarda el umbral usado por la binarizacion.
        self.threshold_var = tk.IntVar(value=128)
        # Esta variable indica si se aplica el filtro de binarizacion.
        self.apply_binary_var = tk.BooleanVar(value=False)
        # Esta variable indica si se aplica el negativo de imagen.
        self.apply_negative_var = tk.BooleanVar(value=False)

        # Esta referencia evita que Tkinter libere la imagen mostrada.
        self.display_image = None

        # Se construye toda la interfaz grafica al crear la clase.
        self._build_layout()

    def _build_layout(self):
        """Construye visualmente la ventana y todos sus controles."""
        # Se define un tamano inicial comodo para trabajar en escritorio.
        self.root.geometry("1100x650")

        # Se crea un frame superior para contener el titulo.
        title_frame = ttk.Frame(self.root)
        # Se posiciona el frame del titulo en la parte superior.
        title_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

        # Se crea la etiqueta grande que identifica al programa.
        title_label = ttk.Label(
            title_frame,
            text="Visor de Imágenes",
            anchor="center",
            foreground="red",
            font=("Arial", 18, "bold"),
        )
        # Se expande la etiqueta para que quede centrada horizontalmente.
        title_label.pack(fill=tk.X)

        # Se crea el frame que agrupa ruta y botones de archivo.
        path_frame = ttk.Frame(self.root)
        # Se ubica este frame debajo del titulo.
        path_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

        # Se crea la etiqueta que describe el campo de ruta.
        path_label = ttk.Label(path_frame, text="Archivo de imagen:")
        # Se coloca la etiqueta a la izquierda.
        path_label.pack(side=tk.LEFT)

        # Se crea el campo de texto que muestra la ruta seleccionada.
        path_entry = ttk.Entry(path_frame, textvariable=self.image_path_var)
        # Se deja expandible para aprovechar el ancho disponible.
        path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        # Se crea el boton para abrir el explorador de archivos.
        explore_button = ttk.Button(path_frame, text="Explorar", command=self._on_explore)
        # Se coloca el boton junto al campo de texto.
        explore_button.pack(side=tk.LEFT, padx=2)

        # Se crea el boton para cargar la imagen principal.
        load_button = ttk.Button(path_frame, text="Cargar", command=self._on_load)
        # Se coloca el boton junto al boton de explorar.
        load_button.pack(side=tk.LEFT, padx=2)

        # Se crea el boton para guardar la imagen procesada.
        save_button = ttk.Button(path_frame, text="Guardar", command=self._on_save)
        # Se ubica a continuacion de los controles anteriores.
        save_button.pack(side=tk.LEFT, padx=2)

        # Se crea el boton que permite seleccionar una segunda imagen.
        fusion_button = ttk.Button(
            path_frame,
            text="Fusionar Imágenes",
            command=self._on_load_second_image,
        )
        # Se coloca el boton de fusion dentro de la misma fila superior.
        fusion_button.pack(side=tk.LEFT, padx=2)

        # Se crea el contenedor principal que separa visor y controles.
        main_frame = ttk.Frame(self.root)
        # Se hace expandible para ocupar el resto de la ventana.
        main_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Se crea el frame donde se mostrara la imagen.
        image_frame = ttk.Frame(main_frame)
        # Se ubica a la izquierda y se le permite crecer.
        image_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        # Se asigna peso a la columna para que el canvas se redimensione.
        image_frame.columnconfigure(0, weight=1)
        # Se asigna peso a la fila principal del canvas.
        image_frame.rowconfigure(0, weight=1)

        # Se crea el canvas que actuara como area de visualizacion.
        self.canvas = tk.Canvas(image_frame, bg="white")
        # Se coloca el canvas ocupando toda la celda disponible.
        self.canvas.grid(row=0, column=0, sticky="nsew")
        # Se vincula el cambio de tamano del canvas para redibujar la imagen.
        self.canvas.bind("<Configure>", self._on_canvas_resize)

        # Se crea la barra horizontal para navegar la imagen ampliada.
        self.horizontal_scrollbar = ttk.Scrollbar(
            image_frame,
            orient=tk.HORIZONTAL,
            command=self.canvas.xview,
        )
        # Se crea la barra vertical para navegar la imagen ampliada.
        self.vertical_scrollbar = ttk.Scrollbar(
            image_frame,
            orient=tk.VERTICAL,
            command=self.canvas.yview,
        )
        # Se conecta el canvas con ambas barras de desplazamiento.
        self.canvas.configure(
            xscrollcommand=self.horizontal_scrollbar.set,
            yscrollcommand=self.vertical_scrollbar.set,
        )
        # Se reserva la fila inferior para la barra horizontal.
        self.horizontal_scrollbar.grid(row=1, column=0, sticky="ew")
        # Se reserva la columna derecha para la barra vertical.
        self.vertical_scrollbar.grid(row=0, column=1, sticky="ns")
        # Se oculta la barra horizontal mientras no sea necesaria.
        self.horizontal_scrollbar.grid_remove()
        # Se oculta la barra vertical mientras no sea necesaria.
        self.vertical_scrollbar.grid_remove()

        # Se crea el panel lateral donde iran todos los controles.
        controls_frame = ttk.Frame(main_frame, width=260)
        # Se coloca el panel a la derecha del visor.
        controls_frame.pack(side=tk.RIGHT, fill=tk.Y)

        # Se crea la etiqueta del control de brillo.
        brightness_label = ttk.Label(controls_frame, text="Brillo:")
        # Se alinea la etiqueta a la izquierda del panel.
        brightness_label.pack(anchor="w", pady=(0, 2))
        # Se crea el slider que modifica el brillo de la imagen.
        brightness_scale = ttk.Scale(
            controls_frame,
            from_=-100,
            to=100,
            orient=tk.HORIZONTAL,
            variable=self.brightness_var,
            command=self._on_live_change,
        )
        # Se expande el slider a lo ancho del panel.
        brightness_scale.pack(fill=tk.X, pady=(0, 5))

        # Se crea la etiqueta del control de contraste.
        contrast_label = ttk.Label(controls_frame, text="Contraste:")
        # Se coloca la etiqueta sobre su slider correspondiente.
        contrast_label.pack(anchor="w", pady=(0, 2))
        # Se crea el slider que modifica el contraste.
        contrast_scale = ttk.Scale(
            controls_frame,
            from_=-100,
            to=100,
            orient=tk.HORIZONTAL,
            variable=self.contrast_var,
            command=self._on_live_change,
        )
        # Se posiciona el slider en el panel lateral.
        contrast_scale.pack(fill=tk.X, pady=(0, 5))

        # Se crea la etiqueta del control de rotacion.
        rotation_label = ttk.Label(controls_frame, text="Rotación (°):")
        # Se agrega un espacio superior para separar visualmente este grupo.
        rotation_label.pack(anchor="w", pady=(5, 2))
        # Se crea el slider que controla el angulo de rotacion.
        rotation_scale = ttk.Scale(
            controls_frame,
            from_=0,
            to=360,
            orient=tk.HORIZONTAL,
            variable=self.rotation_var,
            command=self._on_live_change,
        )
        # Se dibuja el slider de rotacion.
        rotation_scale.pack(fill=tk.X, pady=(0, 5))

        # Se crea la etiqueta del control de fusion.
        fusion_label = ttk.Label(controls_frame, text="Transparencia Fusión:")
        # Se ubica la etiqueta antes del slider de fusion.
        fusion_label.pack(anchor="w", pady=(5, 2))
        # Se crea el slider que controla cuanto participa la segunda imagen.
        fusion_scale = ttk.Scale(
            controls_frame,
            from_=0.0,
            to=1.0,
            orient=tk.HORIZONTAL,
            variable=self.fusion_alpha_var,
            command=self._on_live_change,
        )
        # Se muestra el slider de fusion.
        fusion_scale.pack(fill=tk.X, pady=(0, 5))

        # Se crea la etiqueta del selector de modo de fusion.
        fusion_mode_label = ttk.Label(controls_frame, text="Modo de Fusión:")
        # Se coloca encima del desplegable de modos.
        fusion_mode_label.pack(anchor="w", pady=(0, 2))
        # Se crea un combobox con los modos disponibles de superposicion.
        fusion_mode_combo = ttk.Combobox(
            controls_frame,
            textvariable=self.fusion_mode_var,
            values=["normal", "multiplicacion", "adicion", "diferencia"],
            state="readonly",
        )
        # Se ubica el desplegable dentro del panel de controles.
        fusion_mode_combo.pack(fill=tk.X, pady=(0, 5))
        # Se actualiza la imagen cuando el usuario cambia el modo.
        fusion_mode_combo.bind("<<ComboboxSelected>>", self._on_entry_commit)

        # Se crea el grupo de botones para resaltar zonas.
        zones_frame = ttk.LabelFrame(controls_frame, text="Zonas")
        # Se ubica el grupo en el panel lateral.
        zones_frame.pack(fill=tk.X, pady=5)
        # Se crea la opcion para no aplicar filtro de zonas.
        no_zone_radio = ttk.Radiobutton(
            zones_frame,
            text="Sin filtro",
            value="none",
            variable=self.zone_mode_var,
            command=self._on_live_change,
        )
        # Se coloca la opcion dentro del grupo.
        no_zone_radio.pack(anchor="w")
        # Se crea la opcion para resaltar zonas claras.
        light_radio = ttk.Radiobutton(
            zones_frame,
            text="Zonas Claras",
            value="light",
            variable=self.zone_mode_var,
            command=self._on_live_change,
        )
        # Se posiciona el boton dentro del grupo.
        light_radio.pack(anchor="w")
        # Se crea la opcion para resaltar zonas oscuras.
        dark_radio = ttk.Radiobutton(
            zones_frame,
            text="Zonas Oscuras",
            value="dark",
            variable=self.zone_mode_var,
            command=self._on_live_change,
        )
        # Se muestra el boton de zonas oscuras.
        dark_radio.pack(anchor="w")

        # Se crea el grupo de activacion de canales RGB.
        rgb_frame = ttk.LabelFrame(controls_frame, text="Canales RGB")
        # Se ubica el grupo en el panel lateral.
        rgb_frame.pack(fill=tk.X, pady=5)
        # Se crea el check del canal rojo.
        rgb_r = ttk.Checkbutton(
            rgb_frame,
            text="Rojo",
            variable=self.rgb_red_var,
            command=self._on_live_change,
        )
        # Se muestra el check del canal rojo.
        rgb_r.pack(anchor="w")
        # Se crea el check del canal verde.
        rgb_g = ttk.Checkbutton(
            rgb_frame,
            text="Verde",
            variable=self.rgb_green_var,
            command=self._on_live_change,
        )
        # Se muestra el check del canal verde.
        rgb_g.pack(anchor="w")
        # Se crea el check del canal azul.
        rgb_b = ttk.Checkbutton(
            rgb_frame,
            text="Azul",
            variable=self.rgb_blue_var,
            command=self._on_live_change,
        )
        # Se muestra el check del canal azul.
        rgb_b.pack(anchor="w")

        # Se crea el grupo de activacion de canales CMY.
        cmy_frame = ttk.LabelFrame(controls_frame, text="Canales CMY")
        # Se posiciona el grupo debajo de RGB.
        cmy_frame.pack(fill=tk.X, pady=5)
        # Se crea el check del canal cian.
        cmy_c = ttk.Checkbutton(
            cmy_frame,
            text="Cian",
            variable=self.cmy_cyan_var,
            command=self._on_live_change,
        )
        # Se muestra el check del canal cian.
        cmy_c.pack(anchor="w")
        # Se crea el check del canal magenta.
        cmy_m = ttk.Checkbutton(
            cmy_frame,
            text="Magenta",
            variable=self.cmy_magenta_var,
            command=self._on_live_change,
        )
        # Se muestra el check del canal magenta.
        cmy_m.pack(anchor="w")
        # Se crea el check del canal amarillo.
        cmy_y = ttk.Checkbutton(
            cmy_frame,
            text="Amarillo",
            variable=self.cmy_yellow_var,
            command=self._on_live_change,
        )
        # Se muestra el check del canal amarillo.
        cmy_y.pack(anchor="w")

        # Se crea el grupo visual del zoom.
        zoom_frame = ttk.LabelFrame(controls_frame, text="Zoom")
        # Se ubica el grupo en el panel lateral.
        zoom_frame.pack(fill=tk.X, pady=5)
        # Se crea un frame interno para alinear botones y etiqueta.
        zoom_controls_frame = ttk.Frame(zoom_frame)
        # Se muestra el frame interno de controles.
        zoom_controls_frame.pack(fill=tk.X, pady=2)
        # Se crea el boton para reducir el zoom.
        zoom_out_button = ttk.Button(zoom_controls_frame, text="-", width=4, command=self._zoom_out)
        # Se coloca a la izquierda del grupo de zoom.
        zoom_out_button.pack(side=tk.LEFT)
        # Se crea la etiqueta que muestra el porcentaje actual de zoom.
        self.zoom_label = ttk.Label(zoom_controls_frame, text="100%", anchor="center")
        # Se deja la etiqueta expandible para que quede centrada.
        self.zoom_label.pack(side=tk.LEFT, expand=True, padx=6)
        # Se crea el boton que restaura el zoom al 100 por ciento.
        zoom_reset_button = ttk.Button(zoom_controls_frame, text="100%", width=6, command=self._zoom_reset)
        # Se ubica el boton de restauracion de zoom.
        zoom_reset_button.pack(side=tk.LEFT, padx=2)
        # Se crea el boton para aumentar el zoom.
        zoom_in_button = ttk.Button(zoom_controls_frame, text="+", width=4, command=self._zoom_in)
        # Se coloca el boton de aumentar a la derecha.
        zoom_in_button.pack(side=tk.LEFT)

        # Se crea el grupo de binarizacion y negativo.
        binary_frame = ttk.LabelFrame(controls_frame, text="Binarización y Negativo")
        # Se ubica este grupo en el panel lateral.
        binary_frame.pack(fill=tk.X, pady=5)
        # Se crea el check para activar la binarizacion.
        binary_check = ttk.Checkbutton(
            binary_frame,
            text="Binarizar",
            variable=self.apply_binary_var,
            command=self._on_live_change,
        )
        # Se muestra el check en el grupo.
        binary_check.pack(anchor="w")
        # Se crea la etiqueta que describe el slider de umbral.
        threshold_label = ttk.Label(binary_frame, text="Umbral:")
        # Se ubica encima del slider.
        threshold_label.pack(anchor="w")
        # Se crea el slider que define el umbral de binarizacion.
        threshold_scale = ttk.Scale(
            binary_frame,
            from_=0,
            to=255,
            orient=tk.HORIZONTAL,
            variable=self.threshold_var,
            command=self._on_live_change,
        )
        # Se muestra el slider dentro del grupo.
        threshold_scale.pack(fill=tk.X, pady=(0, 4))
        # Se crea la etiqueta que refleja numericamente el umbral.
        self.threshold_value_label = ttk.Label(binary_frame, text="128")
        # Se muestra la etiqueta del valor del umbral.
        self.threshold_value_label.pack(anchor="w")
        # Se crea el check para activar el negativo.
        negative_check = ttk.Checkbutton(
            binary_frame,
            text="Negativo",
            variable=self.apply_negative_var,
            command=self._on_live_change,
        )
        # Se muestra el check de negativo.
        negative_check.pack(anchor="w")

        # Se crea el frame inferior para acciones globales.
        bottom_frame = ttk.Frame(self.root)
        # Se coloca este frame en la parte inferior de la ventana.
        bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=5)

        # Se crea el boton que fuerza una actualizacion manual.
        update_button = ttk.Button(bottom_frame, text="Actualizar", command=self._on_update)
        # Se ubica a la izquierda del frame inferior.
        update_button.pack(side=tk.LEFT)

        # Se crea el boton para volver a la imagen original.
        restore_button = ttk.Button(
            bottom_frame,
            text="Restaurar Original",
            command=self._on_restore_original,
        )
        # Se coloca a continuacion del boton actualizar.
        restore_button.pack(side=tk.LEFT, padx=5)

        # Se crea el boton que abre la ventana del histograma.
        histogram_button = ttk.Button(bottom_frame, text="Histograma", command=self._on_histogram)
        # Se coloca junto a los otros botones de accion.
        histogram_button.pack(side=tk.LEFT, padx=5)

    def _on_explore(self):
        """Abre el explorador de archivos para elegir la imagen principal."""
        # Se define el filtro de extensiones permitidas.
        filetypes = [("Imágenes", "*.jpg *.jpeg *.png *.bmp"), ("Todos los archivos", "*.*")]
        # Se abre el cuadro de dialogo para seleccionar un archivo.
        filename = filedialog.askopenfilename(title="Seleccionar imagen", filetypes=filetypes)
        # Si el usuario eligio un archivo, se actualiza la ruta visible.
        if filename:
            self.image_path_var.set(filename)

    def _on_load(self):
        """Carga la imagen principal seleccionada y la muestra en pantalla."""
        # Se obtiene la ruta escrita o seleccionada por el usuario.
        path = self.image_path_var.get().strip()
        # Si no hay ruta, se informa el error y se cancela la operacion.
        if not path:
            messagebox.showerror("Error", "Seleccione un archivo de imagen.")
            return

        try:
            # Se pide al procesador cargar la imagen principal.
            array = self.processor.load_main_image(path)
        except Exception as exc:
            # Si falla la carga, se muestra el detalle del error.
            messagebox.showerror("Error", f"No se pudo cargar la imagen.\n{exc}")
            return

        # Se dibuja la imagen cargada en el canvas.
        self._show_array_on_canvas(array)
        # Se ejecuta una actualizacion inicial para sincronizar todos los controles.
        self._on_update(show_errors=False)

    def _on_save(self):
        """Guarda en disco la imagen procesada actual."""
        # Si no existe imagen procesada, no tiene sentido guardar.
        if self.processor.image_array is None:
            messagebox.showerror("Error", "No hay imagen para guardar.")
            return

        # Se definen los formatos disponibles para guardar.
        filetypes = [("Imagen PNG", "*.png"), ("Imagen JPG", "*.jpg *.jpeg"), ("Bitmap", "*.bmp")]
        # Se abre el cuadro de dialogo para elegir nombre y ruta de salida.
        filename = filedialog.asksaveasfilename(
            title="Guardar imagen",
            defaultextension=".png",
            filetypes=filetypes,
        )
        # Si el usuario cancela, se abandona la operacion.
        if not filename:
            return

        try:
            # Se delega al procesador la escritura de la imagen.
            self.processor.save_image(filename)
        except Exception as exc:
            # Si ocurre un fallo, se informa en pantalla.
            messagebox.showerror("Error", f"No se pudo guardar la imagen.\n{exc}")

    def _on_load_second_image(self):
        """Carga una segunda imagen para realizar fusion."""
        # Se reutiliza el mismo filtro de formatos soportados.
        filetypes = [("Imágenes", "*.jpg *.jpeg *.png *.bmp"), ("Todos los archivos", "*.*")]
        # Se abre el dialogo de seleccion para la imagen secundaria.
        filename = filedialog.askopenfilename(
            title="Seleccionar segunda imagen",
            filetypes=filetypes,
        )
        # Si no se selecciona archivo, se cancela el proceso.
        if not filename:
            return

        try:
            # Se carga la segunda imagen en el procesador.
            self.processor.load_second_image(filename)
        except Exception as exc:
            # Si la carga falla, se muestra un mensaje descriptivo.
            messagebox.showerror("Error", f"No se pudo cargar la segunda imagen.\n{exc}")
            return

        # Se actualiza la vista para aplicar la fusion si corresponde.
        self._on_update(show_errors=False)
        # Se confirma al usuario que la segunda imagen ya esta lista.
        messagebox.showinfo("Información", "Segunda imagen cargada para la fusión.")

    def _on_update(self, show_errors=True):
        """Lee los controles actuales y recalcula la imagen mostrada."""
        # Si aun no hay imagen principal, no se intenta procesar nada.
        if self.processor.original_image_array is None:
            return

        try:
            # Se construye un diccionario simple con todos los parametros.
            config = self._build_processing_config()
            # Se aplica la cadena completa de transformaciones.
            array = self.processor.apply_transformations(config)
        except Exception as exc:
            # Si se permite mostrar errores, se informa el problema al usuario.
            if show_errors:
                messagebox.showerror("Error", f"No se pudo actualizar la imagen.\n{exc}")
            return

        # Se refresca la imagen visible en el canvas.
        self._show_array_on_canvas(array)

    def _on_histogram(self):
        """Solicita al procesador mostrar el histograma actual."""
        try:
            # Se genera y visualiza el histograma de la imagen procesada.
            self.processor.show_histogram()
        except Exception as exc:
            # Si algo falla, se muestra un cuadro de error.
            messagebox.showerror("Error", f"No se pudo generar el histograma.\n{exc}")

    def _on_restore_original(self):
        """Restaura la imagen original y reinicia los controles."""
        try:
            # Se recupera una copia limpia de la imagen original.
            array = self.processor.restore_original_image()
        except Exception as exc:
            # Si no existe una imagen cargada, se informa el problema.
            messagebox.showerror("Error", f"No se pudo restaurar la imagen.\n{exc}")
            return

        # Se reinician los controles al estado base del programa.
        self._reset_controls()
        # Se redibuja la imagen original en pantalla.
        self._show_array_on_canvas(array)

    def _build_processing_config(self):
        """Empaqueta todos los valores de la interfaz en un diccionario."""
        # Se devuelve un diccionario plano y facil de consumir por el procesador.
        return {
            # Se redondea y convierte el brillo a entero.
            "brightness": int(round(self.brightness_var.get())),
            # Se redondea y convierte el contraste a entero.
            "contrast": int(round(self.contrast_var.get())),
            # Se redondea la rotacion para trabajar con grados enteros.
            "rotation": int(round(self.rotation_var.get())),
            # Se obtiene el valor actual del control de fusion.
            "fusion_alpha": float(self.fusion_alpha_var.get()),
            # Se obtiene el modo de superposicion elegido.
            "fusion_mode": self.fusion_mode_var.get(),
            # Se obtiene el filtro actual de zonas.
            "zone_mode": self.zone_mode_var.get(),
            # Se consulta si el canal rojo esta activo.
            "rgb_red": self.rgb_red_var.get(),
            # Se consulta si el canal verde esta activo.
            "rgb_green": self.rgb_green_var.get(),
            # Se consulta si el canal azul esta activo.
            "rgb_blue": self.rgb_blue_var.get(),
            # Se consulta si el canal cian esta activo.
            "cmy_cyan": self.cmy_cyan_var.get(),
            # Se consulta si el canal magenta esta activo.
            "cmy_magenta": self.cmy_magenta_var.get(),
            # Se consulta si el canal amarillo esta activo.
            "cmy_yellow": self.cmy_yellow_var.get(),
            # Se obtiene el factor de zoom de la vista.
            "zoom_scale": float(self.zoom_scale_var.get()),
            # Se obtiene el umbral de binarizacion.
            "threshold": int(self.threshold_var.get()),
            # Se indica si se aplica binarizacion.
            "apply_binary": self.apply_binary_var.get(),
            # Se indica si se aplica el negativo.
            "apply_negative": self.apply_negative_var.get(),
        }

    def _on_live_change(self, _value=None):
        """Actualiza la vista cuando cambia un slider o check."""
        # Se refrescan las etiquetas numericas visibles.
        self._refresh_status_labels()
        # Se recalcula la imagen sin mostrar errores emergentes menores.
        self._on_update(show_errors=False)

    def _on_entry_commit(self, _event=None):
        """Actualiza la vista al confirmar un valor de lista."""
        # Se reutiliza el mismo flujo de actualizacion en vivo.
        self._on_live_change()

    def _on_canvas_resize(self, _event=None):
        """Redibuja la imagen cuando cambia el tamano del canvas."""
        # Solo se redibuja si ya existe una imagen procesada cargada.
        if self.processor.image_array is not None:
            self._show_array_on_canvas(self.processor.image_array)

    def _zoom_in(self):
        """Aumenta el zoom de la vista en pasos de 25 por ciento."""
        # Se obtiene el nivel actual de zoom.
        current_scale = self.zoom_scale_var.get()
        # Se incrementa el zoom con un limite superior para evitar excesos.
        self.zoom_scale_var.set(min(4.0, current_scale + 0.25))
        # Se actualiza la interfaz y la imagen visible.
        self._on_live_change()

    def _zoom_out(self):
        """Disminuye el zoom de la vista en pasos de 25 por ciento."""
        # Se obtiene el nivel actual de zoom.
        current_scale = self.zoom_scale_var.get()
        # Se reduce el zoom con un limite inferior para no desaparecer la imagen.
        self.zoom_scale_var.set(max(0.25, current_scale - 0.25))
        # Se aplica el cambio inmediatamente.
        self._on_live_change()

    def _zoom_reset(self):
        """Restablece el zoom al 100 por ciento."""
        # Se fija la escala de zoom en el valor base.
        self.zoom_scale_var.set(1.0)
        # Se actualiza la vista del canvas.
        self._on_live_change()

    def _refresh_status_labels(self):
        """Sincroniza etiquetas numericas de zoom y umbral."""
        # Se convierte el zoom actual a porcentaje entero.
        zoom_percent = int(round(self.zoom_scale_var.get() * 100))
        # Se redondea el valor actual del umbral para mostrarlo.
        threshold_value = int(round(self.threshold_var.get()))
        # Se actualiza el texto de la etiqueta de zoom.
        self.zoom_label.config(text=f"{zoom_percent}%")
        # Se actualiza el texto de la etiqueta de umbral.
        self.threshold_value_label.config(text=str(threshold_value))

    def _reset_controls(self):
        """Devuelve todos los controles al estado inicial del visor."""
        # Se restaura el brillo al valor neutro.
        self.brightness_var.set(0)
        # Se restaura el contraste al valor neutro.
        self.contrast_var.set(0)
        # Se reinicia la rotacion a cero grados.
        self.rotation_var.set(0)
        # Se elimina la presencia de la segunda imagen en la fusion.
        self.fusion_alpha_var.set(0.0)
        # Se vuelve al modo de fusion basico.
        self.fusion_mode_var.set("normal")
        # Se desactiva cualquier resaltado de zonas.
        self.zone_mode_var.set("none")
        # Se reactiva el canal rojo.
        self.rgb_red_var.set(True)
        # Se reactiva el canal verde.
        self.rgb_green_var.set(True)
        # Se reactiva el canal azul.
        self.rgb_blue_var.set(True)
        # Se desactiva el canal cian.
        self.cmy_cyan_var.set(False)
        # Se desactiva el canal magenta.
        self.cmy_magenta_var.set(False)
        # Se desactiva el canal amarillo.
        self.cmy_yellow_var.set(False)
        # Se restablece el zoom al 100 por ciento.
        self.zoom_scale_var.set(1.0)
        # Se devuelve el umbral al valor medio.
        self.threshold_var.set(128)
        # Se desactiva la binarizacion.
        self.apply_binary_var.set(False)
        # Se desactiva el negativo.
        self.apply_negative_var.set(False)
        # Se actualizan las etiquetas asociadas a estos valores.
        self._refresh_status_labels()

    def _show_array_on_canvas(self, array):
        """Convierte un arreglo en imagen visible y la dibuja en el canvas."""
        # Si no se recibe una imagen valida, no se hace nada.
        if array is None:
            return

        # Se obtiene la altura original de la imagen.
        height = array.shape[0]
        # Se obtiene el ancho original de la imagen.
        width = array.shape[1]
        # Se consulta el ancho actual disponible en el canvas.
        canvas_width = self.canvas.winfo_width()
        # Se consulta el alto actual disponible en el canvas.
        canvas_height = self.canvas.winfo_height()

        # Si el canvas aun no tiene tamano util, se usan valores de respaldo.
        if canvas_width <= 1 or canvas_height <= 1:
            # Se usa un ancho estimado para el primer dibujo.
            canvas_width = 800
            # Se usa una altura estimada para el primer dibujo.
            canvas_height = 500

        # Se calcula la escala base que hace encajar la imagen en el canvas.
        base_scale = min(canvas_width / width, canvas_height / height)
        # Se obtiene el nivel de zoom definido por el usuario.
        zoom_scale = float(self.zoom_scale_var.get())
        # Se calcula la escala final combinando ajuste base y zoom.
        display_scale = base_scale * zoom_scale
        # Se calcula el ancho final que tendra la imagen en pantalla.
        new_width = max(1, int(width * display_scale))
        # Se calcula el alto final que tendra la imagen en pantalla.
        new_height = max(1, int(height * display_scale))

        # Se convierte el arreglo NumPy en una imagen PIL.
        image = Image.fromarray(array)
        # Se redimensiona la imagen segun la escala calculada.
        image = image.resize((new_width, new_height), Image.LANCZOS)
        # Se convierte la imagen PIL en un objeto compatible con Tkinter.
        self.display_image = ImageTk.PhotoImage(image)

        # Se limpia cualquier contenido previo del canvas.
        self.canvas.delete("all")
        # Se decide si hacen falta scrollbars cuando el zoom supera el tamano visible.
        use_scrollbars = zoom_scale > 1.0 and (new_width > canvas_width or new_height > canvas_height)

        # Si la imagen ampliada ya no cabe en el visor, se activa navegacion.
        if use_scrollbars:
            # Se muestran las barras de desplazamiento.
            self._set_scrollbars_visibility(True)
            # Se dibuja la imagen desde la esquina superior izquierda.
            self.canvas.create_image(0, 0, image=self.display_image, anchor="nw")
            # Se actualiza la region desplazable del canvas.
            self.canvas.configure(scrollregion=(0, 0, new_width, new_height))
            # Se centra la vista inicial sobre la imagen ampliada.
            self._center_canvas_view(new_width, new_height, canvas_width, canvas_height)
        else:
            # Si no se necesitan scrollbars, se ocultan.
            self._set_scrollbars_visibility(False)
            # Se dibuja la imagen centrada dentro del canvas.
            self.canvas.create_image(
                canvas_width // 2,
                canvas_height // 2,
                image=self.display_image,
                anchor="center",
            )
            # Se redefine la region visible para el tamano actual del canvas.
            self.canvas.configure(scrollregion=(0, 0, canvas_width, canvas_height))
            # Se asegura que el desplazamiento horizontal vuelva al inicio.
            self.canvas.xview_moveto(0)
            # Se asegura que el desplazamiento vertical vuelva al inicio.
            self.canvas.yview_moveto(0)

    def _set_scrollbars_visibility(self, visible):
        """Muestra u oculta las barras de desplazamiento del visor."""
        # Si el parametro es verdadero, se muestran ambas barras.
        if visible:
            self.horizontal_scrollbar.grid()
            self.vertical_scrollbar.grid()
        else:
            # Si el parametro es falso, se ocultan ambas barras.
            self.horizontal_scrollbar.grid_remove()
            self.vertical_scrollbar.grid_remove()

    def _center_canvas_view(self, content_width, content_height, view_width, view_height):
        """Centra la ventana visible del canvas sobre la imagen ampliada."""
        # Si el contenido es mas ancho que el area visible, se centra horizontalmente.
        if content_width > view_width:
            # Se calcula el desplazamiento maximo posible en horizontal.
            max_offset_x = content_width - view_width
            # Se toma la mitad para dejar la vista centrada.
            offset_x = max_offset_x / 2.0
            # Se mueve la vista horizontalmente usando proporcion del contenido.
            self.canvas.xview_moveto(offset_x / content_width)
        else:
            # Si no sobra ancho, el desplazamiento horizontal vuelve al inicio.
            self.canvas.xview_moveto(0)

        # Si el contenido es mas alto que el area visible, se centra verticalmente.
        if content_height > view_height:
            # Se calcula el desplazamiento maximo posible en vertical.
            max_offset_y = content_height - view_height
            # Se toma la mitad para dejar la vista centrada.
            offset_y = max_offset_y / 2.0
            # Se mueve la vista verticalmente usando proporcion del contenido.
            self.canvas.yview_moveto(offset_y / content_height)
        else:
            # Si no sobra alto, el desplazamiento vertical vuelve al inicio.
            self.canvas.yview_moveto(0)
