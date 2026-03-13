import numpy as np

def creacion_y_propiedades():
    array = np.arange(1, 11)
    print(f"array original:\n{array}\nPropiedades:\n-forma: {array.shape}\n-dimension: {array.size}\n")
    resized_array = array.reshape(5, 2)
    print(f"array reestructurado:\n{resized_array}\nPropiedades:\n-forma: {resized_array.shape}\n-dimension: {resized_array.size}")

def operaciones_basicas(limite_inferior, limite_superior):
    array_a = np.random.randint(limite_inferior, limite_superior + 1, 5)
    array_b = np.random.randint(limite_inferior, limite_superior + 1, 5)
    print(f"array A: {array_a}")
    print(f"array B: {array_b}")
    print(f"suma elemento a elemento (A + B): {np.add(array_a, array_b)}") #suma el elemento a[n] con el elemnto b[n] 
    print(f"resta elemento a elemento (A - B): {np.subtract(array_a, array_b)}") #resta el elemento a[n] con el elemnto b[n] 
    print(f"resta elemento a elemento (B - A): {np.subtract(array_b, array_a)}") #resta el elemento b[n] con el elemnto a[n] 
    print(f"producto elemento a elemento (A x B): {np.multiply(array_b, array_a)}") #multiplica el elemento a[n] con el elemnto b[n] 
    print(f"suma total de los elementos de A: {array_a.sum()}") #suma del elemento a[0] hasta el elemento a[n] del array A

def indexacion_y_slicing():
    array = np.arange(0, 20)
    #print(f"array: {array}")
    print(f"5 elemento del array: {array[4]}") #selecciona el quinto elemento del array (indice 0)
    print(f"elementos de la posicion 2 a la 6: {array[2:7]}") #selecciona los elementos del 2 hasta el 6 (7, ya que no llega al limite superior)
    print(f"ultimos 3 elementos: {array[-3:]}") #los indices negativos cuentan desde el final, -3 muestra los 3 elementos desde el final
    print(f"array normal: {array}")
    array[0] = 100
    print(f"array actualizado: {array}")
    
def broadcasting_y_ufunc():
    matrix = np.arange(1, 10).reshape(3, 3)
    print(f"matriz original:\n{matrix}\n")
    matrix = matrix + 10
    print(f"se suma un escalar (10) a cada elemento de la matriz con broadcasting:\n{matrix}")
    print("el broadcasting permite sumar arrays de diferentes dimensiones, por ejemplo\nnos permitio sumar un numero (escalar) con un array 3x3 (matriz)")
    print(f"\nse calcula la raiz cuadrada de cada elemento de la matriz:\n{np.sqrt(matrix)}")
    
def manejo_de_datos_faltantes():
    array = np.array([1, 2, np.nan, 4, 5])
    array2 = np.nan_to_num(array)
    print(f"media del array original: {array.mean()}")
    print(f"media del array con valores faltantes reemplazados: {array2.mean()}")

def guardar_y_cargar_array():
    datos = np.array([10, 20, 35, 40, 50])
    np.save('datos.npy', datos)
    datos_cargados = np.load('datos.npy')
    verificacion = np.array_equal(datos, datos_cargados)
    print(f"datos originales: {datos}")
    print(f"datos cargados: {datos_cargados}")
    print(f"verificacion de igualdad: {verificacion}")

def main_menu():
    while True:
        print("\nMenu Principal\n")
        print("1. Creacion y Propiedades de Arrays")
        print("2. Operaciones Basicas con Arrays")
        print("3. Indexacion y Slicing")
        print("4. Broadcasting y Ufuncs")
        print("5. Manejo de Datos Faltantes")
        print("6. Guardar y Cargar Arrays")
        print("7. Salir")
        opcion = input("Ingrese su eleccion: ")
        if opcion == "1":
            creacion_y_propiedades()
        elif opcion == "2":
            inf = input("Limite inferior: ")
            up = input("Limite superior: ")
            operaciones_basicas(inf, up)
        elif opcion == "3":
            indexacion_y_slicing()
        elif opcion == "4":
            broadcasting_y_ufunc()
        elif opcion == "5":
            manejo_de_datos_faltantes()
        elif opcion == "6":
            guardar_y_cargar_array()
        elif opcion == "7":
            print("Saliendo")
            break
        else:
            print("Opcion invalida")


guardar_y_cargar_array()