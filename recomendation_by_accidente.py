import pandas as pd
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

# === FUNCIÓN PARA RECOMENDAR POR ACCIDENTE ===
def recomendar_por_accidente():
    # 1️⃣ Seleccionar un accidente aleatorio con ubicación válida
    accidentes_validos = accidents[
        accidents["extracted_locations"].notna() & 
        accidents["extracted_locations"].apply(lambda x: isinstance(x, str) and len(x.strip()) > 0)
    ]
    
    if accidentes_validos.empty:
        return "No hay accidentes con ubicaciones válidas disponibles."
    
    accidente_seleccionado = accidentes_validos.sample(1).iloc[0]
    ubicacion_accidente = accidente_seleccionado["extracted_locations"]
    
    print(f"🚨 ACCIDENTE SELECCIONADO:")
    print(f"Tipo: {accidente_seleccionado['incident_type']}")
    print(f"Ubicación: {ubicacion_accidente}")
    print(f"Texto: {accidente_seleccionado['text'][:100]}...")
    print("\n" + "="*80)
    
    # 2️⃣ Encontrar usuarios afectados por sus rutas frecuentes
    usuarios_afectados = []
    
    for _, user in users.iterrows():
        rutas_usuario = user["frequent_routes"]
        if isinstance(rutas_usuario, list):
            # Verificar si alguna ruta del usuario está relacionada con la ubicación del accidente
            for ruta in rutas_usuario:
                if isinstance(ruta, str) and ruta.lower() in ubicacion_accidente.lower():
                    usuarios_afectados.append(user)
                    break
    
    if not usuarios_afectados:
        print("❌ No se encontraron usuarios afectados por este accidente.")
        return
    
    print(f"👥 USUARIOS AFECTADOS: {len(usuarios_afectados)}")
    print("\n" + "="*80)
    
    # 3️⃣ Generar recomendaciones para cada usuario afectado
    for user in usuarios_afectados:
        print(f"\n🔔 Recomendación para usuario: {user['user_id']}")
        print(f"Nombre: {user['name']}")
        print(f"Zona Residencial: {user['residential_zone']}")
        print(f"Zona de Trabajo: {user['work_zone']}")
        print(f"Interes: {user["interests"]} - Rutas: {user["frequent_routes"]} \n\n")

        mensaje = f"🚧 ALERTA: Se reporta un {accidente_seleccionado['incident_type'].lower()} en {ubicacion_accidente}. "
        mensaje += "Se recomienda evitar esta ruta.\n"
        
        # Buscar POI alternativo basado en intereses y zonas del usuario
        zona_residencia = user["residential_zone"]
        zona_trabajo = user["work_zone"]
        intereses = user["interests"]
        
        print(f"🔍 Buscando POI para zonas: {zona_residencia}, {zona_trabajo}")
        print(f"🎯 Intereses del usuario: {intereses}")
        
        # Buscar POI en zonas del usuario con intereses similares
        def has_matching_interests(poi_interests):
            if not isinstance(poi_interests, list) or not isinstance(intereses, list):
                return False
            return any(i in poi_interests for i in intereses)
        
        poi_candidates = points[
            (points["zone"].isin([zona_trabajo, zona_residencia])) &
            (points["related_interests"].apply(has_matching_interests))
        ]
        
        print(f"📍 POIs con intereses similares encontrados: {len(poi_candidates)}")
        
        if poi_candidates.empty:
            # Si no hay POI con intereses similares, buscar cualquier POI en las zonas
            poi_candidates = points[points["zone"].isin([zona_trabajo, zona_residencia])]
            print(f"📍 POIs en zonas del usuario (sin filtro de intereses): {len(poi_candidates)}")
            
        if poi_candidates.empty:
            # Como último recurso, seleccionar cualquier POI
            poi = points.sample(1).iloc[0]
            print("⚠️ Usando POI aleatorio (último recurso)")
        else:
            poi = poi_candidates.sample(1).iloc[0]
            print(f"✅ POI seleccionado: {poi['name']} - Intereses: {poi['related_interests']}")
        
        mensaje += f"🧭 Te sugerimos visitar **{poi['name']}** ({poi['type']}) en {poi['zone']}. "
        mensaje += f"💡 Oferta actual: {poi['current_offer']}."
        
        print(mensaje)
        print("-" * 60)

# === EJECUTAR RECOMENDACIÓN ===
if __name__ == "__main__":
    recomendar_por_accidente()