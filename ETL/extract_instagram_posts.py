"""
=============================================
📸 Instagram Post Extractor (Instaloader v4.14)
=============================================

Este script descarga publicaciones de una cuenta pública o privada (si tienes acceso)
usando Instaloader y las guarda en formato CSV con metadatos útiles.

Ahora soporta reanudar descargas sin duplicar publicaciones.

Requisitos:
    - Python 3.12+
    - Instaloader 4.14: pip install instaloader
    - Pandas (para manejar CSV incremental): pip install pandas

Importante:
    Usa cookies manuales para evitar errores 401 Unauthorized.
"""

import instaloader
from itertools import islice
from datetime import datetime
import csv
import os
import pandas as pd

# =============================
# 🔧 CONFIGURACIÓN
# =============================
USERNAME = "elcheposord"        # ⚠️ Tu usuario de Instagram
TARGET = "accidentes_rd"
LIMIT = 350                      # Número máximo de publicaciones a intentar extraer (puedes subirlo)
OUTPUT_FILE = "instagram_posts.csv"

# =============================
# 🔐 SESIÓN MANUAL (CON COOKIES)
# =============================
# Copia tus cookies desde tu navegador:
# En Chrome/Edge/Brave → F12 → Application → Storage → Cookies → https://www.instagram.com
cookies = {
    "csrftoken": "XnwUJJa5qul1BhPbpJz07tf6h5Yb7OvC",
    "sessionid": "78325552069%3ARklJ5VMZUF5ubo%3A29%3AAYiOsWhS6JNaHyJA53vozpmYf6bnp1JzW8-OD9yj1A",
    "ds_user_id": "78325552069",
    "mid": "Z_SknQAEAAHtx-0Ur_HMYQpptiZc",
    "ig_did": "9294C868-E4E3-41C5-BC29-9AE569AA9CBE"
}

# =============================
# 🚀 INICIALIZAR INSTALOADER
# =============================
L = instaloader.Instaloader()

try:
    L.load_session(USERNAME, cookies)
    print(f"✅ Sesión manual cargada correctamente para '{USERNAME}'")
    print(f"👤 Usuario autenticado: {L.test_login()}")
except Exception as e:
    print(f"❌ Error al cargar la sesión manual: {e}")
    exit()

# =============================
# 📂 CARGAR POSTS EXISTENTES (si hay)
# =============================
existing_shortcodes = set()
if os.path.exists(OUTPUT_FILE):
    df_existing = pd.read_csv(OUTPUT_FILE)
    existing_shortcodes = set(df_existing["id"].tolist())
    print(f"🧩 Se encontraron {len(existing_shortcodes)} publicaciones ya guardadas.")
else:
    df_existing = pd.DataFrame()

# =============================
# 📥 DESCARGAR PUBLICACIONES NUEVAS
# =============================
try:
    profile = instaloader.Profile.from_username(L.context, TARGET)
    print(f"\n📸 Descargando nuevas publicaciones de '{TARGET}' (hasta {LIMIT} máximo)...\n")

    new_posts = []

    for post in islice(profile.get_posts(), LIMIT):
        if post.shortcode in existing_shortcodes:
            print(f"⏩ Post duplicado, saltando: {post.shortcode}")
            continue

        data = {
            "id": post.shortcode,
            "text": post.caption or "",
            "timestamp": post.date_utc,
            "user": post.owner_username,
            "platform": "instagram",
            "likes": post.likes,
            "comments_count": post.comments,
            "video_views": post.video_view_count if post.is_video else 0,
            "is_video": post.is_video,
            "image_url": post.url,
            "post_url": f"https://instagram.com/p/{post.shortcode}",
            "account_followers": post.owner_profile.followers,
            "account_verified": post.owner_profile.is_verified,
            "year": post.date_utc.year,
            "month": post.date_utc.month,
            "day": post.date_utc.day,
            "hour": post.date_utc.hour,
            "day_of_week": post.date_utc.strftime("%A"),
            "is_weekend": post.date_utc.weekday() >= 5,
            "hashtags": ", ".join(post.caption_hashtags or []),
            "mentions": ", ".join(post.caption_mentions or []),
        }

        new_posts.append(data)
        print(f"✅ Nuevo post guardado: {data['post_url']}")

    # =============================
    # 💾 GUARDAR RESULTADOS
    # =============================
    if new_posts:
        df_new = pd.DataFrame(new_posts)

        if not df_existing.empty:
            df_combined = pd.concat([df_existing, df_new], ignore_index=True)
        else:
            df_combined = df_new

        df_combined.to_csv(OUTPUT_FILE, index=False, encoding="utf-8")
        print(f"\n💾 Datos actualizados correctamente en '{OUTPUT_FILE}'")
        print(f"📊 Total acumulado: {len(df_combined)} publicaciones")
        print(f"🆕 Nuevas publicaciones agregadas: {len(df_new)}")
    else:
        print("⚠️ No se encontraron publicaciones nuevas para agregar.")

# =============================
# ❌ MANEJO DE ERRORES
# =============================
except instaloader.exceptions.ConnectionException as e:
    print(f"❌ Error de conexión o autenticación: {e}")
except instaloader.exceptions.ProfileNotExistsException:
    print(f"❌ El perfil '{TARGET}' no existe o no es accesible.")
except Exception as e:
    print(f"⚠️ Error inesperado: {e}")
