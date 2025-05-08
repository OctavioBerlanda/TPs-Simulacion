import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import chi2
from collections import Counter


# Generador GCL
def generador_gcl(a, c, m, semilla, cantidad):
    numeros = []
    x = semilla
    for _ in range(cantidad):
        x = (a * x + c) % m
        numeros.append(x / m)
    return numeros

# Prueba de Frecuencia (Chi-cuadrado)
def prueba_frecuencia(numeros, k=10, alpha=0.05):
    n = len(numeros)
    intervalos = np.linspace(0, 1, k + 1)
    fo, _ = np.histogram(numeros, bins=intervalos)
    fe = n / k
    chi_cuadrado = np.sum(((fo - fe) ** 2) / fe)
    chi_critico = chi2.ppf(1 - alpha, df=k - 1)

    print("Frecuencias observadas:", fo)
    print("Frecuencia esperada:", fe)
    print("Chi-cuadrado:", round(chi_cuadrado, 4))
    print("Chi-crítico (alpha =", alpha, "):", round(chi_critico, 4))

    if chi_cuadrado < chi_critico:
        print("✅ Pasa la prueba de frecuencia.")
    else:
        print("❌ No pasa la prueba de frecuencia.")

    # Visualización
    plt.bar(range(k), fo, tick_label=[f"{intervalos[i]:.1f}-{intervalos[i+1]:.1f}" for i in range(k)])
    plt.axhline(y=fe, color='red', linestyle='--', label='Esperado')
    plt.title("Prueba de Frecuencia")
    plt.xlabel("Intervalos")
    plt.ylabel("Frecuencia")
    plt.legend()
    plt.show()

#Verifica si los pares consecutivos (𝑥𝑖,𝑥𝑖+1)(x i,x i+1​) están uniformemente distribuidos en el plano [0,1)×[0,1).
def prueba_series(numeros, k=10, alpha=0.05):
    n = len(numeros) - 1
    fe = n / (k ** 2)

    # Pares consecutivos
    pares = [(numeros[i], numeros[i + 1]) for i in range(n)]
    fo = np.zeros((k, k))

    for x, y in pares:
        i = min(int(x * k), k - 1)
        j = min(int(y * k), k - 1)
        fo[i][j] += 1

    chi_cuadrado = np.sum((fo - fe) ** 2 / fe)
    chi_critico = chi2.ppf(1 - alpha, df=k * k - 1)

    print("Chi-cuadrado (Series):", round(chi_cuadrado, 4))
    print("Chi-crítico:", round(chi_critico, 4))

    if chi_cuadrado < chi_critico:
        print("✅ Pasa la prueba de series.")
    else:
        print("❌ No pasa la prueba de series.")

    # Visualización 2D
    plt.imshow(fo, cmap="Blues", interpolation='nearest')
    plt.title("Prueba de Series")
    plt.xlabel("x_i")
    plt.ylabel("x_{i+1}")
    plt.colorbar(label="Frecuencia")
    plt.show()

# Mide si hay demasiadas subidas o bajadas en la secuencia. Se cuentan las "corridas", es decir, secuencias crecientes o decrecientes.
def prueba_corridas(numeros, alpha=0.05):
    n = len(numeros)
    corridas = 1

    for i in range(1, n - 1):
        if (numeros[i] > numeros[i - 1] and numeros[i] > numeros[i + 1]) or \
           (numeros[i] < numeros[i - 1] and numeros[i] < numeros[i + 1]):
            corridas += 1

    media = (2 * n - 1) / 3
    varianza = (16 * n - 29) / 90
    z = (corridas - media) / (varianza ** 0.5)

    print("Corridas observadas:", corridas)
    print("Media esperada:", round(media, 2))
    print("Z calculado:", round(z, 4))

    if abs(z) < 1.96:  # z crítico para alfa = 0.05 (dos colas)
        print("✅ Pasa la prueba de corridas.")
    else:
        print("❌ No pasa la prueba de corridas.")


def clasificar_mano(digitos):
    cuentas = Counter(digitos).values()
    cuentas = sorted(cuentas, reverse=True)
    if cuentas == [5]:
        return "quintilla"
    elif cuentas == [4, 1]:
        return "póker"
    elif cuentas == [3, 2]:
        return "full"
    elif cuentas == [3, 1, 1]:
        return "trío"
    elif cuentas == [2, 2, 1]:
        return "doble par"
    elif cuentas == [2, 1, 1, 1]:
        return "par"
    else:
        return "todos distintos"

def prueba_poker(numeros, alpha=0.05):
    n = len(numeros)
    clases = ["todos distintos", "par", "doble par", "trío", "full", "póker", "quintilla"]
    fo = dict.fromkeys(clases, 0)

    for num in numeros:
        cinco_digitos = str(num)[2:7]  # toma 5 dígitos luego del "0."
        mano = clasificar_mano(cinco_digitos)
        fo[mano] += 1

    total = sum(fo.values())
    fe = {
        "todos distintos": 0.3024 * total,
        "par": 0.5040 * total,
        "doble par": 0.1080 * total,
        "trío": 0.0720 * total,
        "full": 0.0090 * total,
        "póker": 0.0045 * total,
        "quintilla": 0.0001 * total
    }

    chi_cuadrado = sum(((fo[c] - fe[c]) ** 2) / fe[c] for c in clases if fe[c] > 0)
    chi_critico = chi2.ppf(1 - alpha, df=len(clases) - 1)

    print("Chi-cuadrado (Poker):", round(chi_cuadrado, 4))
    print("Chi-crítico:", round(chi_critico, 4))

    if chi_cuadrado < chi_critico:
        print("✅ Pasa la prueba de poker.")
    else:
        print("❌ No pasa la prueba de poker.")


numeros = generador_gcl(a=1664525, c=1013904223, m=2**32, semilla=12345, cantidad=10000)

prueba_frecuencia(numeros, k=10)
prueba_series(numeros, k=10)
prueba_corridas(numeros)
prueba_poker(numeros)

