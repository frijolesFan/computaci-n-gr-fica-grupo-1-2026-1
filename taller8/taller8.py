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

if __name__ == "__main__":
    punto3()