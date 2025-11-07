import pandas as pd
import random
from pathlib import Path

# ==========================================================
# CONFIG
# ==========================================================
N_USERS = 80
N_POIS = 40

USER_INTERESTS_POOL = [
    "deportes", "salud", "películas", "arte", "dieta", "tecnología", "videojuegos",
    "negocios", "viajes", "gastronomía", "fotografía", "moda",
    "entretenimiento", "lectura", "hobbies"
]

# These will be populated from accidents data
ZONES_RESIDENTIAL = []
ZONES_WORK = []

# POI types mapped to related interests for better matching
POI_INTEREST_MAPPING = {
    "Gimnasio": ["deportes", "salud", "dieta"],
    "Cine": ["películas", "entretenimiento"],
    "Restaurante": ["gastronomía", "entretenimiento"],
    "Centro Comercial": ["moda", "entretenimiento"],
    "Centro Cultural": ["arte", "entretenimiento", "lectura"],
    "Cafetería": ["gastronomía", "negocios", "lectura"],
    "Tienda": ["moda", "entretenimiento"],
    "Spa": ["salud", "dieta"],
    "Parque": ["deportes", "salud", "fotografía"],
    "Museo": ["arte", "entretenimiento", "lectura"]
}

POI_TYPES = list(POI_INTEREST_MAPPING.keys())

# ==========================================================
# 1. READ ACCIDENTS AND EXTRACT LOCATIONS
# ==========================================================
accidents_path = Path("accidents.csv")
if not accidents_path.exists():
    raise FileNotFoundError("❌ File 'accidents.csv' not found in current directory.")

accidents = pd.read_csv(accidents_path)

def extract_clean_locations(value):
    """Extract multiple locations separated by comma or semicolon."""
    if pd.isna(value):
        return []
    value = str(value)
    for sep in [",", ";", "|"]:
        if sep in value:
            return [v.strip() for v in value.split(sep) if v.strip()]
    return [value.strip()]

# Gather all location mentions
all_locations = []
accidents["extracted_locations"].dropna().apply(
    lambda locs: all_locations.extend(extract_clean_locations(locs))
)

popular_routes = pd.Series(all_locations).value_counts().head(10).index.tolist()

# Use the most popular accident locations as residential and work zones
all_accident_locations = pd.Series(all_locations).value_counts()
ZONES_RESIDENTIAL = all_accident_locations.head(15).index.tolist()
ZONES_WORK = all_accident_locations.head(12).index.tolist()

print("\n📍 Main routes detected from accidents.csv:")
for i, route in enumerate(popular_routes, 1):
    print(f"  {i}. {route}")

print(f"\n🏠 Residential zones from accidents: {len(ZONES_RESIDENTIAL)} zones")
print(f"🏢 Work zones from accidents: {len(ZONES_WORK)} zones")

# ==========================================================
# 2. GENERATE SYNTHETIC USERS
# ==========================================================
users = []
for i in range(1, N_USERS + 1):
    name = f"Usuario {i:03d}"
    residential_zone = random.choice(ZONES_RESIDENTIAL)
    work_zone = random.choice(ZONES_WORK)
    interests = random.sample(USER_INTERESTS_POOL, k=3)
    
    # Generate routes strictly limited to residential and work zones
    candidate_routes = [residential_zone, work_zone]
    
    # Remove duplicates if residential and work zones are the same
    candidate_routes = list(set(candidate_routes))
    
    # Select routes only from residential and work zones (1-2 routes max)
    num_routes = min(random.randint(1, 2), len(candidate_routes))
    routes = random.sample(candidate_routes, k=num_routes)

    users.append({
        "user_id": f"U{i:03d}",
        "name": name,
        "residential_zone": residential_zone,
        "work_zone": work_zone,
        "interests": str(interests),
        "frequent_routes": str(routes),
    })

users_df = pd.DataFrame(users)
users_df.to_csv("users.csv", index=False, encoding="utf-8-sig")
print(f"\n✅ File generated: users.csv ({len(users_df)} rows)")

# ==========================================================
# 3. GENERATE SYNTHETIC POINTS OF INTEREST
# ==========================================================
pois = []
for i in range(1, N_POIS + 1):
    poi_type = random.choice(POI_TYPES)
    route = random.choice(popular_routes)
    # Use the same zones from accidents data for consistency
    zone = random.choice(ZONES_RESIDENTIAL)  
    
    # Use mapped interests for this POI type with some randomness
    poi_mapped_interests = POI_INTEREST_MAPPING[poi_type]
    related_interests = random.sample(poi_mapped_interests, k=min(2, len(poi_mapped_interests)))
    
    # Add one random interest occasionally for variety (30% chance)
    if random.random() < 0.3:
        additional_interest = random.choice([i for i in USER_INTERESTS_POOL if i not in related_interests])
        related_interests = related_interests[:1] + [additional_interest]
    
    start_hour = random.randint(6, 10)
    end_hour = random.randint(18, 22)
    if start_hour >= end_hour:
        end_hour = start_hour + random.randint(8, 12)

    poi = {
        "poi_id": f"P{i:03d}",
        "name": f"{poi_type} {route}",
        "type": poi_type,
        "zone": zone,
        "related_interests": str(related_interests),
        "nearby_routes": str([route]),
        "schedule": f"{start_hour}:00-{end_hour}:00",
        "current_offer": random.choice([
            "2x1 en servicios", "10% de descuento", "Clase gratuita", "Nuevo menú", "Promoción del día"
        ]),
        "description": f"{poi_type} ubicado cerca de {route}, popular entre personas interesadas en {related_interests[0]} y {related_interests[1]}."
    }
    pois.append(poi)

pois_df = pd.DataFrame(pois)
pois_df.to_csv("points_of_interest.csv", index=False, encoding="utf-8-sig")
print(f"✅ File generated: points_of_interest.csv ({len(pois_df)} rows)")

# ==========================================================
# 4. SUMMARY
# ==========================================================
print("\n📊 SUMMARY:")
print(f"  Users generated: {len(users_df)}")
print(f"  POIs generated:  {len(pois_df)}")

print("\n👤 Example user:")
print(users_df.head(1).to_string(index=False))

print("\n📍 Example POI:")
print(pois_df.head(1).to_string(index=False))
