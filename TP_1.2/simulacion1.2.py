import random
import argparse
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import PercentFormatter

def simular_ruleta(n_tiradas, n_corridas, numero_elegido=None, estrategia='m', capital_tipo='i', capital_inicial=1000):
    """
    Simula múltiples corridas de una ruleta y calcula estadísticas, incluyendo estrategias de apuesta
    """
    # Configuración de la ruleta (europea: 0-36)
    numeros_ruleta = list(range(37))
    prob_teorica = 1/37 if numero_elegido is not None else None

    # Almacenar resultados de todas las corridas
    resultados = {
        'frecuencias': [],
        'capital': [],
        'victorias_acumuladas': [],
        'win_loss_ratio': [],
        'bancarrotas': 0
    }

    for _ in range(n_corridas):
        # Inicializar capital
        capital = capital_inicial if capital_tipo == 'f' else float('inf')
        capital_acum = []
        en_bancarrota = False

        # Simular tiradas
        tiradas = [random.choice(numeros_ruleta) for _ in range(n_tiradas)]
        print(f"Tiradas: {tiradas}")  # Debug: Mostrar tiradas generadas

        # Estadísticas acumulativas
        fr_acum = []  # Frecuencia relativa acumulada del número elegido
        victorias_acum = []  # Victorias acumuladas
        win_loss_acum = []  # Relación victorias/derrotas
        conteo_victorias = 0
        conteo_derrotas = 0
        conteo = 0

        # Variables para estrategias
        apuesta_base = 10
        apuesta_actual = apuesta_base
        victorias_consecutivas = 0
        fibonacci = [1, 1, 2, 3, 5, 8, 13, 21, 34]
        fib_index = 0

        for i in range(1, n_tiradas + 1):
            if capital_tipo == 'f' and capital <= 0:
                en_bancarrota = True
                break

            if capital_tipo == 'f' and apuesta_actual > capital:
                apuesta_actual = capital  # No apostar más del capital disponible

            gano = numero_elegido is not None and tiradas[i - 1] == numero_elegido

            # Actualizar capital según resultado
            if gano:
                capital += apuesta_actual * 35
                conteo_victorias += 1
                victorias_consecutivas += 1
            else:
                capital -= apuesta_actual
                conteo_derrotas += 1
                victorias_consecutivas = 0

            # Actualizar apuesta según estrategia
            if estrategia == 'm':  # Martingala
                apuesta_actual = apuesta_base if gano else apuesta_actual * 2
            elif estrategia == 'd':  # D'Alembert
                apuesta_actual = max(apuesta_base, apuesta_actual + (10 if not gano else -10))
            elif estrategia == 'f':  # Fibonacci
                if gano:
                    fib_index = max(0, fib_index - 2)  # Retrocede 2 posiciones si gana
                else:
                    fib_index = min(len(fibonacci) - 1, fib_index + 1)  # Avanza 1 posición si pierde
                apuesta_actual = apuesta_base * fibonacci[fib_index]
            elif estrategia == 'o':  # Paroli
                if gano and victorias_consecutivas < 3:
                    apuesta_actual *= 2  # Duplica la apuesta si gana y no ha alcanzado 3 victorias consecutivas
                else:
                    apuesta_actual = apuesta_base  # Reinicia la apuesta

            capital_acum.append(capital)

            # Estadísticas (solo si se especificó un número elegido)
            if numero_elegido is not None:
                if tiradas[i - 1] == numero_elegido:
                    conteo += 1
                fr = conteo / i
                fr_acum.append(fr)
                victorias_acum.append(conteo)
                # Relación victorias/derrotas
                ratio = conteo_victorias / conteo_derrotas if conteo_derrotas > 0 else np.nan
                win_loss_acum.append(ratio)
            else:
                fr_acum.append(np.nan)
                victorias_acum.append(0)
                win_loss_acum.append(np.nan)

        # Rellenar las listas hasta n_tiradas si la simulación terminó antes
        while len(capital_acum) < n_tiradas:
            capital_acum.append(capital_acum[-1] if capital_acum else np.nan)
            if numero_elegido is not None:
                fr_acum.append(fr_acum[-1] if fr_acum else np.nan)
                victorias_acum.append(victorias_acum[-1] if victorias_acum else 0)
                win_loss_acum.append(win_loss_acum[-1] if win_loss_acum else np.nan)
            else:
                fr_acum.append(np.nan)
                victorias_acum.append(0)
                win_loss_acum.append(np.nan)

        resultados['frecuencias'].append(fr_acum)
        resultados['capital'].append(capital_acum)
        resultados['victorias_acumuladas'].append(victorias_acum)
        resultados['win_loss_ratio'].append(win_loss_acum)
        if en_bancarrota:
            resultados['bancarrotas'] += 1

    return resultados


def graficar_resultados(resultados, n_tiradas, n_corridas, numero_elegido, estrategia, capital_tipo, capital_inicial=1000):
    """
    Genera las gráficas: frecuencia relativa, flujo de caja, histograma de capital final,
    relación victorias/derrotas, capital promedio y victorias acumuladas, y las muestra en pantalla
    """
    # Configuración común para las gráficas
    plt.style.use('seaborn-v0_8')
    figsize = (10, 6)
    x_vals = range(1, n_tiradas + 1)
    prob_teorica = 1/37 if numero_elegido is not None else None

    # Inicializar capitales_finales
    capitales_finales = [corrida[-1] if corrida else np.nan for corrida in resultados['capital']]
    capitales_finales = np.array(capitales_finales)
    capitales_finales = capitales_finales[np.isfinite(capitales_finales)]

    # 1. Gráfico de frecuencia relativa (una corrida)
    if numero_elegido is not None and resultados['frecuencias']:
        plt.figure(figsize=figsize)
        y_vals_freq = resultados['frecuencias'][0]
        plt.plot(x_vals[:len(y_vals_freq)], y_vals_freq, label='Frecuencia relativa obtenida', color='red')
        # plt.ylim(0, max(y_vals_capital) * 1.1)
        plt.axhline(y=prob_teorica, color='black', linestyle='--', label='Probabilidad teórica')
        plt.title(f'Frecuencia relativa del número {numero_elegido} (1 corrida)')
        plt.xlabel('Número de tiradas')
        plt.ylabel('Frecuencia relativa')
        plt.legend()
        plt.grid(True)
        plt.show()

    # 2. Gráfico de flujo de caja (una corrida)
    if resultados['capital']:
        plt.figure(figsize=figsize)
        y_vals_capital = resultados['capital'][0]
        plt.plot(x_vals[:len(y_vals_capital)], y_vals_capital, label='Flujo de caja', color='red')
        plt.axhline(y=capital_inicial if capital_tipo == 'f' else 0, color='blue', linestyle='--', label='Capital inicial')
        plt.title(f'Flujo de caja (1 corrida, Estrategia: {estrategia.upper()}, Capital: {capital_tipo.upper()})')
        plt.xlabel('Número de tiradas')
        plt.ylabel('Cantidad de capital')
        plt.legend()
        plt.grid(True)
        plt.show()

    # 3. Histograma del capital final (todas las corridas)
    if len(capitales_finales) > 0:
        plt.figure(figsize=figsize)
        plt.hist(capitales_finales, bins=20, color='green', alpha=0.7)
        plt.ylim(0, max(np.histogram(capitales_finales, bins=20)[0]) * 1.1)

        plt.xlabel('Capital final')
        plt.ylabel('Frecuencia')
        plt.title('Distribución de capitales finales')
        plt.show()
    else:
        print("No hay datos válidos para graficar el capital final.")

    # 4. Relación victorias/derrotas (una corrida)
    if numero_elegido is not None and resultados['win_loss_ratio']:
        plt.figure(figsize=figsize)
        y_vals_ratio = resultados['win_loss_ratio'][0]
        plt.plot(x_vals[:len(y_vals_ratio)], y_vals_ratio, label='Relación victorias/derrotas', color='purple')
        plt.title(f'Relación victorias/derrotas (1 corrida)')
        plt.xlabel('Número de tiradas')
        plt.ylabel('Relación (victorias/derrotas)')
        plt.legend()
        plt.grid(True)
        plt.show()

    # 5. Capital promedio (todas las corridas)
    if resultados['capital']:
        max_len = max(len(cap) for cap in resultados['capital'])
        padded_capital = [cap + [np.nan] * (max_len - len(cap)) for cap in resultados['capital']]
        capital_promedio = np.nanmean(padded_capital, axis=0)
        capital_std = np.nanstd(padded_capital, axis=0)
        plt.figure(figsize=figsize)
        plt.plot(x_vals[:len(capital_promedio)], capital_promedio, label='Capital promedio', color='orange')
        plt.ylim(0, np.nanmax(capital_promedio + capital_std) * 1.1)
        plt.fill_between(x_vals[:len(capital_promedio)], capital_promedio - capital_std, capital_promedio + capital_std, color='orange', alpha=0.2, label='±1 Desviación estándar')
        plt.axhline(y=capital_inicial if capital_tipo == 'f' else 0, color='blue', linestyle='--', label='Capital inicial')
        plt.title(f'Capital promedio ({n_corridas} corridas)')
        plt.xlabel('Número de tiradas')
        plt.ylabel('Cantidad de capital')
        plt.legend()
        plt.grid(True)
        plt.show()

    # 6. Victorias acumuladas (una corrida)
    if numero_elegido is not None and resultados['victorias_acumuladas']:
        plt.figure(figsize=figsize)
        y_vals_victorias = resultados['victorias_acumuladas'][0]
        plt.plot(x_vals[:len(y_vals_victorias)], y_vals_victorias, label='Victorias acumuladas', color='blue')
        plt.title(f'Victorias acumuladas (1 corrida)')
        plt.xlabel('Número de tiradas')
        plt.ylabel('Número de victorias')
        plt.legend()
        plt.grid(True)
        plt.show()

# 7. Bancarrotas: barras + pastel
    if capital_tipo == 'f':
        bancarrotas   = resultados['bancarrotas']
        no_banca      = n_corridas - bancarrotas
        labels        = ['Bancarrota', 'No Bancarrota']
        valores       = [bancarrotas, no_banca]

        plt.figure(figsize=(12, 5))

        # 7a. Barra
        plt.subplot(1, 2, 1)
        plt.bar(labels, valores, color=['red', 'green'])
        plt.title('Veces en bancarrota')
        plt.ylabel('Número de simulaciones')
        plt.grid(axis='y', linestyle='--', alpha=0.7)

        # 7b. Pastel
        plt.subplot(1, 2, 2)
        plt.pie(valores,
                labels=labels,
                autopct='%1.1f%%',
                startangle=90)
        plt.title('Porcentaje de bancarrotas')

        plt.tight_layout()
        plt.show()
    else:
        print("No se generará gráfico de bancarrotas, ya que el capital es infinito.")


def main():
    # Configurar argumentos de línea de comandos
    parser = argparse.ArgumentParser(description='Simulación de Ruleta')
    parser.add_argument('-n', '--tiradas', type=int, default=1000,
                        help='Número de tiradas por corrida')
    parser.add_argument('-c', '--corridas', type=int, default=5,
                        help='Número de corridas a simular')
    parser.add_argument('-e', '--numero', type=int, required=False,
                        help='Número elegido para análisis de frecuencia (0-36)')
    parser.add_argument('-s', '--estrategia', choices=['m', 'd', 'f', 'o'], default='m',
                        help='Estrategia de apuesta: m (Martingala), d (D’Alembert), f (Fibonacci), o (Paroli)')
    parser.add_argument('-a', '--capital', choices=['i', 'f'], default='i',
                        help='Tipo de capital: i (infinito), f (finito)')
    parser.add_argument('--capital_inicial', type=int, default=1000,
                        help='Capital inicial para simulaciones con capital finito')
    args = parser.parse_args()

    # Validar número elegido
    if args.numero is not None and not (0 <= args.numero <= 36):
        raise ValueError("El número elegido debe estar entre 0 y 36")

    # Ejecutar simulación
    resultados = simular_ruleta(
        args.tiradas, args.corridas, args.numero, args.estrategia, args.capital, args.capital_inicial
    )

    # Generar gráficos
    graficar_resultados(resultados, args.tiradas, args.corridas, args.numero, args.estrategia, args.capital, args.capital_inicial)

if __name__ == '__main__':
    main()