import random
import argparse
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import PercentFormatter

def simular_ruleta(n_tiradas, n_corridas, numero_elegido):
    """
    Simula múltiples corridas de una ruleta y calcula estadísticas
    """
    # Configuración de la ruleta (europea: 0-36)
    numeros_ruleta = list(range(37))
    prob_teorica = 1/37
    
    # Almacenar resultados de todas las corridas
    resultados = {
        'frecuencias': [],
        'promedios': [],
        'varianzas': [],
        'desvios': []
    }
    
    for _ in range(n_corridas):
        # Simular tiradas
        tiradas = [random.choice(numeros_ruleta) for _ in range(n_tiradas)]
        
        # Calcular estadísticas acumulativas
        fr_acum = []  # Frecuencia relativa acumulada del número elegido
        vp_acum = []  # Valor promedio acumulado
        vv_acum = []  # Varianza acumulada
        vd_acum = []  # Desvío acumulado
        
        conteo = 0
        suma = 0
        suma_cuadrados = 0
        
        for i in range(1, n_tiradas+1):
            if tiradas[i-1] == numero_elegido:
                conteo += 1
            suma += tiradas[i-1]
            suma_cuadrados += tiradas[i-1]**2
            
            # Frecuencia relativa
            fr = conteo / i
            fr_acum.append(fr)
            
            # Valor promedio
            vp = suma / i
            vp_acum.append(vp)
            
            # Varianza
            if i > 1:
                varianza = (suma_cuadrados - (suma**2)/i) / (i-1)
            else:
                varianza = 0
            vv_acum.append(varianza)
            
            # Desvío (diferencia entre fr observada y teórica)
            desvio = abs(fr - prob_teorica)
            vd_acum.append(desvio)
        
        resultados['frecuencias'].append(fr_acum)
        resultados['promedios'].append(vp_acum)
        resultados['varianzas'].append(vv_acum)
        resultados['desvios'].append(vd_acum)
    
    return resultados

def graficar_resultados(resultados, n_tiradas, n_corridas, numero_elegido):
    """
    Genera las gráficas solicitadas a partir de los resultados
    """
    # Configuración común para todas las gráficas
    plt.style.use('seaborn-v0_8')
    figsize = (10, 6)
    x_vals = range(1, n_tiradas+1)
    prob_teorica = 1/37
    promedio_teorico = sum(range(37))/37  # 18
    
    # 1. Gráfico de frecuencia relativa (una corrida)
    # Cuántas veces salió tu número elegido (ej: el 17) comparado con lo que debería salir teóricamente.
    plt.figure(figsize=figsize)
    plt.plot(x_vals, resultados['frecuencias'][0], label='Observado')
    plt.axhline(y=prob_teorica, color='r', linestyle='--', label='Teórico')
    plt.title(f'Frecuencia relativa del número {numero_elegido} (1 corrida)')
    plt.xlabel('Número de tiradas')
    plt.ylabel('Frecuencia relativa')
    plt.legend()
    plt.grid(True)
    plt.show()
    
    # 2. Gráfico de frecuencia relativa (todas las corridas)
    plt.figure(figsize=figsize)
    for i in range(n_corridas):
        plt.plot(x_vals, resultados['frecuencias'][i], alpha=0.5)
    plt.axhline(y=prob_teorica, color='r', linestyle='--', label='Teórico')
    plt.title(f'Frecuencia relativa del número {numero_elegido} ({n_corridas} corridas)')
    plt.xlabel('Número de tiradas')
    plt.ylabel('Frecuencia relativa')
    plt.legend()
    plt.grid(True)
    plt.show()
    
    # 3. Gráfico de valor promedio (una corrida)
    # Promedio de los números que van saliendo
    plt.figure(figsize=figsize)
    plt.plot(x_vals, resultados['promedios'][0], label='Observado')
    plt.axhline(y=promedio_teorico, color='r', linestyle='--', label='Teórico')
    plt.title(f'Valor promedio de las tiradas (1 corrida)')
    plt.xlabel('Número de tiradas')
    plt.ylabel('Valor promedio')
    plt.legend()
    plt.grid(True)
    plt.show()
    
    # 4. Gráfico de valor promedio (todas las corridas)
    plt.figure(figsize=figsize)
    for i in range(n_corridas):
        plt.plot(x_vals, resultados['promedios'][i], alpha=0.5)
    plt.axhline(y=promedio_teorico, color='r', linestyle='--', label='Teórico')
    plt.title(f'Valor promedio de las tiradas ({n_corridas} corridas)')
    plt.xlabel('Número de tiradas')
    plt.ylabel('Valor promedio')
    plt.legend()
    plt.grid(True)
    plt.show()
    
    # 5. Gráfico de varianza (una corrida)
    # Que tan dispersos estan los numeros que van saliendo
    plt.figure(figsize=figsize)
    plt.plot(x_vals, resultados['varianzas'][0], label='Observado')
    plt.title(f'Varianza de las tiradas (1 corrida)')
    plt.xlabel('Número de tiradas')
    plt.ylabel('Varianza')
    plt.grid(True)
    plt.show()
    
    # 6. Gráfico de varianza (todas las corridas)
    plt.figure(figsize=figsize)
    for i in range(n_corridas):
        plt.plot(x_vals, resultados['varianzas'][i], alpha=0.5)
    plt.title(f'Varianza de las tiradas ({n_corridas} corridas)')
    plt.xlabel('Número de tiradas')
    plt.ylabel('Varianza')
    plt.grid(True)
    plt.show()
    
    # 7. Gráfico de desvío (una corrida)
    # Diferencia entre lo que sale y lo que deberia salir
    plt.figure(figsize=figsize)
    plt.plot(x_vals, resultados['desvios'][0], label='Observado')
    plt.title(f'Desvío de la frecuencia relativa (1 corrida)')
    plt.xlabel('Número de tiradas')
    plt.ylabel('Desvío (|fr - fr teórica|)')
    plt.grid(True)
    plt.show()
    
    # 8. Gráfico de desvío (todas las corridas)
    plt.figure(figsize=figsize)
    for i in range(n_corridas):
        plt.plot(x_vals, resultados['desvios'][i], alpha=0.5)
    plt.title(f'Desvío de la frecuencia relativa ({n_corridas} corridas)')
    plt.xlabel('Número de tiradas')
    plt.ylabel('Desvío (|fr - fr teórica|)')
    plt.grid(True)
    plt.show()

def main():
    # Configurar argumentos de línea de comandos
    parser = argparse.ArgumentParser(description='Simulación de Ruleta')
    parser.add_argument('-n', '--tiradas', type=int, default=1000, 
                       help='Número de tiradas por corrida')
    parser.add_argument('-c', '--corridas', type=int, default=5, 
                       help='Número de corridas a simular')
    parser.add_argument('-e', '--numero', type=int, default=0, 
                       help='Número elegido para análisis de frecuencia')
    
    args = parser.parse_args()
    
    # Ejecutar simulación
    resultados = simular_ruleta(args.tiradas, args.corridas, args.numero)
    
    # Generar gráficos
    graficar_resultados(resultados, args.tiradas, args.corridas, args.numero)

if __name__ == '__main__':
    main()