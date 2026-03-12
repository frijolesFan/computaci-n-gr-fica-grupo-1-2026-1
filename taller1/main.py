import numpy as np
import matplotlib.pyplot as plt

def caida_libre(h, g=9.8): #calcula la caida libre de un objeto dados su altura y la gravedad
    return np.sqrt((2*h) / g)

def conversion_de_unidades(value, unit): #convierte km/h a m/s y viceversa
    return value / 360 if unit == "km/h" else 360 /value

def movimiento_rectilineo_acelerado(v0, a, t): #calcula el MRUA dados v0, a y t
    return (v0 * t) + ((a * t**2) / 2)

def suma_de_vectores(v1, v2): #suma de vectores
    return np.add(v1, v2)

def producto_escalar(v1, v2): #devuelve el angulo entre dos vectorse
    return np.dot(v1, v2)/np.linalg.norm(v1)*np.linalg.norm(v2)

def lanzamiento_de_proyectil(v0, angle):
    vy = v0 * np.sin(np.radians(angle))
    max_height = (vy**2) / (2 * 9.8)
    max_length = (v0**2 * np.sin(np.radians(2 * angle))) / 9.8
    print(f"Altura maxima: {max_height:.2f} metros")
    print(f"Longitud maxima: {max_length:.2f} metros")

def menu():
    print("1. Calcular caida libre")
    print("2. Convertir unidades")
    print("3. Calcular MRUA")
    print("4. Sumar vectores")
    print("5. Calcular angulo entre vectores")
    print("6. Lanzar proyectil")
    print("0. Salir")
    opcion = int(input("Ingrese una opcion: "))
    if opcion == 1:
        h = float(input("Ingrese la altura: "))
        print(f"La caida libre es: {caida_libre(h):.2f} metros")
    elif opcion == 2:
        value = float(input("Ingrese el valor: "))
        unit = input("Ingrese la unidad (km/h o m/s): ")
        print(f"La conversion es: {conversion_de_unidades(value, unit):.2f}")
    elif opcion == 3:
        v0 = float(input("Ingrese la velocidad inicial: "))
        a = float(input("Ingrese la aceleracion: "))
        t = float(input("Ingrese el tiempo: "))
        print(f"La velocidad es: {movimiento_rectilineo_acelerado(v0, a, t):.2f} metros/segundo")
    elif opcion == 4:
        v1 = np.array(input("Ingrese el primer vector (separado por espacios): ").split(), dtype=float)
        v2 = np.array(input("Ingrese el segundo vector (separado por espacios): ").split(), dtype=float)
        print(f"La suma de los vectores es: {suma_de_vectores(v1, v2)}")
    elif opcion == 5:
        v1 = np.array(input("Ingrese el primer vector (separado por espacios): ").split(), dtype=float)
        v2 = np.array(input("Ingrese el segundo vector (separado por espacios): ").split(), dtype=float)
        print(f"El angulo entre los vectores es: {producto_escalar(v1, v2):.2f} grados")
    elif opcion == 6:
        v0 = float(input("Ingrese la velocidad inicial: "))
        angle = float(input("Ingrese el angulo: "))
        lanzamiento_de_proyectil(v0, angle)
    elif opcion == 0:
        print("adios")
    else:
        print("Opcion invalida")

lanzamiento_de_proyectil(12, 60)