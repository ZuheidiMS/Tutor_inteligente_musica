from database.mongodb import MongoDB
from database.dashboard_repository import DashboardRepository


def main():
    print("=" * 70)
    print("PRUEBA DEL DASHBOARD")
    print("=" * 70)

    mongo = MongoDB()
    db = mongo.conectar()

    if db is None:
        print("No fue posible conectar con MongoDB.")
        return

    dashboard = DashboardRepository(db)

    print("\n--- INDICADORES ---")
    indicadores = dashboard.obtener_indicadores()

    for nombre, valor in indicadores.items():
        print(f"{nombre}: {valor}")

    print("\n--- INCIDENTES POR CATEGORÍA ---")
    categorias = dashboard.incidentes_por_categoria()

    if categorias:
        for resultado in categorias:
            print(
                f"{resultado['categoria']}: "
                f"{resultado['total']}"
            )
    else:
        print("No hay incidentes registrados.")

    print("\n--- INCIDENTES POR SEMANA ---")
    semanas = dashboard.incidentes_por_semana()

    if semanas:
        for resultado in semanas:
            print(
                f"Año {resultado['anio']}, "
                f"semana {resultado['semana']}: "
                f"{resultado['total']} incidentes"
            )
    else:
        print("No hay incidentes con timestamp.")

    print("\n--- EVALUACIONES POR MODELO ---")
    modelos = dashboard.evaluaciones_por_modelo()

    if modelos:
        for resultado in modelos:
            print(
                f"{resultado['modelo']}: "
                f"{resultado['total']}"
            )
    else:
        print("No hay evaluaciones registradas.")

    mongo.cerrar()

    print("\n" + "=" * 70)
    print("PRUEBA DEL DASHBOARD FINALIZADA")
    print("=" * 70)


if __name__ == "__main__":
    main()