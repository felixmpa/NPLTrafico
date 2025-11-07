import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import ast
import random
import os

# === FUNCIONES AUXILIARES ===
def parse_list(x):
    try:
        return ast.literal_eval(x)
    except:
        return []

def recomendar_para_usuario(user_id, users, points):
    # Encontrar usuario
    user = users[users["user_id"] == user_id]
    if user.empty:
        return f"❌ Usuario {user_id} no encontrado."
    
    user = user.iloc[0]
    intereses_usuario = user["interests"]
    zonas_usuario = user["frequent_routes"]
    
    # Crear corpus de texto para TF-IDF
    user_text = " ".join(intereses_usuario)
    poi_texts = []
    
    for _, poi in points.iterrows():
        poi_text = " ".join(poi["related_interests"]) + " " + poi["type"].lower()
        poi_texts.append(poi_text)
    
    # Aplicar TF-IDF
    vectorizer = TfidfVectorizer(stop_words=None)
    
    # Crear matriz con texto del usuario + textos de POIs
    all_texts = [user_text] + poi_texts
    tfidf_matrix = vectorizer.fit_transform(all_texts)
    
    # Calcular similitudes
    similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()
    
    # Ordenar POIs por similitud
    poi_similarities = list(zip(points.index, similarities))
    poi_similarities.sort(key=lambda x: x[1], reverse=True)
    
    # Filtrar por zonas si es posible
    filtered_pois = []
    for poi_idx, similarity in poi_similarities:
        poi = points.iloc[poi_idx]
        poi_routes = poi["nearby_routes"]
        
        # Verificar si hay intersección entre rutas del usuario y del POI
        if any(route in zonas_usuario for route in poi_routes):
            filtered_pois.append((poi_idx, similarity))
    
    # Si no hay POIs en las zonas del usuario, usar todos
    if not filtered_pois:
        filtered_pois = poi_similarities
    
    # Tomar los top 3
    top_pois = filtered_pois[:3]
    
    mensaje = f"\n🎯 RECOMENDACIONES PARA {user['name']} (ID: {user_id})\n"
    mensaje += f"📍 Zonas frecuentes: {zonas_usuario}\n"
    mensaje += f"🎨 Intereses: {intereses_usuario}\n\n"
    
    for i, (poi_idx, similarity) in enumerate(top_pois, 1):
        poi = points.iloc[poi_idx]
        mensaje += f"{i}. 🏪 **{poi['name']}** ({poi['type']})\n"
        mensaje += f"   📍 Ubicación: {poi['zone']}\n"
        mensaje += f"   🎯 Similitud: {similarity:.3f}\n"
        mensaje += f"   🎨 Intereses relacionados: {poi['related_interests']}\n"
        mensaje += f"   💡 Oferta: {poi['current_offer']}\n"
        mensaje += f"   ⏰ Horario: {poi['schedule']}\n\n"
    
    return mensaje

def run():
    """Main function to run the recommendation system."""
    print("\n" + "=" * 80)
    print("🚀 SISTEMA DE RECOMENDACIONES PERSONALIZADO")
    print("=" * 80)
    
    # === CARGAR DATOS ===
    users_path = os.path.join("ETL", "users.csv")
    accidents_path = os.path.join("ETL", "accidents.csv")
    points_path = os.path.join("ETL", "points_of_interest.csv")
    
    users = pd.read_csv(users_path)
    accidents = pd.read_csv(accidents_path)
    points = pd.read_csv(points_path)

    # === LIMPIEZA Y PARSEO DE LISTAS ===
    for df, cols in [
        (users, ["interests", "frequent_routes"]),
        (points, ["related_interests", "nearby_routes"]),
    ]:
        for c in cols:
            df[c] = df[c].apply(parse_list)

    # === EJEMPLO DE USO ===
    ejemplo_usuarios = ["U001", "U004", "U005"]
    
    for uid in ejemplo_usuarios:
        print("\n" + "="*60)
        resultado = recomendar_para_usuario(uid, users, points)
        print(resultado)
    
    print("\n" + "=" * 80)
    print("✅ RECOMENDACIONES COMPLETADAS")
    print("=" * 80)

def main():
    """Alias for run() function."""
    run()

if __name__ == "__main__":
    run()