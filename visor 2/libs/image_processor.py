"""Modulo que concentra la logica de procesamiento de imagenes."""

# Se importa NumPy para trabajar directamente con arreglos de pixeles.
import numpy as np
# Se importa Matplotlib para guardar imagenes y mostrar histogramas.
import matplotlib.pyplot as plt
# Se importa el lector de imagenes de Matplotlib.
from matplotlib import image as mpimg
# Se importa PIL para algunas tareas simples de conversion y rotacion.
from PIL import Image


class ImageProcessor:
    """Clase que agrupa las operaciones de carga, edicion y analisis."""

    def __init__(self):
        """Inicializa las referencias de trabajo del procesador."""
        # Aqui se conserva la imagen original sin modificaciones.
        self.original_image_array = None
        # Aqui se guarda la ultima version procesada de la imagen principal.
        self.image_array = None
        # Aqui se guarda una segunda imagen para fusionarla con la principal.
        self.second_image_array = None

    def load_main_image(self, path):
        """Carga la imagen principal desde disco."""
        # Se lee la imagen usando Matplotlib.
        array = mpimg.imread(path)
        # Se normaliza el arreglo para trabajar siempre en RGB uint8.
        array = self._ensure_uint8_rgb(array)
        # Se almacena una copia como referencia original.
        self.original_image_array = array
        # Se crea una copia inicial como imagen de trabajo.
        self.image_array = array.copy()
        # Se devuelve la imagen lista para mostrarla.
        return self.image_array

    def load_second_image(self, path):
        """Carga una segunda imagen para la fusion."""
        # Se lee la segunda imagen desde el archivo indicado.
        array = mpimg.imread(path)
        # Se asegura el mismo formato interno que la imagen principal.
        array = self._ensure_uint8_rgb(array)
        # Se guarda la segunda imagen para futuras fusiones.
        self.second_image_array = array
        # Se devuelve la imagen ya normalizada.
        return array

    def restore_original_image(self):
        """Restaura la imagen principal a su estado original."""
        # Si aun no existe imagen original, no se puede restaurar.
        if self.original_image_array is None:
            raise ValueError("No hay imagen original para restaurar.")

        # Se reemplaza la imagen de trabajo por una copia de la original.
        self.image_array = self.original_image_array.copy()
        # Se devuelve la imagen restaurada.
        return self.image_array

    def save_image(self, path, use_second=False):
        """Guarda la imagen principal o secundaria en disco."""
        # Si se solicita expresamente, se usa la segunda imagen.
        if use_second:
            array = self.second_image_array
        else:
            # En caso contrario, se guarda la imagen principal procesada.
            array = self.image_array
        # Si no hay imagen disponible, se lanza una excepcion.
        if array is None:
            raise ValueError("No hay imagen para guardar.")
        # Se guarda el arreglo en la ruta indicada.
        plt.imsave(path, array)

    def apply_transformations(self, config):
        """Aplica todas las transformaciones segun la configuracion recibida."""
        # Si no hay imagen original, no existe base para transformar.
        if self.original_image_array is None:
            raise ValueError("Primero debe cargar una imagen principal.")

        # Se parte siempre desde la imagen original para evitar acumulaciones.
        image = self.original_image_array.copy()
        # Se aplica el ajuste de brillo.
        image = self._apply_brightness(image, config.get("brightness", 0))
        # Se aplica el ajuste de contraste.
        image = self._apply_contrast(image, config.get("contrast", 0))
        # Se aplica el filtro opcional de zonas claras u oscuras.
        image = self._apply_zone_filter(image, config.get("zone_mode", "none"))
        # Se activan o desactivan canales RGB.
        image = self._apply_rgb_channels(
            image,
            config.get("rgb_red", True),
            config.get("rgb_green", True),
            config.get("rgb_blue", True),
        )
        # Se aplican los canales CMY si el usuario los activo.
        image = self._apply_cmy_channels(
            image,
            config.get("cmy_cyan", False),
            config.get("cmy_magenta", False),
            config.get("cmy_yellow", False),
        )

        # Si el usuario activo la binarizacion, se aplica el umbral.
        if config.get("apply_binary", False):
            image = self._apply_binarization(image, config.get("threshold", 128))

        # Si el usuario activo el negativo, se invierten los colores.
        if config.get("apply_negative", False):
            image = self._apply_negative(image)

        # Se aplica la rotacion de la imagen.
        image = self._apply_rotation(image, config.get("rotation", 0))

        # Se aplica la fusion con la segunda imagen si existe.
        image = self._apply_fusion(
            image,
            config.get("fusion_alpha", 0.0),
            config.get("fusion_mode", "normal"),
        )
        # Se guarda el resultado como imagen actual del visor.
        self.image_array = image
        # Se devuelve la imagen ya procesada.
        return self.image_array

    def show_histogram(self):
        """Genera y muestra el histograma de la imagen actual."""
        # Si no hay imagen cargada, no se puede generar el histograma.
        if self.image_array is None:
            raise ValueError("No hay imagen cargada para generar el histograma.")

        # Se toma la imagen procesada actual.
        image = self.image_array
        # Se calcula una luminancia aproximada para el canal de intensidad.
        luminance = self._calculate_luminance(image)

        # Se crea la ventana de Matplotlib para el histograma.
        plt.figure("Histograma de la imagen", figsize=(10, 6))
        # Se limpia la figura por si ya existia previamente.
        plt.clf()
        # Se dibuja la distribucion del canal rojo.
        plt.hist(image[:, :, 0].ravel(), bins=256, color="red", alpha=0.4, label="Rojo")
        # Se dibuja la distribucion del canal verde.
        plt.hist(image[:, :, 1].ravel(), bins=256, color="green", alpha=0.4, label="Verde")
        # Se dibuja la distribucion del canal azul.
        plt.hist(image[:, :, 2].ravel(), bins=256, color="blue", alpha=0.4, label="Azul")
        # Se dibuja la distribucion de la luminancia.
        plt.hist(luminance.ravel(), bins=256, color="black", alpha=0.5, label="Luminosidad")
        # Se define el titulo del grafico.
        plt.title("Distribución de colores")
        # Se etiqueta el eje horizontal.
        plt.xlabel("Intensidad")
        # Se etiqueta el eje vertical.
        plt.ylabel("Frecuencia")
        # Se muestra la leyenda de los canales.
        plt.legend()
        # Se ajustan los margenes automaticamente.
        plt.tight_layout()
        # Se presenta la ventana del histograma.
        plt.show()

    def _apply_brightness(self, image, brightness):
        """Aumenta o disminuye el brillo de la imagen."""
        # Se convierte el rango [-100, 100] a una variacion real de intensidad.
        delta = (float(brightness) / 100.0) * 255.0
        # Se suma la variacion a cada pixel usando float para evitar desbordes.
        adjusted = image.astype(np.float32) + delta
        # Se recorta el resultado al rango valido y se vuelve a uint8.
        return np.clip(adjusted, 0, 255).astype(np.uint8)

    def _apply_contrast(self, image, contrast):
        """Modifica el contraste separando o acercando tonos al valor medio."""
        # Se transforma el valor del control a un factor multiplicativo.
        factor = max(0.0, (100.0 + float(contrast)) / 100.0)
        # Se ajusta el contraste alrededor del valor central 128.
        adjusted = (image.astype(np.float32) - 128.0) * factor + 128.0
        # Se limita el resultado al rango valido y se devuelve en uint8.
        return np.clip(adjusted, 0, 255).astype(np.uint8)

    def _apply_zone_filter(self, image, zone_mode):
        """Resalta zonas claras u oscuras usando la luminancia."""
        # Si el modo es none, la imagen se devuelve sin cambios.
        if zone_mode == "none":
            return image

        # Se calcula la luminancia para clasificar las zonas.
        luminance = self._calculate_luminance(image)
        # Se crea una copia en float para modificarla con mayor seguridad.
        result = image.astype(np.float32).copy()

        # Si se quieren destacar zonas claras, se crea una mascara alta.
        if zone_mode == "light":
            mask = luminance >= 170
            # Se intensifican las zonas claras.
            result[mask] = np.clip(result[mask] * 1.15, 0, 255)
            # Se atenúa el resto de la imagen para enfatizar el contraste.
            result[~mask] = result[~mask] * 0.35
        elif zone_mode == "dark":
            # Si se quieren destacar zonas oscuras, se crea una mascara baja.
            mask = luminance <= 85
            # Se intensifican las zonas oscuras conservadas.
            result[mask] = np.clip(result[mask] * 1.35, 0, 255)
            # Se atenúa el resto de la imagen.
            result[~mask] = result[~mask] * 0.45

        # Se recorta el resultado y se regresa en el formato estandar.
        return np.clip(result, 0, 255).astype(np.uint8)

    def _apply_rgb_channels(self, image, red, green, blue):
        """Activa o desactiva directamente los canales RGB."""
        # Se crea una copia para no modificar la imagen original recibida.
        result = image.copy()
        # Si el rojo esta desactivado, su canal se lleva a cero.
        if not red:
            result[:, :, 0] = 0
        # Si el verde esta desactivado, su canal se lleva a cero.
        if not green:
            result[:, :, 1] = 0
        # Si el azul esta desactivado, su canal se lleva a cero.
        if not blue:
            result[:, :, 2] = 0
        # Se devuelve la imagen con los canales seleccionados.
        return result

    def _apply_cmy_channels(self, image, cyan, magenta, yellow):
        """Construye una visualizacion simple basada en combinaciones CMY."""
        # Si no hay ningun canal CMY activo, no se altera la imagen.
        if not any([cyan, magenta, yellow]):
            return image

        # Se crea una imagen vacia donde se iran sumando los canales elegidos.
        result = np.zeros_like(image)
        # Si cian esta activo, se conservan verde y azul.
        if cyan:
            result[:, :, 1] = np.maximum(result[:, :, 1], image[:, :, 1])
            result[:, :, 2] = np.maximum(result[:, :, 2], image[:, :, 2])
        # Si magenta esta activo, se conservan rojo y azul.
        if magenta:
            result[:, :, 0] = np.maximum(result[:, :, 0], image[:, :, 0])
            result[:, :, 2] = np.maximum(result[:, :, 2], image[:, :, 2])
        # Si amarillo esta activo, se conservan rojo y verde.
        if yellow:
            result[:, :, 0] = np.maximum(result[:, :, 0], image[:, :, 0])
            result[:, :, 1] = np.maximum(result[:, :, 1], image[:, :, 1])
        # Se devuelve la combinacion resultante.
        return result

    def _apply_binarization(self, image, threshold):
        """Convierte la imagen a blanco y negro segun un umbral."""
        # Se fuerza el umbral al rango valido entre 0 y 255.
        threshold = int(np.clip(threshold, 0, 255))
        # Se calcula la luminancia para trabajar en una sola intensidad.
        luminance = self._calculate_luminance(image)
        # Se asigna blanco o negro segun si cada pixel supera el umbral.
        binary = np.where(luminance >= threshold, 255, 0).astype(np.uint8)
        # Se replica el resultado en los tres canales para conservar formato RGB.
        return np.stack([binary, binary, binary], axis=-1)

    def _apply_negative(self, image):
        """Invierte los colores de la imagen."""
        # Cada valor se reemplaza por su complemento respecto a 255.
        return 255 - image

    def _apply_rotation(self, image, rotation):
        """Rota la imagen usando PIL para simplificar la implementacion."""
        # Se normaliza el angulo al rango de 0 a 360 grados.
        angle = float(rotation) % 360.0
        # Si el angulo es cero, se devuelve la imagen original.
        if angle == 0:
            return image

        # Se convierte el arreglo a una imagen PIL.
        pil_image = Image.fromarray(image)
        # Se rota la imagen; se usa expand para no recortar y fondo blanco.
        rotated = pil_image.rotate(-angle, expand=True, fillcolor=(255, 255, 255))
        # Se devuelve la imagen rotada otra vez como arreglo NumPy.
        return np.array(rotated, dtype=np.uint8)

    def _apply_fusion(self, image, fusion_alpha, fusion_mode):
        """Combina la imagen principal con una segunda imagen usando varios modos."""
        # Si no existe segunda imagen, no se aplica fusion.
        if self.second_image_array is None:
            return image

        # Se asegura que alpha quede entre 0 y 1.
        alpha = float(np.clip(fusion_alpha, 0.0, 1.0))
        # Se redimensiona la segunda imagen para que coincida con la principal.
        second = self._resize_to_shape(self.second_image_array, image.shape[1], image.shape[0])
        # Se convierte la imagen principal a float para operar con seguridad.
        base = image.astype(np.float32)
        # Se convierte la segunda imagen a float por la misma razon.
        overlay = second.astype(np.float32)

        # Si el modo es multiplicacion, se multiplican intensidades.
        if fusion_mode == "multiplicacion":
            blended = (base * overlay) / 255.0
        elif fusion_mode == "adicion":
            # Si el modo es adicion, se suman intensidades con recorte.
            blended = np.clip(base + overlay, 0, 255)
        elif fusion_mode == "diferencia":
            # Si el modo es diferencia, se usa la diferencia absoluta.
            blended = np.abs(base - overlay)
        else:
            # En modo normal, el contenido base de fusion es la segunda imagen.
            blended = overlay

        # Se mezcla la imagen base con el resultado del modo seleccionado.
        result = base * (1.0 - alpha) + blended * alpha
        # Se limita el resultado y se devuelve en formato uint8.
        return np.clip(result, 0, 255).astype(np.uint8)

    def _resize_to_shape(self, image, width, height):
        """Redimensiona una imagen al ancho y alto requeridos."""
        # Se convierte el arreglo a imagen PIL y se cambia de tamano.
        resized = Image.fromarray(image).resize((width, height), Image.LANCZOS)
        # Se devuelve de nuevo como arreglo NumPy.
        return np.array(resized, dtype=np.uint8)

    def _calculate_luminance(self, image):
        """Calcula una luminancia aproximada a partir de RGB."""
        # Se combina el canal rojo con su peso perceptual.
        return (
            0.299 * image[:, :, 0]
            # Se combina el canal verde con mayor peso por sensibilidad visual.
            + 0.587 * image[:, :, 1]
            # Se combina el canal azul con el peso restante.
            + 0.114 * image[:, :, 2]
        )

    def _ensure_uint8_rgb(self, array):
        """Convierte cualquier imagen cargada a RGB uint8."""
        # Si la imagen viene como float, se asume rango entre 0 y 1.
        if array.dtype == np.float32 or array.dtype == np.float64:
            # Se limita el rango float para evitar valores invalidos.
            array = np.clip(array, 0.0, 1.0)
            # Se escala al rango clasico de 0 a 255 y se convierte a uint8.
            array = (array * 255).astype(np.uint8)
        else:
            # Si ya viene en enteros, solo se fuerza el rango permitido.
            array = np.clip(array, 0, 255).astype(np.uint8)

        # Si la imagen es de un solo canal, se replica a tres canales RGB.
        if array.ndim == 2:
            # Se usa el mismo canal para rojo, verde y azul.
            array = np.stack([array, array, array], axis=-1)

        # Si la imagen trae canal alfa, se elimina para trabajar solo con RGB.
        if array.ndim == 3 and array.shape[2] == 4:
            # Se conservan unicamente los tres primeros canales.
            array = array[:, :, :3]

        # Se devuelve la imagen final normalizada.
        return array
