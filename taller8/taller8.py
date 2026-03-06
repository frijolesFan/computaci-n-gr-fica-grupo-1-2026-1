import numpy as np
import matplotlib.pyplot as plt
import ImgProcess as imp

def punto1():
    lienzo = np.zeros((3, 3, 3), dtype=np.uint8)
    lienzo[0, 0, :] = [0, 255, 255]  #cian
    lienzo[0, 1, :] = [255, 255, 255]  #blanco
    lienzo[0, 2, :] = [255, 0, 0]  #rojo
    
    lienzo[1, 0, :] = [255, 0, 255]  #magenta
    lienzo[1, 1, :] = [255/2, 255/2, 255/2]  #gris
    lienzo[1, 2, :] = [0, 255, 0]  #verde

    lienzo[2, 0, :] = [255, 255, 0]  #amarillo
    lienzo[2, 1, :] = [0, 0, 0]  #negro
    lienzo[2, 2, :] = [0, 0, 255]  #azul

    plt.imshow(lienzo)
    plt.show()

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
    punto1()