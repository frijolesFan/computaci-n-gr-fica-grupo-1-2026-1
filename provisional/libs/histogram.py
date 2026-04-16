import matplotlib.pyplot as plt
import numpy as np
from PIL import Image


"""
Módulo de visualización de histogramas.

Dibuja el histograma de la imagen resultante, incluyendo intensidad global
y canales RGB. Opcionalmente añade también los canales CMY en función de
las opciones seleccionadas en la interfaz.
"""


def show_histogram(
    image: Image.Image,
    channel_cyan: bool,
    channel_magenta: bool,
    channel_yellow: bool,
) -> None:
    """
    Muestra el histograma de la imagen en una ventana de Matplotlib.

    Parámetros:
        image: imagen PIL ya procesada.
        channel_cyan, channel_magenta, channel_yellow:
            indican si se deben incluir también los histogramas de los
            canales C, M y Y derivados de la imagen RGB.
    """
    array = np.asarray(image.convert("RGB"))
    r = array[..., 0].flatten()
    g = array[..., 1].flatten()
    b = array[..., 2].flatten()
    gray = 0.299 * r + 0.587 * g + 0.114 * b

    plt.figure("Histograma")
    plt.clf()
    plt.hist(gray, bins=256, range=(0, 255), color="black", alpha=0.3, label="Intensidad")
    plt.hist(r, bins=256, range=(0, 255), color="red", alpha=0.3, label="R")
    plt.hist(g, bins=256, range=(0, 255), color="green", alpha=0.3, label="G")
    plt.hist(b, bins=256, range=(0, 255), color="blue", alpha=0.3, label="B")

    if channel_cyan or channel_magenta or channel_yellow:
        c = 255.0 - r
        m = 255.0 - g
        y = 255.0 - b
        if channel_cyan:
            plt.hist(c, bins=256, range=(0, 255), color="c", alpha=0.3, label="C")
        if channel_magenta:
            plt.hist(m, bins=256, range=(0, 255), color="m", alpha=0.3, label="M")
        if channel_yellow:
            plt.hist(y, bins=256, range=(0, 255), color="y", alpha=0.3, label="Y")

    plt.xlabel("Intensidad")
    plt.ylabel("Frecuencia")
    plt.legend()
    plt.tight_layout()
    plt.show(block=False)
