import random
import argparse
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import PercentFormatter

def simular_ruleta(n_tiradas, n_corridas, seleccion=None, estrategia='m', capital_tipo='i', capital_inicial=1000, tipo_apuesta='numero'):
    """
    Simula múltiples corridas de una ruleta con diversas estrategias de apuesta
    
    Args:
        n_tiradas: Número de tiradas por corrida
        n_corridas: Número de corridas a simular
        seleccion: Número o característica a apostar (ej: 17, 'rojo', 'par', etc.)
        estrategia: Estrategia de apuesta ('m': Martingala, 'd': D'Alembert, 'f': Fibonacci, 'o': Paroli, 'p': Pleno)
        capital_tipo: Tipo de capital ('i': infinito, 'f': finito)
        capital_inicial: Capital inicial para capital finito
        tipo_apuesta: Tipo de apuesta ('numero', 'color', 'docena', 'columna', 'par_impar', 'alto_bajo')
    """
    # Configuración de la ruleta (europea: 0-36)
    numeros_ruleta = list(range(37))
    
    # Definición de grupos de apuestas
    rojos = {1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36}
    negros = set(range(1,37)) - rojos
    
    docenas = {
        1: range(1,13),
        2: range(13,25),
        3: range(25,37)
    }
    
    columnas = {
        1: {1,4,7,10,13,16,19,22,25,28,31,34},
        2: {2,5,8,11,14,17,20,23,26,29,32,35},
        3: {3,6,9,12,15,18,21,24,27,30,33,36}
    }
    
    # Determinar automáticamente el tipo de apuesta si no se especifica
    if tipo_apuesta is None:
        if isinstance(seleccion, int):
            if 0 <= seleccion <= 36:
                tipo_apuesta = 'numero'
            elif 1 <= seleccion <= 3:
                tipo_apuesta = random.choice(['docena', 'columna'])
        elif isinstance(seleccion, str):
            if seleccion.lower() in ['rojo', 'negro']:
                tipo_apuesta = 'color'
            elif seleccion.lower() in ['par', 'impar']:
                tipo_apuesta = 'par_impar'
            elif seleccion.lower() in ['alto', 'bajo']:
                tipo_apuesta = 'alto_bajo'
        else:
            tipo_apuesta = 'numero'  # Default
    
    # Validar selección según tipo de apuesta inferido
    if tipo_apuesta == 'numero' and seleccion is not None and not (0 <= seleccion <= 36):
        raise ValueError("Para apuesta a número, la selección debe estar entre 0 y 36")
    elif tipo_apuesta == 'color' and seleccion not in ['rojo', 'negro']:
        raise ValueError("Para apuesta a color, la selección debe ser 'rojo' o 'negro'")
    elif tipo_apuesta == 'docena' and seleccion not in [1, 2, 3]:
        raise ValueError("Para apuesta a docena, la selección debe ser 1, 2 o 3")
    elif tipo_apuesta == 'columna' and seleccion not in [1, 2, 3]:
        raise ValueError("Para apuesta a columna, la selección debe ser 1, 2 o 3")
    elif tipo_apuesta == 'par_impar' and seleccion not in ['par', 'impar']:
        raise ValueError("Para apuesta a par/impar, la selección debe ser 'par' o 'impar'")
    elif tipo_apuesta == 'alto_bajo' and seleccion not in ['alto', 'bajo']:
        raise ValueError("Para apuesta a alto/bajo, la selección debe ser 'alto' o 'bajo'")
    
    # Calcular probabilidad teórica según tipo de apuesta
    if tipo_apuesta == 'numero':
        prob_teorica = 1/37
        pago = 35  # Pago 35:1
    elif tipo_apuesta == 'color':
        prob_teorica = 18/37
        pago = 1  # Pago 1:1
    elif tipo_apuesta == 'docena' or tipo_apuesta == 'columna':
        prob_teorica = 12/37
        pago = 2  # Pago 2:1
    elif tipo_apuesta == 'par_impar' or tipo_apuesta == 'alto_bajo':
        prob_teorica = 18/37
        pago = 1  # Pago 1:1
    else:
        prob_teorica = None
        pago = None

    # Almacenar resultados de todas las corridas
    resultados = {
        'frecuencias': [],
        'capital': [],
        'ganancias_perdidas': [],  # Nuevo: registro de ganancias/pérdidas
        'victorias_acumuladas': [],
        'win_loss_ratio': [],
        'bancarrotas': 0,
        'capital_final': [],
        'ganancia_neta': [],
        'tipo_apuesta': tipo_apuesta,
        'seleccion': seleccion
    }

    for _ in range(n_corridas):
        # Inicializar capital y ganancias/pérdidas
        capital = capital_inicial if capital_tipo == 'f' else float('inf')
        ganancias_perdidas = 0  # Registro de ganancias/pérdidas acumuladas
        capital_acum = []
        ganancias_perdidas_acum = []  # Registro acumulado de ganancias/pérdidas
        en_bancarrota = False

        # Simular tiradas
        tiradas = [random.choice(numeros_ruleta) for _ in range(n_tiradas)]

        # Estadísticas acumulativas
        fr_acum = []  # Frecuencia relativa acumulada
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

            # Determinar si ganó la apuesta
            gano = False
            numero_salido = tiradas[i - 1]
            
            if tipo_apuesta == 'numero':
                gano = (seleccion is not None and numero_salido == seleccion)
            elif tipo_apuesta == 'color':
                if seleccion == 'rojo':
                    gano = (numero_salido in rojos)
                elif seleccion == 'negro':
                    gano = (numero_salido in negros)
            elif tipo_apuesta == 'docena':
                gano = (numero_salido in docenas.get(seleccion, set()))
            elif tipo_apuesta == 'columna':
                gano = (numero_salido in columnas.get(seleccion, set()))
            elif tipo_apuesta == 'par_impar':
                if seleccion == 'par':
                    gano = (numero_salido != 0 and numero_salido % 2 == 0)
                elif seleccion == 'impar':
                    gano = (numero_salido % 2 == 1)
            elif tipo_apuesta == 'alto_bajo':
                if seleccion == 'alto':
                    gano = (18 < numero_salido <= 36)
                elif seleccion == 'bajo':
                    gano = (1 <= numero_salido <= 18)

            # Actualizar ganancias/pérdidas según resultado
            if gano:
                ganancias_perdidas += apuesta_actual * pago
            else:
                ganancias_perdidas -= apuesta_actual

            # Actualizar capital según tipo
            if capital_tipo == 'f':
                if gano:
                    capital += apuesta_actual * pago
                else:
                    capital -= apuesta_actual
            else:
                capital = float('inf')  # Mantener como infinito

            # Registrar ambos valores
            capital_acum.append(capital)
            ganancias_perdidas_acum.append(ganancias_perdidas)

            # Actualizar apuesta según estrategia
            if estrategia == 'm':  # Martingala
                apuesta_actual = apuesta_base if gano else apuesta_actual * 2
            elif estrategia == 'd':  # D'Alembert
                apuesta_actual = max(apuesta_base, apuesta_actual + (apuesta_base if not gano else -apuesta_base))
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
            elif estrategia == 'p':  # Pleno (apuesta fija)
                apuesta_actual = apuesta_base  # Siempre la misma apuesta

            # Estadísticas (solo si se especificó una selección)
            if seleccion is not None:
                if gano:
                    conteo += 1
                    conteo_victorias += 1
                    victorias_consecutivas += 1
                else:
                    conteo_derrotas += 1
                    victorias_consecutivas = 0
                
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
            ganancias_perdidas_acum.append(ganancias_perdidas_acum[-1] if ganancias_perdidas_acum else 0)
            if seleccion is not None:
                fr_acum.append(fr_acum[-1] if fr_acum else np.nan)
                victorias_acum.append(victorias_acum[-1] if victorias_acum else 0)
                win_loss_acum.append(win_loss_acum[-1] if win_loss_acum else np.nan)
            else:
                fr_acum.append(np.nan)
                victorias_acum.append(0)
                win_loss_acum.append(np.nan)

        resultados['frecuencias'].append(fr_acum)
        resultados['capital'].append(capital_acum)
        resultados['ganancias_perdidas'].append(ganancias_perdidas_acum)
        resultados['victorias_acumuladas'].append(victorias_acum)
        resultados['win_loss_ratio'].append(win_loss_acum)
        resultados['capital_final'].append(capital_acum[-1] if capital_acum else np.nan)
        resultados['ganancia_neta'].append((capital_acum[-1] - capital_inicial) if capital_tipo == 'f' else ganancias_perdidas_acum[-1])
        if en_bancarrota:
            resultados['bancarrotas'] += 1

    return resultados


def graficar_resultados(resultados, n_tiradas, n_corridas, estrategia, capital_tipo, capital_inicial=1000):
    """
    Genera las gráficas: frecuencia relativa, flujo de caja, histograma de capital final,
    relación victorias/derrotas, capital promedio y victorias acumuladas, y las muestra en pantalla
    """
    # Configuración común para las gráficas
    plt.style.use('seaborn-v0_8')
    figsize = (10, 6)
    x_vals = range(1, n_tiradas + 1)
    
    # Obtener tipo de apuesta y selección de los resultados
    tipo_apuesta = resultados.get('tipo_apuesta', 'numero')
    seleccion = resultados.get('seleccion', None)
    
    # Calcular probabilidad teórica según tipo de apuesta
    if tipo_apuesta == 'numero':
        prob_teorica = 1/37
    elif tipo_apuesta == 'color':
        prob_teorica = 18/37
    elif tipo_apuesta == 'docena' or tipo_apuesta == 'columna':
        prob_teorica = 12/37
    elif tipo_apuesta == 'par_impar' or tipo_apuesta == 'alto_bajo':
        prob_teorica = 18/37
    else:
        prob_teorica = None

    # Inicializar capitales_finales
    capitales_finales = resultados['capital_final']
    capitales_finales = np.array(capitales_finales)
    capitales_finales = capitales_finales[np.isfinite(capitales_finales)]

    # 1. Gráfico de frecuencia relativa (una corrida)
    if seleccion is not None and resultados['frecuencias']:
        plt.figure(figsize=figsize)
        y_vals_freq = resultados['frecuencias'][0]
        plt.plot(x_vals[:len(y_vals_freq)], y_vals_freq, label='Frecuencia relativa obtenida', color='red')
        if prob_teorica is not None:
            plt.axhline(y=prob_teorica, color='black', linestyle='--', label='Probabilidad teórica')
        title = f'Frecuencia relativa de {tipo_apuesta} {seleccion} (1 corrida)' if seleccion is not None else f'Frecuencia relativa (1 corrida)'
        plt.title(title)
        plt.xlabel('Número de tiradas')
        plt.ylabel('Frecuencia relativa')
        plt.legend()
        plt.grid(True)
        plt.show()

 # 2. Gráfico de cambios por tirada (1 corrida) - Versión corregida
    if resultados.get('ganancias_perdidas') and len(resultados['ganancias_perdidas'][0]) > 1:
        plt.figure(figsize=figsize)
        datos_corrida = resultados['ganancias_perdidas'][0]  # Usamos ganancias/pérdidas
        
        # Calcular diferencias entre tiradas consecutivas
        cambios = [datos_corrida[i] - datos_corrida[i-1] for i in range(1, len(datos_corrida))]
        
        plt.bar(range(1, len(cambios)+1), cambios, 
               color=['green' if x > 0 else 'red' for x in cambios],
               width=1.0, alpha=0.6)
        
        plt.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
        title = 'Cambios en ganancias/pérdidas por tirada' if capital_tipo == 'i' else 'Cambios en capital por tirada'
        plt.title(f'{title} - Estrategia: {estrategia.upper()}')
        plt.xlabel('Número de tirada')
        plt.ylabel('Cambio en ganancias/pérdidas' if capital_tipo == 'i' else 'Cambio en capital')
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.show()

    # 3. Histograma del capital final (todas las corridas)
    if len(capitales_finales) > 0:
        plt.figure(figsize=figsize)
        plt.hist(capitales_finales, bins=20, color='green', alpha=0.7)
        plt.xlabel('Capital final')
        plt.ylabel('Frecuencia')
        plt.title('Distribución de capitales finales')
        plt.grid(True)
        plt.show()
    else:
        print("No hay datos válidos para graficar el capital final.")

    # 4. Relación victorias/derrotas (una corrida)
    if seleccion is not None and resultados['win_loss_ratio']:
        plt.figure(figsize=figsize)
        y_vals_ratio = resultados['win_loss_ratio'][0]
        plt.plot(x_vals[:len(y_vals_ratio)], y_vals_ratio, label='Relación victorias/derrotas', color='purple')
        plt.title(f'Relación victorias/derrotas (1 corrida)')
        plt.xlabel('Número de tiradas')
        plt.ylabel('Relación (victorias/derrotas)')
        plt.legend()
        plt.grid(True)
        plt.show()

    # 5. Gráfico de ganancias/pérdidas o capital promedio
    if resultados.get('ganancias_perdidas'):
        datos = resultados['ganancias_perdidas'] if capital_tipo == 'i' else resultados['capital']
        max_len = max(len(cap) for cap in datos)
        padded_data = [cap + [np.nan] * (max_len - len(cap)) for cap in datos]
        
        promedio = np.nanmean(padded_data, axis=0)
        std = np.nanstd(padded_data, axis=0)
        
        plt.figure(figsize=figsize)
        
        y_label = 'Ganancias/Pérdidas Promedio' if capital_tipo == 'i' else 'Capital promedio'
        referencia = 0  # Siempre comparamos con el punto de equilibrio
        
        plt.plot(x_vals[:len(promedio)], promedio, label=y_label, color='orange')
        plt.fill_between(x_vals[:len(promedio)], 
                        promedio - std, 
                        promedio + std, 
                        color='orange', alpha=0.2, label='±1 Desviación estándar')
        plt.axhline(y=referencia, color='blue', linestyle='--', label='Punto de equilibrio')
        plt.title(f'{y_label} ({n_corridas} corridas)')
        plt.xlabel('Número de tiradas')
        plt.ylabel(y_label)
        plt.legend()
        plt.grid(True)
        plt.show()
        
    # 6. Victorias acumuladas (una corrida)
    if seleccion is not None and resultados['victorias_acumuladas']:
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
        bancarrotas = resultados['bancarrotas']
        no_banca = n_corridas - bancarrotas
        labels = ['Bancarrota', 'No Bancarrota']
        valores = [bancarrotas, no_banca]

        plt.figure(figsize=(12, 5))

        # 7a. Barra
        plt.subplot(1, 2, 1)
        plt.bar(labels, valores, color=['red', 'green'])
        plt.title('Veces en bancarrota')
        plt.ylabel('Número de simulaciones')
        plt.grid(axis='y', linestyle='--', alpha=0.7)

        # 7b. Pastel
        plt.subplot(1, 2, 2)
        plt.pie(valores, labels=labels, autopct='%1.1f%%', startangle=90)
        plt.title('Porcentaje de bancarrotas')

        plt.tight_layout()
        plt.show()
    else:
        print("No se generará gráfico de bancarrotas, ya que el capital es infinito.")

    # 8. Ganancia/pérdida neta
    if capital_tipo == 'f' and len(resultados['ganancia_neta']) > 0:
        ganancias_netas = np.array(resultados['ganancia_neta'])
        ganancias_netas = ganancias_netas[np.isfinite(ganancias_netas)]
        
        if len(ganancias_netas) > 0:
            plt.figure(figsize=figsize)
            plt.hist(ganancias_netas, bins=20, color='blue', alpha=0.7)
            plt.axvline(x=0, color='red', linestyle='--', label='Punto de equilibrio')
            plt.xlabel('Ganancia/Pérdida Neta')
            plt.ylabel('Frecuencia')
            plt.title('Distribución de ganancias netas')
            plt.legend()
            plt.grid(True)
            plt.show()


def main():
    # Configurar argumentos de línea de comandos simplificados
    parser = argparse.ArgumentParser(description='Simulación de Ruleta con Estrategias Avanzadas')
    parser.add_argument('-c', type=int, default=5,
                       help='Número de corridas a simular (opcional, default=5)')
    parser.add_argument('-n', type=int, default=1000,
                       help='Número de tiradas por corrida (opcional, default=1000)')
    parser.add_argument('-e', default=None,
                       help='Selección para la apuesta (ej: 17, "rojo", "par", etc.) (opcional)')
    parser.add_argument('-s', choices=['m', 'd', 'f', 'o', 'p'], default='m',
                       help='Estrategia de apuesta: m (Martingala), d (D’Alembert), f (Fibonacci), o (Paroli), p (Pleno) (opcional, default=m)')
    parser.add_argument('-a', choices=['i', 'f'], default='i',
                       help='Tipo de capital: i (infinito), f (finito) (opcional, default=i)')
    
    # Argumentos opcionales adicionales
    parser.add_argument('--capital_inicial', type=int, default=1000,
                       help='Capital inicial para simulaciones con capital finito (opcional, default=1000)')
    parser.add_argument('--tipo_apuesta', 
                       choices=['numero', 'color', 'docena', 'columna', 'par_impar', 'alto_bajo'],
                       default=None,
                       help='Tipo de apuesta: numero, color, docena, columna, par_impar, alto_bajo (opcional)')
    
    args = parser.parse_args()

    # Convertir selección a tipo apropiado
    seleccion = args.e
    if seleccion is not None:
        try:
            # Intentar convertir a número si es posible
            seleccion = int(seleccion)
        except ValueError:
            # Si no es número, mantener como string y convertir a minúsculas
            seleccion = seleccion.lower()

    # Determinar automáticamente el tipo de apuesta si no se especifica
    tipo_apuesta = args.tipo_apuesta
    if tipo_apuesta is None and seleccion is not None:
        if isinstance(seleccion, int):
            if 0 <= seleccion <= 36:
                tipo_apuesta = 'numero'
            elif 1 <= seleccion <= 3:
                tipo_apuesta = random.choice(['docena', 'columna'])
        elif isinstance(seleccion, str):
            if seleccion in ['rojo', 'negro']:
                tipo_apuesta = 'color'
            elif seleccion in ['par', 'impar']:
                tipo_apuesta = 'par_impar'
            elif seleccion in ['alto', 'bajo']:
                tipo_apuesta = 'alto_bajo'
    
    # Si aún no se determinó, usar número como default
    if tipo_apuesta is None:
        tipo_apuesta = 'numero'
        seleccion = random.randint(0, 36)  # Seleccionar un número aleatorio

    # Ejecutar simulación
    resultados = simular_ruleta(
        n_tiradas=args.n,
        n_corridas=args.c,
        seleccion=seleccion,
        estrategia=args.s,
        capital_tipo=args.a,
        capital_inicial=args.capital_inicial,
        tipo_apuesta=tipo_apuesta
    )

    # Generar gráficos
    graficar_resultados(
        resultados=resultados,
        n_tiradas=args.n,
        n_corridas=args.c,
        estrategia=args.s,
        capital_tipo=args.a,
        capital_inicial=args.capital_inicial
    )

if __name__ == '__main__':
    main()