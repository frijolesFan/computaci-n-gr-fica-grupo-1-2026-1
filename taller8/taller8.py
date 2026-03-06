import numpy as np
import matplotlib.pyplot as plt
import ImgProcess as imp

def punto1():
    pass

def punto3():
    imagen = plt.imread('resources/dawg.jpg')
    imagenNega = imp.negative(imagen)
    plt.imshow(imagenNega)
    plt.show()

def punto4():
    imagen = plt.imread('resources/dawg.jpg')
    imagenRed = imp.red_channel(imagen)
    plt.imshow(imagenRed)
    plt.show()

def punto5():
    imagen = plt.imread('resources/dawg.jpg')
    imagenGreen = imp.green_channel(imagen)
    plt.imshow(imagenGreen)
    plt.show()

def punto6():
    imagen = plt.imread('resources/dawg.jpg')
    imagenBlue = imp.blue_channel(imagen)
    plt.imshow(imagenBlue)
    plt.show()

def punto7():
    imagen = plt.imread('resources/dawg.jpg')
    imagenMagenta = imp.magenta(imagen)
    plt.imshow(imagenMagenta)
    plt.show()

if __name__ == "__main__":
    punto7()