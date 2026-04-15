import os
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk

from PIL import Image, ImageTk

from libs.image_processing import process_image
from libs.histogram import show_histogram


"""
Aplicación principal del visor y editor de imágenes.

Este módulo contiene la clase VisorImagenes, responsable de:
- Construir la interfaz gráfica con Tkinter.
- Cargar y gestionar múltiples imágenes.
- Aplicar transformaciones usando las funciones de libs.image_processing.
- Mostrar histogramas a través de libs.histogram.
- Gestionar herramientas interactivas como zoom, rotación y fusión.
"""


class VisorImagenes:
    def __init__(self, root: tk.Tk) -> None:
        """
        Inicializa el visor, variables de estado y crea todos los widgets.

        Parámetros:
            root: instancia principal de Tk sobre la que se monta la interfaz.
        """
        self.root = root
        self.root.title("Visor de Imágenes")
        self.root.geometry("900x600")

        self.image_paths: list[str] = []
        self.current_index: int = -1
        self.current_image_original: Image.Image | None = None
        self.current_image_display: Image.Image | None = None
        self.photo_image: ImageTk.PhotoImage | None = None
        self.zoom_factor: float = 1.0
        self.fit_to_window: bool = True
        self.rotation: int = 0

        self.source_image: Image.Image | None = None
        self.blend_image: Image.Image | None = None

        self.file_path_var = tk.StringVar()
        self.brightness_var = tk.IntVar(value=0)
        self.contrast_var = tk.IntVar(value=0)
        self.zone_mode = tk.StringVar(value="ninguna")
        self.type_var = tk.StringVar(value="Original")
        self.channel_r = tk.BooleanVar(value=True)
        self.channel_g = tk.BooleanVar(value=True)
        self.channel_b = tk.BooleanVar(value=True)
        self.channel_cyan = tk.BooleanVar(value=False)
        self.channel_magenta = tk.BooleanVar(value=False)
        self.channel_yellow = tk.BooleanVar(value=False)
        self.blend_alpha_var = tk.DoubleVar(value=0.0)
        self.blend_mode_var = tk.StringVar(value="Normal")

        self.canvas: tk.Canvas | None = None
        self.status_label: tk.Label | None = None
        self.zoom_label: tk.Label | None = None

        self.create_widgets()
        self.update_zoom_label()
        self.bind_shortcuts()

    def create_widgets(self) -> None:
        """
        Crea y distribuye todos los elementos gráficos de la ventana:
        - Panel superior con título y ruta del archivo.
        - Canvas central para visualizar la imagen.
        - Panel lateral con controles de edición.
        - Barra inferior con navegación y zoom.
        - Barra de estado al pie.
        """
        self.root.rowconfigure(0, weight=0)
        self.root.rowconfigure(1, weight=1)
        self.root.rowconfigure(2, weight=0)
        self.root.rowconfigure(3, weight=0)
        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=0)

        top_frame = tk.Frame(self.root, bg="#f0f0f0")
        top_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=5)
        top_frame.columnconfigure(0, weight=0)
        top_frame.columnconfigure(1, weight=1)
        top_frame.columnconfigure(2, weight=0)

        title_label = tk.Label(top_frame, text="Visor de Imágenes", font=("Arial", 18, "bold"), fg="darkred", bg="#f0f0f0")
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 5))

        path_label = tk.Label(top_frame, text="Archivo de imagen:", bg="#f0f0f0")
        path_label.grid(row=1, column=0, sticky="w", padx=(0, 5))

        path_entry = tk.Entry(top_frame, textvariable=self.file_path_var)
        path_entry.grid(row=1, column=1, sticky="ew", padx=(0, 5))

        btn_explore = tk.Button(top_frame, text="Explorar", command=self.browse_file)
        btn_explore.grid(row=1, column=2)

        self.canvas = tk.Canvas(self.root, bg="black")
        self.canvas.grid(row=1, column=0, sticky="nsew", padx=(10, 5), pady=5)
        self.canvas.bind("<Configure>", self.on_canvas_resize)

        controls_frame = tk.Frame(self.root)
        controls_frame.grid(row=1, column=1, sticky="n", padx=(5, 10), pady=5)
        controls_frame.columnconfigure(0, weight=1)

        brightness_label = tk.Label(controls_frame, text="Brillo:")
        brightness_label.grid(row=0, column=0, sticky="w")
        brightness_scale = tk.Scale(controls_frame, from_=-100, to=100, orient="horizontal", variable=self.brightness_var)
        brightness_scale.grid(row=1, column=0, sticky="ew")

        contrast_label = tk.Label(controls_frame, text="Contraste:")
        contrast_label.grid(row=2, column=0, sticky="w", pady=(10, 0))
        contrast_scale = tk.Scale(controls_frame, from_=-100, to=100, orient="horizontal", variable=self.contrast_var)
        contrast_scale.grid(row=3, column=0, sticky="ew")

        zones_frame = tk.Frame(controls_frame)
        zones_frame.grid(row=4, column=0, sticky="w", pady=(10, 0))
        zones_label = tk.Label(zones_frame, text="Zonas:")
        zones_label.grid(row=0, column=0, sticky="w")
        rb_claras = tk.Radiobutton(zones_frame, text="Zonas Claras", variable=self.zone_mode, value="claras")
        rb_claras.grid(row=0, column=1, padx=(5, 0))
        rb_oscuras = tk.Radiobutton(zones_frame, text="Zonas Oscuras", variable=self.zone_mode, value="oscuras")
        rb_oscuras.grid(row=0, column=2, padx=(5, 0))

        type_label = tk.Label(controls_frame, text="Tipo:")
        type_label.grid(row=5, column=0, sticky="w", pady=(10, 0))
        type_combo = ttk.Combobox(controls_frame, textvariable=self.type_var, state="readonly")
        type_combo["values"] = ("Original", "Gris", "Negativo")
        type_combo.grid(row=6, column=0, sticky="ew")

        rgb_label = tk.Label(controls_frame, text="Canales RGB:")
        rgb_label.grid(row=7, column=0, sticky="w", pady=(10, 0))
        rgb_frame = tk.Frame(controls_frame)
        rgb_frame.grid(row=8, column=0, sticky="w")
        cb_r = tk.Checkbutton(rgb_frame, text="Red", variable=self.channel_r)
        cb_g = tk.Checkbutton(rgb_frame, text="Green", variable=self.channel_g)
        cb_b = tk.Checkbutton(rgb_frame, text="Blue", variable=self.channel_b)
        cb_r.grid(row=0, column=0, padx=(0, 5))
        cb_g.grid(row=0, column=1, padx=(0, 5))
        cb_b.grid(row=0, column=2, padx=(0, 5))

        cmy_label = tk.Label(controls_frame, text="Canales CMY:")
        cmy_label.grid(row=9, column=0, sticky="w", pady=(10, 0))
        cmy_frame = tk.Frame(controls_frame)
        cmy_frame.grid(row=10, column=0, sticky="w")
        cb_c = tk.Checkbutton(cmy_frame, text="Cyan", variable=self.channel_cyan)
        cb_m = tk.Checkbutton(cmy_frame, text="Magenta", variable=self.channel_magenta)
        cb_y = tk.Checkbutton(cmy_frame, text="Yellow", variable=self.channel_yellow)
        cb_c.grid(row=0, column=0, padx=(0, 5))
        cb_m.grid(row=0, column=1, padx=(0, 5))
        cb_y.grid(row=0, column=2, padx=(0, 5))

        rotation_label = tk.Label(controls_frame, text="Rotación:")
        rotation_label.grid(row=11, column=0, sticky="w", pady=(10, 0))
        rotation_frame = tk.Frame(controls_frame)
        rotation_frame.grid(row=12, column=0, sticky="w")
        btn_rot_left = tk.Button(rotation_frame, text="⟲", width=4, command=self.rotate_left)
        btn_rot_right = tk.Button(rotation_frame, text="⟳", width=4, command=self.rotate_right)
        btn_rot_left.grid(row=0, column=0, padx=(0, 5))
        btn_rot_right.grid(row=0, column=1, padx=(0, 5))

        fusion_label = tk.Label(controls_frame, text="Fusión de imágenes:")
        fusion_label.grid(row=13, column=0, sticky="w", pady=(10, 0))
        fusion_button = tk.Button(controls_frame, text="Cargar imagen de fusión", command=self.load_blend_image)
        fusion_button.grid(row=14, column=0, sticky="ew", pady=(2, 0))
        fusion_scale = tk.Scale(controls_frame, from_=0, to=100, orient="horizontal", label="Transparencia (%)", variable=self.blend_alpha_var)
        fusion_scale.grid(row=15, column=0, sticky="ew")
        blend_mode_label = tk.Label(controls_frame, text="Modo de fusión:")
        blend_mode_label.grid(row=16, column=0, sticky="w", pady=(5, 0))
        blend_mode_combo = ttk.Combobox(controls_frame, textvariable=self.blend_mode_var, state="readonly")
        blend_mode_combo["values"] = ("Normal", "Suma", "Multiplicar", "Promedio", "Diferencia")
        blend_mode_combo.grid(row=17, column=0, sticky="ew")

        btn_apply = tk.Button(controls_frame, text="Actualizar", command=self.apply_adjustments)
        btn_apply.grid(row=18, column=0, sticky="ew", pady=(15, 0))

        btn_undo = tk.Button(controls_frame, text="Deshacer cambios", command=self.undo_changes)
        btn_undo.grid(row=19, column=0, sticky="ew", pady=(5, 0))

        bottom_frame = tk.Frame(self.root)
        bottom_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=10, pady=(0, 5))
        bottom_frame.columnconfigure(0, weight=0)
        bottom_frame.columnconfigure(1, weight=1)

        nav_frame = tk.Frame(bottom_frame)
        nav_frame.grid(row=0, column=0, padx=5, pady=5)

        btn_first = tk.Button(nav_frame, text="<<", width=3, command=self.show_first)
        btn_prev = tk.Button(nav_frame, text="<", width=3, command=self.show_previous)
        btn_next = tk.Button(nav_frame, text=">", width=3, command=self.show_next)
        btn_last = tk.Button(nav_frame, text=">>", width=3, command=self.show_last)

        btn_first.grid(row=0, column=0, padx=2)
        btn_prev.grid(row=0, column=1, padx=2)
        btn_next.grid(row=0, column=2, padx=2)
        btn_last.grid(row=0, column=3, padx=2)

        zoom_frame = tk.Frame(bottom_frame)
        zoom_frame.grid(row=0, column=1, sticky="e", padx=5, pady=5)

        btn_zoom_out = tk.Button(zoom_frame, text="-", width=3, command=self.zoom_out)
        btn_zoom_reset = tk.Button(zoom_frame, text="100%", width=5, command=self.reset_zoom)
        btn_zoom_in = tk.Button(zoom_frame, text="+", width=3, command=self.zoom_in)

        btn_zoom_out.grid(row=0, column=0, padx=2)
        btn_zoom_reset.grid(row=0, column=1, padx=2)
        btn_zoom_in.grid(row=0, column=2, padx=2)

        self.zoom_label = tk.Label(zoom_frame, text="100%")
        self.zoom_label.grid(row=0, column=3, padx=5)

        self.status_label = tk.Label(self.root, text="Sin imagen", anchor="w")
        self.status_label.grid(row=3, column=0, columnspan=2, sticky="ew", padx=10, pady=(0, 5))

    def bind_shortcuts(self) -> None:
        """
        Asocia los atajos de teclado a las acciones principales del visor.
        """
        self.root.bind("<Right>", self.on_next_key)
        self.root.bind("<Left>", self.on_previous_key)
        self.root.bind("<Home>", self.on_first_key)
        self.root.bind("<End>", self.on_last_key)
        self.root.bind("<Control-o>", self.on_open_file_key)
        self.root.bind("<Control-O>", self.on_open_file_key)
        self.root.bind("<Control-q>", self.on_quit_key)
        self.root.bind("<Control-Q>", self.on_quit_key)
        self.root.bind("<plus>", self.on_zoom_in_key)
        self.root.bind("<minus>", self.on_zoom_out_key)

    def on_next_key(self, event: tk.Event) -> None:
        """
        Avanza a la siguiente imagen cuando se pulsa la tecla de flecha derecha.
        """
        self.show_next()

    def on_previous_key(self, event: tk.Event) -> None:
        """
        Retrocede a la imagen anterior cuando se pulsa la flecha izquierda.
        """
        self.show_previous()

    def on_first_key(self, event: tk.Event) -> None:
        """
        Salta a la primera imagen de la lista.
        """
        self.show_first()

    def on_last_key(self, event: tk.Event) -> None:
        """
        Salta a la última imagen de la lista.
        """
        self.show_last()

    def on_open_file_key(self, event: tk.Event) -> None:
        """
        Abre el cuadro de diálogo de archivo (Ctrl+O).
        """
        self.open_image_file()

    def on_quit_key(self, event: tk.Event) -> None:
        """
        Cierra la aplicación (Ctrl+Q).
        """
        self.root.quit()

    def on_zoom_in_key(self, event: tk.Event) -> None:
        """
        Acerca la imagen con el teclado (+).
        """
        self.zoom_in()

    def on_zoom_out_key(self, event: tk.Event) -> None:
        """
        Aleja la imagen con el teclado (-).
        """
        self.zoom_out()

    def on_canvas_resize(self, event: tk.Event) -> None:
        """
        Recalcula el renderizado de la imagen cuando cambia el tamaño del canvas.
        """
        if self.fit_to_window:
            self.update_image_display()

    def open_image_file(self) -> None:
        """
        Abre un cuadro de diálogo para seleccionar una sola imagen y la carga.
        """
        filetypes = [
            ("Imágenes", "*.jpg;*.jpeg;*.png;*.bmp;*.gif"),
            ("Todos los archivos", "*.*"),
        ]
        path = filedialog.askopenfilename(title="Abrir imagen", filetypes=filetypes)
        if not path:
            return
        self.file_path_var.set(path)
        self.set_single_image(path)

    def browse_file(self) -> None:
        """
        Permite seleccionar múltiples imágenes y las añade a la lista de navegación.
        """
        filetypes = [
            ("Imágenes", "*.jpg;*.jpeg;*.png;*.bmp;*.gif"),
            ("Todos los archivos", "*.*"),
        ]
        paths = filedialog.askopenfilenames(title="Seleccionar imágenes", filetypes=filetypes)
        if not paths:
            return
        path_list = list(paths)
        path_list = [p for p in path_list if os.path.isfile(p)]
        if not path_list:
            return
        self.image_paths = path_list
        self.current_index = 0
        self.file_path_var.set(path_list[0])
        self.load_current_image()

    def load_blend_image(self) -> None:
        """
        Carga una imagen secundaria que se utilizará para la fusión.
        """
        filetypes = [
            ("Imágenes", "*.jpg;*.jpeg;*.png;*.bmp;*.gif"),
            ("Todos los archivos", "*.*"),
        ]
        path = filedialog.askopenfilename(title="Seleccionar imagen de fusión", filetypes=filetypes)
        if not path:
            return
        if not os.path.isfile(path):
            return
        try:
            image = Image.open(path).convert("RGB")
        except Exception:
            messagebox.showerror("Error", "No se pudo abrir la imagen de fusión seleccionada.")
            return
        self.blend_image = image

    def load_from_entry(self) -> None:
        """
        Carga la imagen cuya ruta se ha escrito manualmente en la caja de texto.
        """
        path = self.file_path_var.get().strip()
        if not path:
            return
        if not os.path.isfile(path):
            messagebox.showerror("Error", "La ruta indicada no es un archivo válido.")
            return
        self.set_single_image(path)

    def set_single_image(self, path: str) -> None:
        """
        Configura el visor para trabajar solo con la imagen indicada.

        Parámetros:
            path: ruta absoluta o relativa del archivo de imagen.
        """
        if not path:
            return
        self.image_paths = [path]
        self.current_index = 0
        self.load_current_image()

    def open_image_folder(self) -> None:
        """
        Abre una carpeta y carga todas las imágenes compatibles que contenga.
        """
        directory = filedialog.askdirectory(title="Abrir carpeta de imágenes")
        if not directory:
            return
        extensions = {".jpg", ".jpeg", ".png", ".bmp", ".gif"}
        paths: list[str] = []
        for name in os.listdir(directory):
            full_path = os.path.join(directory, name)
            if not os.path.isfile(full_path):
                continue
            _, ext = os.path.splitext(name)
            if ext.lower() in extensions:
                paths.append(full_path)
        paths.sort()
        if not paths:
            messagebox.showinfo("Carpeta vacía", "La carpeta seleccionada no contiene imágenes compatibles.")
            return
        self.image_paths = paths
        self.current_index = 0
        self.load_current_image()

    def load_current_image(self) -> None:
        """
        Carga en memoria la imagen correspondiente al índice actual.
        Restablece todos los controles de edición y parámetros de visualización.
        """
        if not self.image_paths or self.current_index < 0 or self.current_index >= len(self.image_paths):
            return
        path = self.image_paths[self.current_index]
        try:
            image = Image.open(path).convert("RGB")
        except Exception as error:
            messagebox.showerror("Error", f"No se pudo abrir la imagen:\n{path}\n\n{error}")
            return
        self.source_image = image
        self.current_image_original = image
        self.brightness_var.set(0)
        self.contrast_var.set(0)
        self.zone_mode.set("ninguna")
        self.type_var.set("Original")
        self.channel_r.set(True)
        self.channel_g.set(True)
        self.channel_b.set(True)
        self.channel_cyan.set(False)
        self.channel_magenta.set(False)
        self.channel_yellow.set(False)
        self.rotation = 0
        self.zoom_factor = 1.0
        self.fit_to_window = True
        self.update_image_display()
        self.update_zoom_label()

    def update_image_display(self) -> None:
        """
        Redibuja la imagen en el canvas según el zoom, la rotación y el modo de ajuste.
        """
        if self.canvas is None:
            return
        if self.current_image_original is None:
            self.canvas.delete("all")
            if self.status_label is not None:
                self.status_label.config(text="Sin imagen")
            return

        self.root.update_idletasks()
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        if canvas_width <= 1 or canvas_height <= 1:
            return

        image = self.current_image_original
        if self.rotation != 0:
            image = image.rotate(self.rotation, expand=True)

        original_width, original_height = image.size

        if self.fit_to_window:
            ratio_w = canvas_width / original_width
            ratio_h = canvas_height / original_height
            ratio = min(ratio_w, ratio_h)
            scale = ratio * self.zoom_factor
        else:
            scale = self.zoom_factor

        if scale <= 0:
            scale = 0.01

        new_width = max(1, int(original_width * scale))
        new_height = max(1, int(original_height * scale))

        resized = image.resize((new_width, new_height), Image.LANCZOS)
        self.current_image_display = resized
        self.photo_image = ImageTk.PhotoImage(resized)

        self.canvas.delete("all")
        x = (canvas_width - new_width) // 2
        y = (canvas_height - new_height) // 2
        self.canvas.create_image(x, y, anchor="nw", image=self.photo_image)

        self.update_status(original_width, original_height)

    def update_status(self, original_width: int, original_height: int) -> None:
        """
        Actualiza la barra de estado con información de la imagen.

        Parámetros:
            original_width: ancho original de la imagen sin escalado.
            original_height: alto original de la imagen sin escalado.
        """
        if self.status_label is None:
            return
        if not self.image_paths or self.current_index < 0:
            self.status_label.config(text="Sin imagen")
            return
        path = self.image_paths[self.current_index]
        name = os.path.basename(path)
        position = self.current_index + 1
        total = len(self.image_paths)
        text = f"{name} ({original_width}x{original_height}) [{position} / {total}]"
        self.status_label.config(text=text)

    def update_zoom_label(self) -> None:
        """
        Actualiza el texto del indicador de zoom con el porcentaje actual.
        """
        if self.zoom_label is None:
            return
        percent = int(round(self.zoom_factor * 100))
        self.zoom_label.config(text=f"{percent}%")

    def undo_changes(self) -> None:
        """
        Restaura la imagen al estado original cargado desde disco y
        reinicia todos los controles de edición.
        """
        if self.source_image is None:
            return
        self.current_image_original = self.source_image
        self.brightness_var.set(0)
        self.contrast_var.set(0)
        self.zone_mode.set("ninguna")
        self.type_var.set("Original")
        self.channel_r.set(True)
        self.channel_g.set(True)
        self.channel_b.set(True)
        self.channel_cyan.set(False)
        self.channel_magenta.set(False)
        self.channel_yellow.set(False)
        self.blend_alpha_var.set(0.0)
        self.blend_mode_var.set("Normal")
        self.update_image_display()
        self.update_zoom_label()

    def apply_adjustments(self) -> None:
        """
        Construye la imagen procesada usando la librería de procesamiento
        y actualiza tanto el canvas como el histograma.
        """
        if self.source_image is None:
            return
        processed = process_image(
            source_image=self.source_image,
            brightness=self.brightness_var.get(),
            contrast=self.contrast_var.get(),
            zone_mode=self.zone_mode.get(),
            type_mode=self.type_var.get(),
            channel_r=self.channel_r.get(),
            channel_g=self.channel_g.get(),
            channel_b=self.channel_b.get(),
            channel_cyan=self.channel_cyan.get(),
            channel_magenta=self.channel_magenta.get(),
            channel_yellow=self.channel_yellow.get(),
            blend_image=self.blend_image,
            blend_alpha=self.blend_alpha_var.get(),
            blend_mode=self.blend_mode_var.get(),
        )
        self.current_image_original = processed
        self.update_image_display()
        self.update_zoom_label()
        show_histogram(
            processed,
            channel_cyan=self.channel_cyan.get(),
            channel_magenta=self.channel_magenta.get(),
            channel_yellow=self.channel_yellow.get(),
        )

    def show_next(self) -> None:
        """
        Muestra la siguiente imagen en la lista si existe.
        """
        if not self.image_paths:
            return
        if self.current_index < len(self.image_paths) - 1:
            self.current_index += 1
            self.load_current_image()

    def show_previous(self) -> None:
        """
        Muestra la imagen anterior en la lista si existe.
        """
        if not self.image_paths:
            return
        if self.current_index > 0:
            self.current_index -= 1
            self.load_current_image()

    def show_first(self) -> None:
        """
        Muestra la primera imagen de la lista.
        """
        if not self.image_paths:
            return
        if self.current_index != 0:
            self.current_index = 0
            self.load_current_image()

    def show_last(self) -> None:
        """
        Muestra la última imagen de la lista.
        """
        if not self.image_paths:
            return
        last_index = len(self.image_paths) - 1
        if self.current_index != last_index:
            self.current_index = last_index
            self.load_current_image()

    def zoom_in(self) -> None:
        """
        Incrementa el factor de zoom y redibuja la imagen.
        """
        if self.current_image_original is None:
            return
        self.zoom_factor *= 1.25
        self.update_image_display()
        self.update_zoom_label()

    def zoom_out(self) -> None:
        """
        Reduce el factor de zoom y redibuja la imagen.
        """
        if self.current_image_original is None:
            return
        self.zoom_factor /= 1.25
        self.update_image_display()
        self.update_zoom_label()

    def view_fit_to_window(self) -> None:
        """
        Activa el modo de ajuste a ventana y restablece el zoom.
        """
        if self.current_image_original is None:
            return
        self.reset_zoom()

    def view_real_size(self) -> None:
        """
        Muestra la imagen a tamaño real (1:1 píxel) dentro del canvas.
        """
        if self.current_image_original is None:
            return
        self.fit_to_window = False
        self.zoom_factor = 1.0
        self.update_image_display()
        self.update_zoom_label()

    def reset_zoom(self) -> None:
        """
        Restablece el zoom al 100% ajustado a la ventana.
        """
        if self.current_image_original is None:
            return
        self.fit_to_window = True
        self.zoom_factor = 1.0
        self.update_image_display()
        self.update_zoom_label()

    def rotate_right(self) -> None:
        """
        Rota la imagen 90 grados en sentido horario.
        """
        if self.current_image_original is None:
            return
        self.rotation = (self.rotation + 90) % 360
        self.update_image_display()

    def rotate_left(self) -> None:
        """
        Rota la imagen 90 grados en sentido antihorario.
        """
        if self.current_image_original is None:
            return
        self.rotation = (self.rotation - 90) % 360
        self.update_image_display()


def main() -> None:
    """
    Punto de entrada del programa cuando se ejecuta main.py directamente.
    """
    root = tk.Tk()
    VisorImagenes(root)
    root.mainloop()


if __name__ == "__main__":
    main()
