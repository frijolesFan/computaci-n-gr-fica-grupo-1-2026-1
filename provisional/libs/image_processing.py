import numpy as np
from PIL import Image


"""
Módulo de procesamiento de imágenes.

Incluye todas las transformaciones numéricas aplicadas a la imagen:
brillo, contraste, cambio de tipo (gris/negativo), filtrado por zonas,
activación de canales RGB/CMY y fusión con otra imagen mediante
distintos modos de superposición.
"""


def process_image(
    source_image: Image.Image,
    brightness: float,
    contrast: float,
    zone_mode: str,
    type_mode: str,
    channel_r: bool,
    channel_g: bool,
    channel_b: bool,
    channel_cyan: bool,
    channel_magenta: bool,
    channel_yellow: bool,
    blend_image: Image.Image | None,
    blend_alpha: float,
    blend_mode: str,
) -> Image.Image:
    """
    Aplica todas las transformaciones seleccionadas sobre la imagen origen.

    Parámetros:
        source_image: imagen de entrada en formato PIL.Image.
        brightness: desplazamiento de brillo en el rango aproximado [-100, 100].
        contrast: factor de contraste en porcentaje (0 no cambia, valores positivos aumentan).
        zone_mode: modo de selección de zonas ("claras", "oscuras" o "ninguna").
        type_mode: modo global de la imagen ("Original", "Gris" o "Negativo").
        channel_r, channel_g, channel_b: activación de canales RGB.
        channel_cyan, channel_magenta, channel_yellow: activación de canales CMY.
        blend_image: imagen secundaria para fusión, o None si no se usa.
        blend_alpha: porcentaje de mezcla entre 0 y 100.
        blend_mode: modo de fusión ("Normal", "Suma", "Multiplicar", "Promedio", "Diferencia").

    Devuelve:
        Una nueva instancia PIL.Image con todos los efectos aplicados.
    """
    image_rgb = source_image.convert("RGB")
    data = np.asarray(image_rgb).astype(np.float32)

    data += float(brightness)
    factor = 1.0 + float(contrast) / 100.0
    data = (data - 127.5) * factor + 127.5
    data = np.clip(data, 0.0, 255.0)

    mode = type_mode
    if mode == "Gris":
        gray = 0.299 * data[..., 0] + 0.587 * data[..., 1] + 0.114 * data[..., 2]
        gray = np.clip(gray, 0.0, 255.0)
        data = np.stack((gray, gray, gray), axis=2)
    elif mode == "Negativo":
        data = 255.0 - data

    cyan_sel = bool(channel_cyan)
    magenta_sel = bool(channel_magenta)
    yellow_sel = bool(channel_yellow)

    if cyan_sel or magenta_sel or yellow_sel:
        base_uint = np.clip(data, 0.0, 255.0).astype(np.uint8)
        r = base_uint[..., 0].astype(np.float32)
        g = base_uint[..., 1].astype(np.float32)
        b = base_uint[..., 2].astype(np.float32)
        components: list[np.ndarray] = []
        if cyan_sel:
            components.append(255.0 - r)
        if magenta_sel:
            components.append(255.0 - g)
        if yellow_sel:
            components.append(255.0 - b)
        combined = np.mean(components, axis=0)
        combined = np.clip(combined, 0.0, 255.0).astype(np.uint8)
        base_uint = np.stack((combined, combined, combined), axis=2)
        data = base_uint.astype(np.float32)
    else:
        r_enabled = bool(channel_r)
        g_enabled = bool(channel_g)
        b_enabled = bool(channel_b)
        if not (r_enabled or g_enabled or b_enabled):
            r_enabled = True
            g_enabled = True
            b_enabled = True
        if not r_enabled:
            data[..., 0] = 0.0
        if not g_enabled:
            data[..., 1] = 0.0
        if not b_enabled:
            data[..., 2] = 0.0

    base_uint = np.clip(data, 0.0, 255.0).astype(np.uint8)

    zone = zone_mode
    if zone in ("claras", "oscuras"):
        gray = 0.299 * base_uint[..., 0] + 0.587 * base_uint[..., 1] + 0.114 * base_uint[..., 2]
        if zone == "claras":
            mask = gray >= 180.0
        else:
            mask = gray <= 75.0
        mask3 = np.stack((mask, mask, mask), axis=2)
        base_uint = np.where(mask3, base_uint, 0)

    if blend_image is not None:
        alpha_value = float(blend_alpha)
        if alpha_value > 0.0:
            alpha_value = max(0.0, min(100.0, alpha_value)) / 100.0
            height, width, _ = base_uint.shape
            blend_resized = blend_image.resize((width, height), Image.LANCZOS)
            blend_array = np.asarray(blend_resized.convert("RGB")).astype(np.float32)
            base_float = base_uint.astype(np.float32)

            mode_blend = blend_mode
            if mode_blend == "Suma":
                combined = base_float + alpha_value * blend_array
            elif mode_blend == "Multiplicar":
                combined = base_float * (1.0 - alpha_value + alpha_value * (blend_array / 255.0))
            elif mode_blend == "Promedio":
                combined = (1.0 - alpha_value) * base_float + alpha_value * ((base_float + blend_array) / 2.0)
            elif mode_blend == "Diferencia":
                combined = (1.0 - alpha_value) * base_float + alpha_value * np.abs(base_float - blend_array)
            else:
                combined = (1.0 - alpha_value) * base_float + alpha_value * blend_array

            base_uint = np.clip(combined, 0.0, 255.0).astype(np.uint8)

    return Image.fromarray(base_uint, mode="RGB")

