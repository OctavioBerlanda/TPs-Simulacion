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
        'win_loss_ratio': []
    }
    
    for _ in range(n_corridas):
        # Inicializar capital
        capital = capital_inicial if capital_tipo == 'f' else float('inf')
        capital_acum = []
        
        # Simular tiradas
        tiradas = [random.choice(numeros_ruleta) for _ in range(n_tiradas)]
        
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
        
        for i in range(1, n_tiradas+1):
            # Simular apuesta según estrategia
            if capital_tipo == 'f' and capital < apuesta_actual:
                apuesta_actual = max(capital, 0)  # No apostar más del capital disponible
            
            # Determinar si ganamos (para un solo número o cualquier apuesta)
            gano = numero_elegido is not None and tiradas[i-1] == numero_elegido
            
            # Actualizar capital según resultado
            if gano:
                capital += apuesta_actual * 35  # Pago 35:1 para apuesta a número
                victorias_consecutivas += 1
                conteo_victorias += 1
            else:
                capital -= apuesta_actual
                victorias_consecutivas = 0
                conteo_derrotas += 1
            
            # Actualizar apuesta según estrategia
            if estrategia == 'm':  # Martingala
                apuesta_actual = apuesta_base if gano else apuesta_actual * 2
            elif estrategia == 'd':  # D'Alembert
                apuesta_actual = max(apuesta_base, apuesta_actual + (10 if not gano else -10))
            elif estrategia == 'f':  # Fibonacci
                if gano:
                    fib_index = max(0, fib_index - 2)
                else:
                    fib_index = min(len(fibonacci) - 1, fib_index + 1)
                apuesta_actual = apuesta_base * fibonacci[fib_index]
            elif estrategia == 'o':  # Paroli (custom)
                if gano and victorias_consecutivas < 3:
                    apuesta_actual *= 2
                else:
                    apuesta_actual = apuesta_base
            
            capital_acum.append(capital)
            
            # Estadísticas (solo si se especificó un número elegido)
            if numero_elegido is not None:
                if tiradas[i-1] == numero_elegido:
                    conteo += 1
                fr = conteo / i
                fr_acum.append(fr)
                victorias_acum.append(conteo)
                # Relación victorias/derrotas
                if conteo_derrotas > 0:
                    ratio = conteo_victorias / conteo_derrotas
                else:
                    ratio = conteo_victorias  # Evitar división por 0
                win_loss_acum.append(ratio)
            else:
                fr_acum.append(0)
                victorias_acum.append(0)
                win_loss_acum.append(0)
        
        resultados['frecuencias'].append(fr_acum)
        resultados['capital'].append(capital_acum)
        resultados['victorias_acumuladas'].append(victorias_acum)
        resultados['win_loss_ratio'].append(win_loss_acum)
    
    return resultados

def graficar_resultados(resultados, n_tiradas, n_corridas, numero_elegido, estrategia, capital_tipo, capital_inicial=1000):
    """
    Genera las gráficas: frecuencia relativa, flujo de caja, histograma de capital final,
    relación victorias/derrotas, capital promedio y victorias acumuladas, y las muestra en pantalla
    """
    # Configuración común para las gráficas
    plt.style.use('seaborn-v0_8')
    figsize = (10, 6)
    x_vals = range(1, n_tiradas+1)
    prob_teorica = 1/37 if numero_elegido is not None else None
    
    # 1. Gráfico de frecuencia relativa (una corrida)
    if numero_elegido is not None:
        plt.figure(figsize=figsize)
        plt.plot(x_vals, resultados['frecuencias'][0], label='frsa (Frecuencia relativa obtenida)', color='red')
        plt.axhline(y=prob_teorica, color='black', linestyle='--', label='Probabilidad teórica')
        plt.title(f'Frecuencia relativa del número {numero_elegido} (1 corrida)')
        plt.xlabel('n (número de tiradas)')
        plt.ylabel('fr (frecuencia relativa)')
        plt.legend()
        plt.grid(True)
        plt.show()
    
    # 2. Gráfico de flujo de caja (una corrida)
    plt.figure(figsize=figsize)
    plt.plot(x_vals, resultados['capital'][0], label='fc (flujo de caja)', color='red')
    plt.axhline(y=capital_inicial, color='blue', linestyle='--', label='fci (flujo de caja inicial)')
    plt.title(f'Flujo de caja (1 corrida, Estrategia: {estrategia.upper()}, Capital: {capital_tipo.upper()})')
    plt.xlabel('n (número de tiradas)')
    plt.ylabel('cc (cantidad de capital)')
    plt.legend()
    plt.grid(True)
    plt.show()
    
    # 3. Histograma del capital final (todas las corridas)
    capitales_finales = [corrida[-1] for corrida in resultados['capital']]
    plt.figure(figsize=figsize)
    plt.hist(capitales_finales, bins=20, color='green', alpha=0.7)
    plt.title(f'Distribución del capital final ({n_corridas} corridas)')
    plt.xlabel('Capital final')
    plt.ylabel('Frecuencia (número de corridas)')
    plt.grid(True)
    plt.show()
    
    # 4. Relación victorias/derrotas (una corrida)
    if numero_elegido is not None:
        plt.figure(figsize=figsize)
        plt.plot(x_vals, resultados['win_loss_ratio'][0], label='Relación victorias/derrotas', color='purple')
        plt.title(f'Relación victorias/derrotas (1 corrida)')
        plt.xlabel('n (número de tiradas)')
        plt.ylabel('Relación (victorias/derrotas)')
        plt.legend()
        plt.grid(True)
        plt.show()
    
    # 5. Capital promedio (todas las corridas)
    capital_promedio = np.mean(resultados['capital'], axis=0)
    capital_std = np.std(resultados['capital'], axis=0)
    plt.figure(figsize=figsize)
    plt.plot(x_vals, capital_promedio, label='Capital promedio', color='orange')
    plt.fill_between(x_vals, capital_promedio - capital_std, capital_promedio + capital_std, color='orange', alpha=0.2, label='±1 Desviación estándar')
    plt.axhline(y=capital_inicial, color='blue', linestyle='--', label='Capital inicial')
    plt.title(f'Capital promedio ({n_corridas} corridas)')
    plt.xlabel('n (número de tiradas)')
    plt.ylabel('cc (cantidad de capital)')
    plt.legend()
    plt.grid(True)
    plt.show()
    
    # 6. Victorias acumuladas (una corrida)
    if numero_elegido is not None:
        plt.figure(figsize=figsize)
        plt.plot(x_vals, resultados['victorias_acumuladas'][0], label='Victorias acumuladas', color='blue')
        plt.title(f'Victorias acumuladas (1 corrida)')
        plt.xlabel('n (número de tiradas)')
        plt.ylabel('Número de victorias')
        plt.legend()
        plt.grid(True)
        plt.show()
    


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
    
    args = parser.parse_args()
    
    # Validar número elegido
    if args.numero is not None and not (0 <= args.numero <= 36):
        raise ValueError("El número elegido debe estar entre 0 y 36")
    
    # Ejecutar simulación
    resultados = simular_ruleta(args.tiradas, args.corridas, args.numero, args.estrategia, args.capital)
    
    # Generar gráficos
    graficar_resultados(resultados, args.tiradas, args.corridas, args.numero, args.estrategia, args.capital)

if __name__ == '__main__':
    main()