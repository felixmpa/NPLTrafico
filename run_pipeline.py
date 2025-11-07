from ETL.analizer_npl import main as run_analizer
def main():
    print("\n" + "=" * 50)
    print("Transporte: Optimización del Tráfico y la Logística en Tiempo Real")
    print("=" * 50)

    while True:
        print("\n=== MENÚ PRINCIPAL ===")
        print("1. Ejecutar ETL")
        print("0. Salir")

        choice = input("\nSelecciona una opción: ")

        if choice == "1":
            print("\nEjecutando analizador...\n")
            run_analizer()
        elif choice == "0":
            print("\n¡Hasta luego!")
            break
        else:
            print("\nOpción inválida. Por favor intenta de nuevo.")


if __name__ == "__main__":
    main()
