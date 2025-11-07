from ETL.analizer_npl import main as run_analizer

def run_npl():
    print("\nEjecutando analizador NPL...")
    try:
        run_analizer()
        print("Analizador NPL completado exitosamente")
        return True
    except Exception as e:
        print(f"Error en analizador NPL: {e}")
        return False

def run_synthetic():
    print("\nGenerando Data...")
    try:
        run_analizer()
        print("data generada exitosamente")
        return True
    except Exception as e:
        print(f"Error en generar data: {e}")
        return False


def main():
    """Método principal con menú interactivo."""
    print("\n" + "=" * 50)
    print("Transporte: Optimización del Tráfico y la Logística en Tiempo Real")
    print("=" * 50)

    while True:
        print("\n=== MENÚ PRINCIPAL ===")
        print("1. Ejecutar Análisis NPL")
        print("2. Generar Data de Usuario y Puntos de Interes")
        print("0. Salir")

        choice = input("\nSelecciona una opción: ")

        if choice == "1":
            run_npl()
        if choice == "2":
                run_synthetic()
        elif choice == "0":
            print("\n¡Hasta luego!")
            break
        else:
            print("\nOpción inválida. Por favor intenta de nuevo.")


if __name__ == "__main__":
    main()