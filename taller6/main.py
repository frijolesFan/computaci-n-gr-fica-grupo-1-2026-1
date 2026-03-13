import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

A = np.arange(1, 16)

def creacion_y_manipulacion_de_arrays():
    print(f"Vector A: {A}")
    A1 = A.reshape(5, 3)
    print(f"Vector redimensionado (matriz): {A1}")

def operaciones_basicas():
    print(f"suma de A: {np.sum(A)}")   
    print(f"media de A: {np.mean(A)}")
    print(f"producto de A: {np.prod(A)}")

def acceso_y_slicing():
    print(f"segundo y tercer elemento de la segunda fila de A: {A[1][[1, 2]]}")

B = A[A>=5]
def indexacion_booleana():
    print(f"Vector B {B}")

C = np.arange(5, 14).reshape(3, 3)
def algebra_lineal():
    print(f"Matriz C: {C}")
    print(f"determinante de C: {np.linalg.det(C)}")
    print(f"inversa de C: {np.linalg.inv(C)}")

D = np.random.randint(1, 101, 100)
def estadisticas():
    print(f"Vector D: {D}")
    print(f"valor maximo de D: {np.max(D)}")
    print(f"valor minimo de D: {np.min(D)}")
    print(f"desviacion estandar de D: {np.std(D):.2f}")

def grafico_basico():
    x = np.linspace(-2*np.pi, 2*np.pi, 100)
    seno = np.sin(x)
    coseno = np.cos(x)
    plt.plot(x, seno, label="sin(x)")
    plt.plot(x, coseno, label="cos(x)")
    plt.xlabel("x")
    plt.ylabel("valor")
    plt.show()

def grafico_de_dispersion():
    indices = np.arange(1, len(D) + 1)
    plt.scatter(indices, D)
    plt.xlabel("Índice")
    plt.ylabel("Valor de D")
    plt.show()

def histograma():
    plt.hist(D, bins=20)
    plt.title("Histograma del vector D")
    plt.xlabel("Valores")
    plt.ylabel("Frecuencia")
    plt.show()

def manipulacion_de_imagenes():
    img = mpimg.imread("resources/dawg.jpg")
    gris = np.mean(img, axis=2)
    plt.imshow(gris, cmap="gray")
    plt.show()

manipulacion_de_imagenes()