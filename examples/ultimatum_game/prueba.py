from itertools import product


def calcular_emocion_propia(dinero, emocion_propia):
    # Aquí defines cómo calcular la emoción propia en función del dinero asignado
    # Por ejemplo, podrías utilizar alguna función que dependa de la cantidad de dinero asignado
    return 1 / emocion_propia * dinero[0] / 10


def calcular_emocion_rival(dinero, emocion_rival):
    # Aquí defines cómo calcular la emoción del rival en función del dinero asignado
    # Por ejemplo, podrías utilizar alguna función que dependa de la cantidad de dinero asignado
    return 1 / emocion_rival * dinero[1] / 10


def encontrar_solucion_optima(emocion_propia, emocion_rival, cantidad_total_dinero):
    mejor_emocion_total = float("-inf")
    mejor_dinero_asignado = None

    # Generar todas las posibles combinaciones de dinero para los jugadores
    for dinero in product(range(cantidad_total_dinero + 1), repeat=2):
        # Verificar que la suma del dinero sea igual a la cantidad total de dinero
        if sum(dinero) == cantidad_total_dinero:
            # Calcular la emoción total para esta asignación de dinero
            emocion_total = calcular_emocion_propia(
                dinero, emocion_propia
            ) + calcular_emocion_rival(dinero, emocion_rival)
            print(
                emocion_total,
                calcular_emocion_propia(dinero, emocion_propia),
                calcular_emocion_rival(dinero, emocion_rival),
            )
            # Actualizar la mejor emoción total y la mejor asignación de dinero
            if emocion_total > mejor_emocion_total:
                mejor_emocion_total = emocion_total
                mejor_dinero_asignado = dinero

    return mejor_dinero_asignado


# Condiciones iniciales
cantidad_total_dinero = 10  # La suma total de dinero a repartir
emocion_propia = 0.7  # Emoción propia del jugador
emocion_rival = 1.6  # Emoción del rival

# Encontrar la solución óptima
dinero_optimo = encontrar_solucion_optima(
    emocion_propia, emocion_rival, cantidad_total_dinero
)

# Imprimir la solución óptima
print("Dinero óptimo a repartir:", dinero_optimo)
print("Emoción propia:", calcular_emocion_propia(dinero_optimo, emocion_propia))
print("Emoción del rival:", calcular_emocion_rival(dinero_optimo, emocion_rival))
