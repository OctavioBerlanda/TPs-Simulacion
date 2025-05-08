def generador_cuadrados_medios(semilla, cantidad, digitos=4):
    """Genera números pseudoaleatorios usando el método de los cuadrados medios."""
    numeros = []
    x = semilla
    for _ in range(cantidad):
        x_cuadrado = str(x**2).zfill(2*digitos)
        mitad = len(x_cuadrado) // 2
        x = int(x_cuadrado[mitad - digitos//2 : mitad + digitos//2])
        numeros.append(x / (10**digitos))
    return numeros

semilla = 5731  # Tiene que tener tantos dígitos como definas (4 en este caso)
cantidad = 1000

numeros_cm = generador_cuadrados_medios(semilla, cantidad)
