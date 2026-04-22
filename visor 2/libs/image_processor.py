import numpy as np
import matplotlib.pyplot as plt
from matplotlib import image as mpimg
from PIL import Image

class ImageProcessor:
    """Clase que agrupa las operaciones de carga, edicion y analisis."""

    def __init__(self):
        """Inicializa las referencias de trabajo del procesador."""
        self.original_image_array = None #imagen original sin modificaciones
        self.image_array = None #ultima version procesada de la imagen principal
        self.second_image_array = None #imagen para fusionar con la principal

    def load_main_image(self, path):
        """Carga la imagen principal desde disco."""
        array = mpimg.imread(path) #lee la imagen con matplotlib
        array = self._ensure_uint8_rgb(array) #normaliza la imagen a RGB uint8
        self.original_image_array = array #almacena una copia de la imagen original sin modificaciones
        self.image_array = array.copy() #almacena la imágena a trabajar
        return self.image_array

    def load_second_image(self, path):
        """Carga una segunda imagen para la fusion."""
        array = mpimg.imread(path) #lee la imagen con matplotlib
        array = self._ensure_uint8_rgb(array) #normaliza la imagen a RGB uint8
        self.second_image_array = array #almacena la imagen
        return array

    def restore_original_image(self):
        """Restaura la imagen principal a su estado original."""
        #si aun no hay imagen original, no se puede restaurar
        if self.original_image_array is None:
            raise ValueError("No hay imagen original para restaurar.")

        self.image_array = self.original_image_array.copy() #restaura la imágena a su estado original sin modificaciones
        return self.image_array

    def save_image(self, path, use_second=False):
        """Guarda la imagen principal o secundaria en disco."""
        if use_second: #usa la segunda imagen para guardarla si es solicitado
            array = self.second_image_array
        else: #si no, usa la imagen principal procesada
            array = self.image_array

        if array is None: #si hay una imagen disponible para guardar, lanza una excepcion
            raise ValueError("No hay imagen para guardar.")

        plt.imsave(path, array) #guarda la imágena en la ruta indicada con matplotlib

    def apply_transformations(self, config):
        """Aplica todas las transformaciones segun la configuracion recibida."""
        if self.original_image_array is None: #si no hay una imagen original, no se puede transformar
            raise ValueError("Primero debe cargar una imagen principal.")

        image = self.original_image_array.copy() #trabaja con una copia de la imagen original sin modificaciones, para evitar acumulaciones

        #aplica los ajustes
        image = self._apply_brightness(image, config.get("brightness", 0)) #brilo
        image = self._apply_contrast(image, config.get("contrast", 0)) #contraste
        image = self._apply_zone_filter(image, config.get("zone_mode", "none")) #zonas de luz
        #canales RGB.
        image = self._apply_rgb_channels(
            image,
            config.get("rgb_red", True),
            config.get("rgb_green", True),
            config.get("rgb_blue", True),
        )
        #canales CMY
        image = self._apply_cmy_channels(
            image,
            config.get("cmy_cyan", False),
            config.get("cmy_magenta", False),
            config.get("cmy_yellow", False),
        )
        if config.get("apply_binary", False): #binarización segun umbral
            image = self._apply_binarization(image, config.get("threshold", 128))

        if config.get("apply_negative", False): #negativo
            image = self._apply_negative(image)

        image = self._apply_rotation(image, config.get("rotation", 0)) #rotación

        image = self._apply_fusion( #fusión con la segunda imagen
            image,
            config.get("fusion_alpha", 0.0),
            config.get("fusion_mode", "normal"),
        )

        self.image_array = image #guarda la imagen ya procesada
        return self.image_array

    def show_histogram(self):
        """Genera y muestra el histograma de la imagen actual."""
        if self.image_array is None: #si no hay una imagen procesada, no se puede generar el histograma
            raise ValueError("No hay imagen cargada para generar el histograma.")

        image = self.image_array
        luminance = self._calculate_luminance(image) #calcula la luminancia aproximada para el canal de intensidad

        #crea la ventana de Matplotlib para el histograma.
        plt.figure("Histograma de la imagen", figsize=(10, 6))
        plt.clf() #limpia la figura por si ya existia previamente
        plt.hist(image[:, :, 0].ravel(), bins=256, color="red", alpha=0.4, label="Rojo") #distribución del canal rojo
        plt.hist(image[:, :, 1].ravel(), bins=256, color="green", alpha=0.4, label="Verde") #distribución del canal verde
        plt.hist(image[:, :, 2].ravel(), bins=256, color="blue", alpha=0.4, label="Azul") #distribución del canal azul
        plt.hist(luminance.ravel(), bins=256, color="black", alpha=0.5, label="Luminosidad") #distribución de la luminancia

        #lanza el gráfico
        plt.title("Distribución de colores")
        plt.xlabel("Intensidad")
        plt.ylabel("Frecuencia")
        plt.legend()
        plt.tight_layout()
        plt.show()

    def _apply_brightness(self, image, brightness):
        """Aumenta o disminuye el brillo de la imagen."""
        delta = (float(brightness) / 100.0) * 255.0 #variación de intensidad real
        adjusted = image.astype(np.float32) + delta #suma la variación a cada pixel usando float para evitar desbordes
        return np.clip(adjusted, 0, 255).astype(np.uint8) #recorta el resultado al rango valido y se vuelve a uint8

    def _apply_contrast(self, image, contrast):
        """Modifica el contraste separando o acercando tonos al valor medio."""
        factor = max(0.0, (100.0 + float(contrast)) / 100.0) #factor multiplicativo
        adjusted = (image.astype(np.float32) - 128.0) * factor + 128.0 #contraste modificado
        return np.clip(adjusted, 0, 255).astype(np.uint8) #limita el resultado al rango valido y se vuelve a uint8

    def _apply_zone_filter(self, image, zone_mode):
        """Resalta zonas claras u oscuras usando la luminancia."""
        if zone_mode == "none": #si el modo es none, la imagen se devuelve sin cambios
            return image

        #calcula la luminancia para clasificar las zonas como float
        luminance = self._calculate_luminance(image)
        result = image.astype(np.float32).copy()

        if zone_mode == "light": #si se quieren destacar zonas claras
            mask = luminance >= 170 #se crea una mascara alta
            result[mask] = np.clip(result[mask] * 1.15, 0, 255) #intensifica las zonas claras
            result[~mask] = result[~mask] * 0.35 #atenúa el resto de la imágen
        elif zone_mode == "dark": #si se quieren destacar zonas oscuras
            mask = luminance <= 85 #se crea una mascara baja
            result[mask] = np.clip(result[mask] * 1.35, 0, 255) #intensifica las zonas oscuras
            result[~mask] = result[~mask] * 0.45 #atenúa el resto de la imágen

        return np.clip(result, 0, 255).astype(np.uint8) #limita el resultado al rango valido y se vuelve a uint8

    def _apply_rgb_channels(self, image, red, green, blue):
        """Activa o desactiva directamente los canales RGB."""
        result = image.copy() #trabaja una copia de la imagen original
        if not red: #desactiva el canal rojo
            result[:, :, 0] = 0
        if not green: #desactiva el canal verde
            result[:, :, 1] = 0
        if not blue: #desactiva el canal azul
            result[:, :, 2] = 0
        return result

    def _apply_cmy_channels(self, image, cyan, magenta, yellow):
        """Construye una visualizacion simple basada en combinaciones CMY."""
        if not any([cyan, magenta, yellow]): #si no hay ning canal CMY activo, no se altera la imagen
            return image

        result = np.zeros_like(image) #crea una imagen vacia del mismo tamaño que la original para almacenar el resultado
        if cyan: #si cian esta activo, se conservan verde y azul
            result[:, :, 1] = np.maximum(result[:, :, 1], image[:, :, 1])
            result[:, :, 2] = np.maximum(result[:, :, 2], image[:, :, 2])
        if magenta: #si magenta esta activo, se conservan rojo y azul
            result[:, :, 0] = np.maximum(result[:, :, 0], image[:, :, 0])
            result[:, :, 2] = np.maximum(result[:, :, 2], image[:, :, 2])
        if yellow: #si amarillo esta activo, se conservan rojo y verde
            result[:, :, 0] = np.maximum(result[:, :, 0], image[:, :, 0])
            result[:, :, 1] = np.maximum(result[:, :, 1], image[:, :, 1])
        return result

    def _apply_binarization(self, image, threshold):
        """Convierte la imagen a blanco y negro segun un umbral."""
        threshold = int(np.clip(threshold, 0, 255)) #fuerza el umbral al rango valido entre 0 y 255
        luminance = self._calculate_luminance(image) #calcula la luminancia para trabajar en una sola intensidad
        binary = np.where(luminance >= threshold, 255, 0).astype(np.uint8) #asigna blanco o negro segun si cada pixel supera el umbral
        return np.stack([binary, binary, binary], axis=-1) #replica el resultado en los tres canales para conservar formato RGB

    def _apply_negative(self, image):
        """Invierte los colores de la imagen."""
        return 255 - image #complemento de cada pixel

    def _apply_rotation(self, image, rotation):
        """Rota la imagen usando PIL para simplificar la implementacion."""
        angle = float(rotation) % 360.0 #normaliza el ángulo al rango de 0 a 360 grados
        if angle == 0: #si el ángulo es 0, la imagen se devuelve sin cambios
            return image

        pil_image = Image.fromarray(image) #transforma la imagen NumPy a una imagen PIL
        rotated = pil_image.rotate(-angle, expand=True, fillcolor=(255, 255, 255)) #rota la imagen sin recortarla
        return np.array(rotated, dtype=np.uint8) #retorna la imágen rotada en formato de NumPy

    def _apply_fusion(self, image, fusion_alpha, fusion_mode):
        """Combina la imagen principal con una segunda imagen usando varios modos."""
        if self.second_image_array is None: #si no hay segunda imagen, no se aplica fusión
            return image

        alpha = float(np.clip(fusion_alpha, 0.0, 1.0)) #fuerza el alpha al rango valido entre 0 y 1
        second = self._resize_to_shape(self.second_image_array, image.shape[1], image.shape[0]) #redimensiona la segunda imagen para que coincida con la principal
        base = image.astype(np.float32) #convierte la imagen principal a float para operar con seguridad
        overlay = second.astype(np.float32) #convierte la segunda imagen a float para operar con seguridad

        #modos de fusión:
        if fusion_mode == "multiplicacion": #si el modo es multiplicacion, se multiplican intensidades.
            blended = (base * overlay) / 255.0
        elif fusion_mode == "adicion": #si el modo es adicion, se suman intensidades con recorte.
            blended = np.clip(base + overlay, 0, 255)
        elif fusion_mode == "diferencia": #si el modo es diferencia, se usa la diferencia absoluta.
            blended = np.abs(base - overlay)
        else: #si el modo es otro, se usa la segunda imagen como contenido base de fusion.
            blended = overlay

        result = base * (1.0 - alpha) + blended * alpha #mezcla la imagen base con el resultado del modo seleccionado
        return np.clip(result, 0, 255).astype(np.uint8) #limita el resultado al rango valido y se vuelve a uint8

    def _resize_to_shape(self, image, width, height):
        """Redimensiona una imagen al ancho y alto requeridos."""
        resized = Image.fromarray(image).resize((width, height), Image.LANCZOS) #cambia la imágen de tamaño con Pillow
        return np.array(resized, dtype=np.uint8) #retorna la imágen redimensionada en formato de NumPy

    def _calculate_luminance(self, image):
        """Calcula una luminancia aproximada a partir de RGB."""
        return ( #combina los canales RGB con sus pesos perceptuales
            0.299 * image[:, :, 0] #combina el canal rojo con su peso perceptual
            + 0.587 * image[:, :, 1] #combina el canal verde con mayor peso por sensibilidad visual.
            + 0.114 * image[:, :, 2] #combina el canal azul con el peso restante.
        )

    def _ensure_uint8_rgb(self, array):
        """Convierte cualquier imagen cargada a RGB uint8."""
        #si la imagen viene como float, se asume rango entre 0 y 1.
        if array.dtype == np.float32 or array.dtype == np.float64:
            array = np.clip(array, 0.0, 1.0) #limita el rango float para evitar valores invalidos
            array = (array * 255).astype(np.uint8) #escala al rango clasico de 0 a 255 y se convierte a uint8
        else: #si ya viene en enteros, solo se fuerza el rango permitido.
            array = np.clip(array, 0, 255).astype(np.uint8)

        #si la imagen es de un solo canal, se replica a tres canales RGB.
        if array.ndim == 2:
            array = np.stack([array, array, array], axis=-1) #se usa el mismo canal para rojo, verde y azul

        #si la imagen trae canal alfa, se elimina para trabajar solo con RGB.
        if array.ndim == 3 and array.shape[2] == 4:
            array = array[:, :, :3] #conserva solo los tres primeros canales (RGB), descartando alpha

        return array #retorna la imágen normalizada
