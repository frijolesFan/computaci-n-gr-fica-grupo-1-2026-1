import numpy as np

A = [2, 3, 5, 1, 4, 7, 9, 8, 6, 10] #1
print(f"Vector A: {A}")
B = np.arange(11, 21) #2
print(f"Vector B: {B}")
C = np.concatenate((A, B)) #3
print(f"Vector C: {C}")

print(f"valor minimo en C: {np.min(C)}") #4
print(f"valor maximo en C: {np.max(C)}") #5
print(f"longitud del vector C: {np.size(C)}") #6

media = 0
for i in C:
    media += i
media /= np.size(C)
print(f"promedio de los elementos en C (operaciones elementales): {media}") #7
print(f"promedio de los elementos en C (funcion numpy): {np.mean(C)}") #8
print(f"media en el vector C (usando numpy): {np.mean(C)}") #9
print(f"suma del vector C (usando numpy): {np.sum(C)}") #10
D = C[C>=5]
print(f"Vector D: {D}") #11
E = C[(C>=5) & (C<=15)]
print(f"vector E: {E}") #12
C[[4,14]] = 7
print(f"vector C (elementos 5 y 15 cambiados por 7): {C}") #13
valores, conteo = np.unique(C, return_counts=True)
print(f"moda del vector C: {valores[conteo.argmax()]}") #14
C = np.sort(C)
print(f"vector C ordenado: {C}") #15
print(f"vector C * 10: {C*10}") #16
C[5:8] = [60, 70, 80]
print(f"elementos de C del 6 al 80 cambiados: {C}")#17
C[13:16] = [140, 150, 160]
print(f"vector C con los elementos del 14 al 16 cambiados: {C}") #18