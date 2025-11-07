import pandas as pd
import re
from datetime import datetime
from collections import Counter


class AnalizerNLP:
    def __init__(self):
        self.ubicaciones_conocidas = [
            'george washington', 'máximo gómez', 'máximo gomez', 'winston churchill',
            'abraham lincoln', 'john f kennedy', 'charles de gaulle', '27 de febrero',
            'duarte', 'mella', 'sánchez', 'luperón', 'núñez de cáceres',
            'santo domingo este', 'distrito nacional', 'san isidro',
            'la barranquita', 'los mina', 'villa mella', 'pantoja',
            'las américas', 'ecológica', 'charles summer', 'los próceres',
            'juan pablo duarte', 'isabel aguiar', 'república de colombia',
            'circunvalación', 'olímpica', 'independencia', 'san vicente de paul'
        ]

    def extraer_ubicaciones(self, texto):
        """Extrae todas las ubicaciones mencionadas en el texto"""
        if pd.isna(texto):
            return []

        texto_lower = texto.lower()
        ubicaciones = []

        # Patrones de ubicaciones
        patrones = [
            r'avenida?\s+([^,.\n]+?)(?=\s*[,.\n]|próximo|cerca|kilómetro|$)',
            r'av\.?\s+([^,.\n]+?)(?=\s*[,.\n]|próximo|cerca|kilómetro|$)',
            r'autopista\s+([^,.\n]+?)(?=\s*[,.\n]|kilómetro|rampa|$)',
            r'calle\s+([^,.\n]+?)(?=\s*[,.\n]|esquina|$)',
            r'puente\s+([^,.\n]+?)(?=\s*[,.\n]|rampa|$)',
            r'circunvalación\s+([^,.\n]+?)(?=\s*[,.\n]|$)',
            r'paso a desnivel\s+(?:de\s+)?(?:la\s+)?([^,.\n]+?)(?=\s*[,.\n]|$)',
        ]

        for patron in patrones:
            matches = re.finditer(patron, texto_lower, re.IGNORECASE)
            for match in matches:
                ubicacion = match.group(0).strip()
                ubicacion = re.sub(r'\s+', ' ', ubicacion)
                ubicaciones.append(ubicacion.title())

        # Kilómetros
        km_match = re.search(r'kilómetro\s+(\d+)', texto_lower)
        if km_match:
            ubicaciones.append(f"Km {km_match.group(1)}")

        # Lugares conocidos
        for lugar in self.ubicaciones_conocidas:
            if lugar in texto_lower:
                ubicaciones.append(lugar.title())

        return list(set(ubicaciones))

    def clasificar_tipo_incidente(self, texto):
        """Clasifica el tipo de incidente"""
        if pd.isna(texto):
            return "No clasificado"

        texto_lower = texto.lower()

        categorias = {
            'Accidente vehicular': [
                'accidente', 'choque', 'colisión', 'volcado', 'impacto',
                'descarrilado', 'estrellado'
            ],
            'Incendio vehicular': [
                'incendio', 'incendiado', 'fuego', 'llamas', 'quemado'
            ],
            'Cierre vial': [
                'cierre', 'cerrado', 'bloqueado', 'restringido', 'prohibido',
                'suspendido', 'clausurado'
            ],
            'Alerta meteorológica': [
                'huracán', 'tormenta', 'lluvia', 'inundación',
                'viento', 'clima', 'meteorológica', 'climático'
            ],
            'Medidas de tránsito': [
                'tránsito', 'movilidad', 'velocidad', 'mejora', 'restricción',
                'giro a la izquierda'
            ],
            'Evento/Anuncio': [
                'premio', 'festival', 'lanzó', 'reconocimiento', 'postulaciones',
                'evento'
            ]
        }

        coincidencias = {}
        for categoria, palabras in categorias.items():
            count = sum(1 for palabra in palabras if palabra in texto_lower)
            if count > 0:
                coincidencias[categoria] = count

        if coincidencias:
            return max(coincidencias, key=coincidencias.get)

        return "Otro"

    def calcular_severidad(self, texto, likes=0, comments=0, views=0):
        """Calcula la severidad del incidente"""
        if pd.isna(texto):
            return "Baja"

        texto_lower = texto.lower()
        score = 0

        # Palabras de alta severidad
        alta_severidad = [
            'fallecido', 'muerto', 'muerte', 'fatal', 'grave',
            'herido grave', 'heridos', 'víctima', 'ambulancia',
            'hospital', 'bomberos', 'rescate', 'emergencia'
        ]

        # Palabras de severidad media
        media_severidad = [
            'accidente', 'choque', 'incendio', 'volcado',
            'colisión', 'impacto', 'daños', 'afectado'
        ]

        # Indicadores de urgencia
        urgencia = ['urgente', 'importante', 'alerta', '🚨', 'cuidado', 'peligro']

        # Calcular score
        for palabra in alta_severidad:
            if palabra in texto_lower:
                score += 3

        for palabra in media_severidad:
            if palabra in texto_lower:
                score += 1

        for palabra in urgencia:
            if palabra in texto_lower:
                score += 0.5

        # Factores de engagement
        if likes > 1000:
            score += 2
        elif likes > 500:
            score += 1

        if comments > 100:
            score += 1.5
        elif comments > 50:
            score += 0.5

        if views > 30000:
            score += 2
        elif views > 15000:
            score += 1

        # Clasificación final
        if score >= 6:
            return "Alta"
        elif score >= 3:
            return "Media"
        else:
            return "Baja"

    def clasificar_horario(self, hora):
        """Clasifica la franja horaria"""
        if pd.isna(hora):
            return "No especificado"

        if 5 <= hora < 9:
            return "Mañana temprano (5am-9am)"
        elif 9 <= hora < 12:
            return "Media mañana (9am-12pm)"
        elif 12 <= hora < 15:
            return "Mediodía (12pm-3pm)"
        elif 15 <= hora < 18:
            return "Tarde (3pm-6pm)"
        elif 18 <= hora < 21:
            return "Noche temprano (6pm-9pm)"
        elif 21 <= hora < 24:
            return "Noche (9pm-12am)"
        else:
            return "Madrugada (12am-5am)"

    def es_horario_critico(self, timestamp):
        """Determina si el horario es crítico (alta incidencia en RD)"""
        if isinstance(timestamp, str):
            timestamp = pd.to_datetime(timestamp)

        hora = timestamp.hour
        dia = timestamp.strftime('%A')

        # Horarios críticos en RD
        horario_critico = (
                6 <= hora < 9 or
                12 <= hora < 14 or
                16 <= hora < 20 or
                (22 <= hora or hora < 1)
        )

        dias_criticos = ['Monday', 'Friday', 'Saturday', 'Sunday']
        dia_critico = dia in dias_criticos

        return horario_critico or dia_critico

    def analizar_post(self, texto, timestamp=None, likes=0, comments=0, views=0):
        """
        Análisis completo de un post

        Args:
            texto (str): Texto del post
            timestamp (datetime): Fecha y hora del post
            likes (int): Cantidad de likes
            comments (int): Cantidad de comentarios
            views (int): Vistas (si es video)

        Returns:
            dict: Diccionario con todos los análisis
        """
        if timestamp is None:
            timestamp = datetime.now()
        elif isinstance(timestamp, str):
            timestamp = pd.to_datetime(timestamp)

        resultado = {
            'locations': self.extraer_ubicaciones(texto),
            'incident_type': self.clasificar_tipo_incidente(texto),
            'severity': self.calcular_severidad(texto, likes, comments, views),
            'time_slot': self.clasificar_horario(timestamp.hour),
            'critical_time': self.es_horario_critico(timestamp),
            'alert_required': False
        }

        # Determinar si requiere alerta
        if (resultado['severity'] == 'Alta' or
                (not pd.isna(texto) and any(palabra in texto.lower() for palabra in ['fallecido', 'heridos', 'grave']))):
            resultado['alert_required'] = True

        return resultado

    def analizar_dataset(self, df, columna_texto='text', columna_timestamp='timestamp',
                         columna_likes='likes', columna_comments='comments_count',
                         columna_views='video_views'):
        """
        Analiza un dataset completo de posts

        Args:
            df (DataFrame): Dataset con los posts
            columna_texto (str): Nombre de la columna con el texto
            columna_timestamp (str): Nombre de la columna con timestamp
            columna_likes (str): Nombre de la columna con likes
            columna_comments (str): Nombre de la columna con comentarios
            columna_views (str): Nombre de la columna con vistas

        Returns:
            DataFrame: Dataset enriquecido con análisis NLP
        """
        df = df.copy()

        # Convertir timestamp
        df[columna_timestamp] = pd.to_datetime(df[columna_timestamp])

        # Aplicar análisis
        resultados = []
        for idx, row in df.iterrows():
            resultado = self.analizar_post(
                texto=row[columna_texto],
                timestamp=row[columna_timestamp],
                likes=row.get(columna_likes, 0),
                comments=row.get(columna_comments, 0),
                views=row.get(columna_views, 0) if not pd.isna(row.get(columna_views, 0)) else 0
            )
            resultados.append(resultado)

        # Agregar columnas al dataframe
        df['extracted_locations'] = [r['locations'] for r in resultados]
        df['incident_type'] = [r['incident_type'] for r in resultados]
        df['severity'] = [r['severity'] for r in resultados]
        df['time_slot'] = [r['time_slot'] for r in resultados]
        df['critical_time'] = [r['critical_time'] for r in resultados]
        df['alert_required'] = [r['alert_required'] for r in resultados]

        return df

    def generar_reporte(self, df):
        """Genera un reporte resumido del análisis"""
        reporte = {
            'total_posts': len(df),
            'incident_type': df['incident_type'].value_counts().to_dict(),
            'severity': df['severity'].value_counts().to_dict(),
            'time_slots': df['time_slot'].value_counts().to_dict(),
            'posts_require_alert': df['alert_required'].sum(),
            'top_locations': self._contar_ubicaciones(df)
        }
        return reporte

    def _contar_ubicaciones(self, df):
        """Cuenta las ubicaciones más frecuentes"""
        ubicaciones_todas = []
        for ubicaciones in df['extracted_locations'].dropna():
            if isinstance(ubicaciones, list):
                ubicaciones_todas.extend(ubicaciones)

        ubicaciones_freq = Counter(ubicaciones_todas)
        return dict(ubicaciones_freq.most_common(10))


# ============================================================================
# EJEMPLO DE USO
# ============================================================================

def main():
    # Inicializar analizador
    analizador = AnalizerNLP()

    print("=" * 80)
    print("ANALIZADOR NLP DE POSTS - EJEMPLO DE USO")
    print("=" * 80)

    # Ejemplo 1: Analizar un solo post
    print("\n1. ANÁLISIS DE UN POST INDIVIDUAL:")
    print("-" * 80)

    texto_ejemplo = """
    Accidente grave registrado en la avenida Juan Pablo Duarte, kilómetro 13.
    Hay varios heridos y se solicitó apoyo de ambulancias.
    """

    resultado = analizador.analizar_post(
        texto=texto_ejemplo,
        timestamp="2025-11-07 21:30:00",
        likes=450,
        comments=35,
        views=5000
    )

    print(f"Texto: {texto_ejemplo.strip()}")
    print(f"\nResultados del análisis:")
    for clave, valor in resultado.items():
        print(f"  {clave}: {valor}")

    # Ejemplo 2: Analizar dataset completo
    print("\n\n2. ANÁLISIS DE DATASET COMPLETO:")
    print("-" * 80)

    # Cargar dataset
    df = pd.read_csv('instagram_posts.csv')
    print(f"Posts en el dataset: {len(df)}")

    # Analizar
    df_enriquecido = analizador.analizar_dataset(df)

    # Generar reporte
    reporte = analizador.generar_reporte(df_enriquecido)

    print("\nReporte generado:")
    print(f"  Total de posts: {reporte['total_posts']}")
    print(f"  Posts que requieren alerta: {reporte['posts_require_alert']}")
    print(f"\n  Top 5 ubicaciones:")
    for ubicacion, count in list(reporte['top_locations'].items())[:5]:
        print(f"    - {ubicacion}: {count}")

    # Guardar dataset enriquecido
    output_path = 'accidents.csv'
    df_enriquecido['extracted_locations'] = df_enriquecido['extracted_locations'].apply(
        lambda x: ', '.join(x) if isinstance(x, list) else ''
    )
    df_enriquecido.to_csv(output_path, index=False)
    print(f"\n✓ Dataset guardado en: {output_path}")

    print("\n" + "=" * 80)
    print("ANÁLISIS COMPLETADO")
    print("=" * 80)