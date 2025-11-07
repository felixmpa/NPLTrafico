from ETL.analizer_npl import main as run_analizer
from ETL.generate_synthetic_data import run as run_generator
from recomendation import run as run_recommendations
from recomendation_by_accidente import run as run_accident_recommendations

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
        run_generator()
        print("Data generada exitosamente")
        return True
    except Exception as e:
        print(f"Error en generar data: {e}")
        return False

def run_recommendation_system():
    print("\nEjecutando sistema de recomendaciones...")
    try:
        run_recommendations()
        print("Sistema de recomendaciones completado exitosamente")
        return True
    except Exception as e:
        print(f"Error en sistema de recomendaciones: {e}")
        return False

def run_accident_recommendation_system():
    print("\nEjecutando sistema de recomendaciones basado en accidentes...")
    try:
        run_accident_recommendations()
        print("Sistema de recomendaciones por accidente completado exitosamente")
        return True
    except Exception as e:
        print(f"Error en sistema de recomendaciones por accidente: {e}")
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
        print("3. Sistema de Recomendaciones Personalizado")
        print("4. Sistema de Recomendaciones por Accidentes")
        print("0. Salir")

        choice = input("\nSelecciona una opción: ")

        if choice == "1":
            run_npl()
        elif choice == "2":
            run_synthetic()
        elif choice == "3":
            run_recommendation_system()
        elif choice == "4":
            run_accident_recommendation_system()
        elif choice == "0":
            print("\n¡Hasta luego!")
            break
        else:
            print("\nOpción inválida. Por favor intenta de nuevo.")


if __name__ == "__main__":
    main()