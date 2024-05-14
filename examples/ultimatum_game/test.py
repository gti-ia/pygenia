from scipy.optimize import minimize


def funcion_objetivo(dinero, emocion_propia, emocion_rival):
    # Aquí defines cómo combinar las emociones propia y del rival en la función objetivo
    # Por ejemplo, podrías sumar las emociones propia y del rival ponderadas por algún factor
    return -(dinero[0] * emocion_propia + (dinero[1]) * emocion_rival)


# Función de restricción: suma total del dinero igual a una cantidad fija
def restriccion_suma_total(dinero, cantidad_total_dinero):
    return dinero.sum() - cantidad_total_dinero


# Función de restricción: el dinero repartido no puede ser negativo
def restriccion_no_negativo0(dinero):
    return dinero[0]


# Función de restricción: el dinero repartido no puede ser negativo
def restriccion_no_negativo1(dinero):
    return dinero[1]


# Condiciones iniciales
dinero_inicial = [1, 1]  # Por ejemplo, 2 jugadores
cantidad_total_dinero = 10  # Cantidad total de dinero a repartir
emocion_propia = 0.25  # Emoción propia del jugador
emocion_rival = 0.1  # Emoción del rival

# Definir las restricciones
restricciones = [
    {"type": "eq", "fun": restriccion_suma_total, "args": (cantidad_total_dinero,)},
    {"type": "ineq", "fun": restriccion_no_negativo0},
    {"type": "ineq", "fun": restriccion_no_negativo1},
]

limites = [(0, None)] * len(dinero_inicial)

# Resolver el problema de optimización
resultado = minimize(
    funcion_objetivo,
    dinero_inicial,
    args=(emocion_propia, emocion_rival),
    constraints=restricciones,
    bounds=limites,
)

# Imprimir el resultado
print("Dinero óptimo a repartir:", resultado.x)

print("Valor óptimo de la función objetivo:", -resultado.fun)
