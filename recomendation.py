import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import ast
import random

# === CARGAR DATOS ===
users = pd.read_csv("ETL/users.csv")
accidents = pd.read_csv("ETL/accidents.csv")
points = pd.read_csv("ETL/points_of_interest.csv")

# === LIMPIEZA Y PARSEO DE LISTAS ===
def parse_list(x):
    try:
        return ast.literal_eval(x)
    except:
        return []

for df, cols in [
    (users, ["interests", "frequent_routes"]),
    (points, ["related_interests", "nearby_routes"]),
]:
    for c in cols:
        df[c] = df[c].apply(parse_list)

# === FUNCIÓN PRINCIPAL DE RECOMENDACIÓN ===
def recomendar_para_usuario(user_id):
    # Buscar usuario
    user = users.loc[users["user_id"] == user_id].iloc[0]

    zona_residencia = user["residential_zone"]
    zona_trabajo = user["work_zone"]
    intereses = user["interests"]
    rutas = user["frequent_routes"]

    # 1️⃣ Buscar accidentes que afecten sus rutas o zonas
    accidentes_relevantes = accidents[
        accidents["extracted_locations"].notna() &
        accidents["extracted_locations"].apply(lambda x: isinstance(x, str) and any(ruta.lower() in x.lower() for ruta in rutas))
    ]

    # 2️⃣ Si hay accidentes relevantes → alerta + recomendación
    if not accidentes_relevantes.empty:
        accidente = accidentes_relevantes.iloc[0]
        mensaje =  f"Recomendación para usuario: {user_id} \n"
        mensaje += f"zona_trabajo es: {zona_trabajo} y zona_residencia es: {zona_residencia} \n\n"
        mensaje += f"interes: {intereses} - rutas: {rutas} \n\n"
        mensaje += f"🚧 Se reporta un {accidente['incident_type'].lower()} en {accidente['extracted_locations']}. "
        mensaje += "Evita esa ruta.\n"

        # Buscar POI alternativo en zona de trabajo o residencia con intereses similares
        poi_candidates = points[
            (points["zone"].isin([zona_trabajo, zona_residencia])) &
            (points["related_interests"].apply(lambda lst: any(i in lst for i in intereses)))
        ]

        if poi_candidates.empty:
            poi = points.sample(1).iloc[0]
        else:
            poi = poi_candidates.sample(1).iloc[0]

        mensaje += f"🧭 Te sugerimos visitar **{poi['name']}** ({poi['type']}) en {poi['zone']}. "
        mensaje += f"💡 {poi['current_offer']}."
        return mensaje

    # 3️⃣ Si no hay accidentes → recomendación positiva
    else:
        poi_candidates = points[
            (points["zone"].isin([zona_trabajo, zona_residencia])) &
            (points["related_interests"].apply(lambda lst: any(i in lst for i in intereses)))
        ]
        if poi_candidates.empty:
            poi = points.sample(1).iloc[0]
        else:
            poi = poi_candidates.sample(1).iloc[0]

        mensaje = f"✅ No hay incidentes en tus rutas hoy. "
        mensaje += f"Te recomendamos **{poi['name']}** ({poi['type']}) en {poi['zone']}. "
        mensaje += f"Oferta actual: {poi['current_offer']}."
        return mensaje


# === EJEMPLO DE USO ===
for uid in ["U001", "U004", "U005"]:
    print("\n" + "="*60)
    print(recomendar_para_usuario(uid))
