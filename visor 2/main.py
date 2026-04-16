"""Punto de entrada principal del visor de imagenes."""

# Se importa Tkinter porque la aplicacion usa una interfaz grafica.
import tkinter as tk
# Se importa la clase que construye toda la interfaz del visor.
from libs.ui import ImageViewerGUI


def main():
    """Crea la ventana principal y arranca la aplicacion."""
    # Se crea la ventana raiz de Tkinter.
    root = tk.Tk()
    # Se construye la interfaz completa del visor sobre la ventana raiz.
    app = ImageViewerGUI(root)
    # Se conserva la referencia por claridad durante la lectura del codigo.
    _ = app
    # Se inicia el ciclo de eventos de Tkinter para mantener la ventana activa.
    root.mainloop()


# Este bloque garantiza que la aplicacion solo se ejecute si este archivo
# se lanza directamente y no cuando es importado desde otro modulo.
if __name__ == "__main__":
    # Se llama a la funcion principal de arranque.
    main()

