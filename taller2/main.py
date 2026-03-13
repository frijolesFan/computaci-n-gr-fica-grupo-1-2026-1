import numpy as np
import string
import matplotlib.pyplot as plt

def calculadora(operacion):
    a, operador, b = operacion.split()
    a, b = float(a), float(b)
    if operador == '+':
        return a + b
    elif operador == '-':
        return a - b
    elif operador == '*':
        return a * b
    elif operador == '/':
        return a / b
    else:
        return 'operador invalido'

def filtrar_numeros_pares_bucle(numeros):
    pares = []
    for n in numeros:
        if n % 2 == 0:
            pares.append(n)
    return pares

def celcius_a_fahrenheit(celcius):
    return list(map(lambda c: c * 9/5 + 32, celcius))

def sistema_de_calificaciones(calificacion):
    calificaciones = {
        5: 'A',
        4: 'B',
        3: 'C',
        2: 'D',
        1: 'F',
        0: 'F'
    }
    return calificaciones.get(int(calificacion), 'calificacion invalida')

def conteo_de_palabras(texto):
    for signo in string.punctuation:
        texto = texto.replace(signo, "")
    palabras = texto.split()
    conteo = {}
    for p in palabras:
        if p in conteo:
            conteo[p] += 1
        else:
            conteo[p] = 1
    return conteo

def encontrar_elemento(lista, elemento):
    for i in range(len(lista)):
        if lista[i] == elemento:
            return i
    return -1

def evaluador_de_parentesis(cadena):
    contador = 0
    
    for c in cadena:
        if c == '(':
            contador += 1
        elif c == ')':
            contador -= 1
    
    if contador == 0:
        return True
    return False

def ordenar_personas(lista):
    return sorted(lista, key=lambda persona: (persona[1], persona[0]))

def creador_de_contreaseñas(longitud):
    return ''.join(np.random.choice(list(string.printable), longitud))

contactos = {
    "ana": "1234567890",
    "juan": "0987654321",
    "pedro": "5555555555"
}

def agenda_telefonica():
    while True:
        print("\n----------- Agenda de Contactos -----------\n")
        print("1. Buscar contacto")
        print("2. Agregar contacto")
        print("3. Eliminar contacto")
        print("4. Mostrar todos los contactos")
        print("5. Salir")
        opcion = int(input("Ingrese una opcion:// "))
        print("\n")
        if opcion == 1:
            nombre = input("Ingrese el nombre del contacto:// ")
            if nombre in contactos:
                print(f"El numero de {nombre} es {contactos[nombre]}")
            else:
                print("Contacto no encontrado")

        elif opcion == 2:
            nombre = input("Ingrese el nombre del contacto:// ")
            if nombre in contactos:
                print("El contacto ya existe")
            else:
                numero = input("Ingrese el numero del contacto:// ")
                contactos[nombre] = numero
                if numero.isdigit():
                    if numero not in contactos.values():
                        contactos[nombre] = numero
                        print("Contacto agregado")
                    else:
                        print("Numero ya existe")
                else:
                    print("Numero invalido")

        elif opcion == 3:
            nombre = input("Ingrese el nombre del contacto:// ")
            if nombre in contactos:
                del contactos[nombre]
                print("Contacto eliminado")
            else:
                print("Contacto no encontrado")
        
        elif opcion == 4:
            print("Contactos:")
            for nombre, numero in contactos.items():
                print(f"{nombre}: {numero}")

        elif opcion == 5:
            break

def main_menu():
    while True:
        print("\n----------- Menu Principal -----------\n")
        print("1. operaciones Basicas (Calculadora)")
        print("2. Filtrado de Lista por Numeros Pares")
        print("3. Conversion de Temperaturas de Celsius a Fahrenheit")
        print("4. Sistema de Calificaciones a Letras")
        print("5. Conteo de Palabras en una Cadena")
        print("6. Busqueda de Elemento en Lista")
        print("7. Validacion de Secuencia de Parentesis")
        print("8. ordenamiento Personalizado de Lista de Tuplas")
        print("9. Generador de Contraseñas Aleatorias")
        print("10. Gestion de Agenda Telefonica")
        print("11. Salir del Programa")
        opcion = int(input("Ingrese una opcion:// "))
        print("\n")
        if opcion == 1:
            operacion = input("Ingrese la operacion (a operador b):// ")
            resultado = calculadora(operacion)
            print(f"Resultado: {resultado}")
        elif opcion == 2:
            numeros_str = input("Ingrese una lista de numeros separados por comas: ")
            numeros = [int(n) for n in numeros_str.split(',')]
            pares = filtrar_numeros_pares_bucle(numeros)
            print(f"Numeros pares: {pares}")
        elif opcion == 3:
            temps_str = input("Ingrese temperaturas en Celsius separadas por comas: ")
            temps_c = [float(t) for t in temps_str.split(',')]
            temps_f = celcius_a_fahrenheit(temps_c)
            print(f"Temperaturas en Fahrenheit: {temps_f}")
        elif opcion == 4:
            cal = input("Ingrese la calificacion numerica: ")
            letra = sistema_de_calificaciones(cal)
            print(f"Calificacion en letra: {letra}")
        elif opcion == 5:
            texto = input("Ingrese el texto: ")
            conteo = conteo_de_palabras(texto)
            print(f"Conteo de palabras: {conteo}")
        elif opcion == 6:
            lista_str = input("Ingrese una lista de elementos separados por coma: ")
            lista = lista_str.split(',')
            elemento = input("Ingrese el elemento a buscar: ")
            indice = encontrar_elemento(lista, elemento)
            if indice != -1:
                print(f"El elemento se encuentra en el indice: {indice}")
            else:
                print("El elemento no se encontro en la lista.")
        elif opcion == 7:
            cadena = input("Ingrese la secuencia de parentesis: ")
            if evaluador_de_parentesis(cadena):
                print("La secuencia de parentesis es valida.")
            else:
                print("La secuencia de parentesis no es valida.")
        elif opcion == 8:
            personas = [('Juan', 25), ('Ana', 22), ('Pedro', 25)] #utiliza una lista predefinida por simplificar
            print(f"Lista original: {personas}")
            ordenada = ordenar_personas(personas)
            print(f"Lista ordenada por edad y luego por nombre: {ordenada}")
        elif opcion == 9:
            longitud = int(input("Ingrese la longitud de la contraseña: "))
            contrasena = creador_de_contreaseñas(longitud)
            print(f"Contraseña generada: {contrasena}")
        elif opcion == 10:
            agenda_telefonica()
        elif opcion == 11:
            print("Saliendo del programa")
            break
        else:
            print("opcion no valida")

if __name__ == "__main__":
    main_menu()
