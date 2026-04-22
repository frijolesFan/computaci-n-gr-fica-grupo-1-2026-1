import tkinter as tk
from libs.ui import ImageViewerGUI


def main():
    """Crea la ventana principal y arranca la aplicacion."""
    root = tk.Tk()
    app = ImageViewerGUI(root)
    _ = app
    root.mainloop()

if __name__ == "__main__":
    main()

