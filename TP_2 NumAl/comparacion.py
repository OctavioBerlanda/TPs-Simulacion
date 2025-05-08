import random
from generadorGCL import (
    generador_gcl,
    prueba_frecuencia,
    prueba_series,
    prueba_corridas,
    prueba_poker
)

# Configuración general
CANTIDAD_NUMEROS = 10000
SEMILLA = 12345

# === Generación de números ===

# 1. Números con GCL
numeros_gcl = generador_gcl(a=1664525, c=1013904223, m=2**32, semilla=SEMILLA, cantidad=CANTIDAD_NUMEROS)

# 2. Números con random de Python
random.seed(SEMILLA)  # Fijamos la semilla para comparar en igualdad de condiciones
numeros_py = [random.random() for _ in range(CANTIDAD_NUMEROS)]

# === Comparación mediante pruebas ===

def ejecutar_pruebas(nombre, numeros):
    print("\n" + "="*40)
    print(f"🧪 Resultados para {nombre}")
    print("="*40)
    prueba_frecuencia(numeros, k=10)
    prueba_series(numeros, k=10)
    prueba_corridas(numeros)
    prueba_poker(numeros)

# Ejecutamos para GCL
ejecutar_pruebas("GCL", numeros_gcl)

# Ejecutamos para Random de Python
ejecutar_pruebas("Random de Python", numeros_py)
