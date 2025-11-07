import pandas as pd
import re
import os
import numpy as np
from datetime import datetime
from collections import Counter
from typing import List, Dict, Tuple

# NLP Libraries
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer
from nltk.chunk import ne_chunk
from nltk.tag import pos_tag

try:
    from transformers import pipeline, AutoTokenizer, AutoModel
    import torch
    BERT_AVAILABLE = True
    print("✅ BERT/Transformers disponible")
except ImportError:
    BERT_AVAILABLE = False
    print("⚠️ BERT/Transformers no disponible. Usando solo scikit-learn")

# Download required NLTK data (solo para stopwords y tokenización)
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('tokenizers/punkt_tab')
    nltk.data.find('corpora/stopwords')
except LookupError:
    print("📥 Descargando datos de NLTK necesarios...")
    nltk.download('punkt', quiet=True)
    nltk.download('punkt_tab', quiet=True)
    nltk.download('stopwords', quiet=True)

class AdvancedNLPAnalyzer:
    def __init__(self):
        print("🚀 Inicializando Analizador NLP Avanzado...")
        
        # Traditional location patterns (as fallback)
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
        
        # Initialize NLP components
        self.stemmer = SnowballStemmer('spanish')
        self.stop_words = set(stopwords.words('spanish'))
        
        # Add traffic-specific stop words
        self.stop_words.update(['accidente', 'tráfico', 'vehicular', 'reporte', 'reporta'])
        
        # Initialize BERT if available
        self.bert_model = None
        self.bert_tokenizer = None
        if BERT_AVAILABLE:
            try:
                print("📦 Cargando modelo BERT...")
                self.ner_pipeline = pipeline("ner", 
                                           model="mrm8488/bert-spanish-cased-finetuned-ner",
                                           aggregation_strategy="simple")
                print("✅ BERT NER cargado exitosamente")
            except Exception as e:
                print(f"⚠️ Error cargando BERT: {e}")
                self.ner_pipeline = None
        else:
            self.ner_pipeline = None
    
    def preprocess_text(self, texto: str) -> str:
        """Preprocesa el texto para análisis NLP"""
        if pd.isna(texto):
            return ""
        
        # Convert to lowercase
        texto = texto.lower()
        
        # Remove special characters but keep spaces and letters
        texto = re.sub(r'[^\w\s\-\.]', ' ', texto)
        
        # Normalize whitespace
        texto = re.sub(r'\s+', ' ', texto).strip()
        
        return texto
    
    def extract_entities_with_bert(self, texto: str) -> List[Dict]:
        """Extrae entidades usando BERT NER"""
        if not self.ner_pipeline or pd.isna(texto):
            return []
        
        try:
            entities = self.ner_pipeline(texto)
            location_entities = []
            
            for entity in entities:
                if entity['entity_group'] in ['LOC', 'MISC'] and entity['score'] > 0.8:
                    location_entities.append({
                        'text': entity['word'],
                        'label': entity['entity_group'],
                        'confidence': entity['score'],
                        'method': 'bert'
                    })
            
            return location_entities
        except Exception as e:
            print(f"Error en BERT NER: {e}")
            return []
    
    def extract_entities_with_nltk(self, texto: str) -> List[Dict]:
        """Extrae entidades usando NLTK (deshabilitado por problemas de dependencias)"""
        # NLTK NER deshabilitado temporalmente debido a problemas de recursos
        # Solo usamos BERT y regex para extracción de ubicaciones
        return []
    
    def extract_locations_regex(self, texto: str) -> List[str]:
        """Extrae ubicaciones usando patrones regex (método original mejorado)"""
        if pd.isna(texto):
            return []

        texto_lower = texto.lower()
        ubicaciones = []

        # Enhanced location patterns
        patrones = [
            r'(?:avenida?|av\.?)\s+([^,.\n]+?)(?=\s*[,.\n]|próximo|cerca|kilómetro|$)',
            r'autopista\s+([^,.\n]+?)(?=\s*[,.\n]|kilómetro|rampa|$)',
            r'calle\s+([^,.\n]+?)(?=\s*[,.\n]|esquina|$)',
            r'puente\s+([^,.\n]+?)(?=\s*[,.\n]|rampa|$)',
            r'circunvalación\s*([^,.\n]*?)(?=\s*[,.\n]|$)',
            r'paso a desnivel\s+(?:de\s+)?(?:la\s+)?([^,.\n]+?)(?=\s*[,.\n]|$)',
            r'(?:sector|zona|área)\s+([^,.\n]+?)(?=\s*[,.\n]|$)',
            r'(?:cerca de|próximo a)\s+([^,.\n]+?)(?=\s*[,.\n]|$)',
        ]

        for patron in patrones:
            matches = re.finditer(patron, texto_lower, re.IGNORECASE)
            for match in matches:
                ubicacion = match.group(1).strip() if match.lastindex else match.group(0).strip()
                ubicacion = re.sub(r'\s+', ' ', ubicacion)
                if len(ubicacion) > 2:  # Filter out very short matches
                    ubicaciones.append(ubicacion.title())

        # Extract known locations
        for ubicacion_conocida in self.ubicaciones_conocidas:
            if ubicacion_conocida in texto_lower:
                ubicaciones.append(ubicacion_conocida.title())

        # Extract kilometers
        km_matches = re.finditer(r'kilómetro\s+(\d+)', texto_lower)
        for match in km_matches:
            ubicaciones.append(f"Km {match.group(1)}")

        return list(set(ubicaciones))  # Remove duplicates
    
    def extract_topics_with_lda(self, textos: List[str], n_topics: int = 5) -> Dict:
        """Extrae temas usando Latent Dirichlet Allocation"""
        if not textos:
            return {}
        
        try:
            # Preprocess texts
            processed_texts = [self.preprocess_text(texto) for texto in textos]
            processed_texts = [texto for texto in processed_texts if len(texto) > 10]
            
            if len(processed_texts) < 2:
                return {}
            
            # Vectorize
            vectorizer = TfidfVectorizer(
                max_features=100,
                stop_words=list(self.stop_words),
                ngram_range=(1, 2),
                min_df=2
            )
            
            doc_term_matrix = vectorizer.fit_transform(processed_texts)
            
            # LDA
            lda = LatentDirichletAllocation(
                n_components=n_topics,
                random_state=42,
                max_iter=10
            )
            
            lda.fit(doc_term_matrix)
            
            # Extract topics
            feature_names = vectorizer.get_feature_names_out()
            topics = {}
            
            for topic_idx, topic in enumerate(lda.components_):
                top_words_idx = topic.argsort()[-10:][::-1]
                top_words = [feature_names[i] for i in top_words_idx]
                topics[f"Topic_{topic_idx}"] = top_words
            
            return topics
            
        except Exception as e:
            print(f"Error en análisis LDA: {e}")
            return {}
    
    def classify_incident_severity(self, texto: str) -> Dict[str, float]:
        """Clasifica la severidad del incidente usando TF-IDF y palabras clave"""
        if pd.isna(texto):
            return {'severity': 0.0, 'confidence': 0.0}
        
        # Severity indicators
        severity_keywords = {
            'high': ['muertos', 'fallecidos', 'heridos graves', 'hospitalizado', 'crítico', 'fatal'],
            'medium': ['heridos', 'lesionados', 'ambulancia', 'emergencia', 'atascado'],
            'low': ['lento', 'congestion', 'demora', 'tráfico pesado', 'fila']
        }
        
        texto_lower = texto.lower()
        severity_scores = {'high': 0, 'medium': 0, 'low': 0}
        
        for level, keywords in severity_keywords.items():
            for keyword in keywords:
                if keyword in texto_lower:
                    severity_scores[level] += 1
        
        # Calculate final severity (0-1 scale)
        total_high = severity_scores['high'] * 3
        total_medium = severity_scores['medium'] * 2
        total_low = severity_scores['low'] * 1
        
        total_score = total_high + total_medium + total_low
        
        if total_score == 0:
            return {'severity': 0.3, 'confidence': 0.1}  # Default low severity
        
        severity = min((total_high * 0.8 + total_medium * 0.5 + total_low * 0.2) / max(total_score, 1), 1.0)
        confidence = min(total_score / 10, 1.0)
        
        return {'severity': severity, 'confidence': confidence}
    
    def analyze_text_comprehensive(self, texto: str) -> Dict:
        """Análisis comprensivo del texto usando múltiples técnicas NLP"""
        if pd.isna(texto):
            return {}
        
        result = {
            'original_text': texto,
            'processed_text': self.preprocess_text(texto),
            'locations_regex': self.extract_locations_regex(texto),
            'entities_nltk': self.extract_entities_with_nltk(texto),
            'severity': self.classify_incident_severity(texto),
            'word_count': len(texto.split()),
            'char_count': len(texto)
        }
        
        # Add BERT analysis if available
        if BERT_AVAILABLE:
            result['entities_bert'] = self.extract_entities_with_bert(texto)
        
        # Combine all location extractions
        all_locations = set()
        
        # Add regex locations
        if result.get('locations_regex'):
            all_locations.update(result['locations_regex'])
        
        # Add NLTK locations
        if result.get('entities_nltk'):
            for entity in result['entities_nltk']:
                if entity.get('label') in ['GPE', 'LOCATION']:
                    all_locations.add(entity.get('text', ''))
        
        # Add BERT locations
        if result.get('entities_bert'):
            for entity in result['entities_bert']:
                if entity.get('label') == 'LOC':
                    all_locations.add(entity.get('text', ''))
        
        # Remove empty strings
        all_locations = {loc for loc in all_locations if loc and loc.strip()}
        
        result['all_locations'] = list(all_locations)
        
        return result
    
    def analyze_dataset(self, df: pd.DataFrame) -> pd.DataFrame:
        """Analiza todo el dataset usando técnicas NLP avanzadas"""
        print(f"🔍 Analizando {len(df)} textos con NLP avanzado...")
        
        df_enriched = df.copy()
        
        # Initialize new columns
        df_enriched['extracted_locations'] = ''
        df_enriched['severity_score'] = 0.0
        df_enriched['confidence_score'] = 0.0
        df_enriched['word_count'] = 0
        df_enriched['entities_found'] = 0
        df_enriched['incident_type_predicted'] = ''
        
        # Analyze each text
        all_analyses = []
        for idx, row in df.iterrows():
            try:
                analysis = self.analyze_text_comprehensive(row['text'])
                all_analyses.append(analysis)
                
                # Update dataframe with safe defaults
                locations = analysis.get('all_locations', [])
                severity = analysis.get('severity', {'severity': 0.0, 'confidence': 0.0})
                
                df_enriched.at[idx, 'extracted_locations'] = ', '.join(locations)
                df_enriched.at[idx, 'severity_score'] = severity.get('severity', 0.0)
                df_enriched.at[idx, 'confidence_score'] = severity.get('confidence', 0.0)
                df_enriched.at[idx, 'word_count'] = analysis.get('word_count', 0)
                df_enriched.at[idx, 'entities_found'] = len(locations)
                
            except Exception as e:
                print(f"Error procesando texto en fila {idx}: {e}")
                # Set default values for failed analysis
                df_enriched.at[idx, 'extracted_locations'] = ''
                df_enriched.at[idx, 'severity_score'] = 0.0
                df_enriched.at[idx, 'confidence_score'] = 0.0
                df_enriched.at[idx, 'word_count'] = 0
                df_enriched.at[idx, 'entities_found'] = 0
            
            if idx % 50 == 0:
                print(f"✅ Procesados {idx + 1}/{len(df)} textos...")
        
        # Topic modeling on the entire corpus
        print("📊 Extrayendo temas principales...")
        topics = self.extract_topics_with_lda(df['text'].tolist())
        
        # Print topic analysis
        if topics:
            print("\n🎯 TEMAS PRINCIPALES ENCONTRADOS:")
            for topic_name, words in topics.items():
                print(f"  {topic_name}: {', '.join(words[:5])}")
        
        return df_enriched
    
    def generate_report(self, df_enriched: pd.DataFrame) -> Dict:
        """Genera un reporte comprensivo del análisis"""
        print("\n📋 Generando reporte de análisis...")
        
        # Location analysis
        all_locations = []
        for locations_str in df_enriched['extracted_locations'].dropna():
            if locations_str:
                all_locations.extend(locations_str.split(', '))
        
        location_counts = Counter(all_locations)
        
        # Severity analysis
        avg_severity = df_enriched['severity_score'].mean()
        high_severity = len(df_enriched[df_enriched['severity_score'] > 0.7])
        medium_severity = len(df_enriched[(df_enriched['severity_score'] > 0.3) & (df_enriched['severity_score'] <= 0.7)])
        low_severity = len(df_enriched[df_enriched['severity_score'] <= 0.3])
        
        # Entity analysis
        avg_entities = df_enriched['entities_found'].mean()
        total_entities = df_enriched['entities_found'].sum()
        
        report = {
            'total_posts': len(df_enriched),
            'total_entities_found': total_entities,
            'avg_entities_per_post': avg_entities,
            'top_locations': dict(location_counts.most_common(10)),
            'severity_analysis': {
                'average_severity': avg_severity,
                'high_severity_incidents': high_severity,
                'medium_severity_incidents': medium_severity,
                'low_severity_incidents': low_severity
            },
            'word_statistics': {
                'avg_words_per_post': df_enriched['word_count'].mean(),
                'total_words': df_enriched['word_count'].sum(),
                'min_words': df_enriched['word_count'].min(),
                'max_words': df_enriched['word_count'].max()
            }
        }
        
        return report


def main():
    """Función principal del analizador NLP avanzado"""
    print("\n" + "=" * 80)
    print("🧠 ANALIZADOR NLP AVANZADO PARA TRÁFICO")
    print("=" * 80)
    print("Utilizando: BERT + scikit-learn + NLTK + Regex")
    print("=" * 80)

    # Initialize analyzer
    analizador = AdvancedNLPAnalyzer()

    # Test with sample text
    print("\n\n1. ANÁLISIS DE TEXTO DE PRUEBA:")
    print("-" * 80)
    
    texto_prueba = "Accidente vehicular en la Avenida 27 de Febrero cerca del kilómetro 15, " \
                   "hay heridos graves y tráfico lento hacia Máximo Gómez. Ambulancia en camino."
    
    resultado = analizador.analyze_text_comprehensive(texto_prueba)
    
    print(f"📝 Texto: {texto_prueba}")
    print(f"📍 Ubicaciones encontradas: {resultado['all_locations']}")
    print(f"🚨 Severidad: {resultado['severity']['severity']:.2f} (Confianza: {resultado['severity']['confidence']:.2f})")
    print(f"🔤 Palabras: {resultado['word_count']}")
    
    # Load and analyze full dataset
    print("\n\n2. ANÁLISIS DE DATASET COMPLETO:")
    print("-" * 80)

    # Load dataset
    csv_path = os.path.join(os.path.dirname(__file__), 'instagram_posts.csv')
    df = pd.read_csv(csv_path)
    print(f"Posts en el dataset: {len(df)}")

    # Analyze
    df_enriquecido = analizador.analyze_dataset(df)

    # Generate report
    reporte = analizador.generate_report(df_enriquecido)
    
    print("\n📊 REPORTE FINAL:")
    print("-" * 40)
    print(f"  Posts analizados: {reporte['total_posts']}")
    print(f"  Entidades encontradas: {reporte['total_entities_found']}")
    print(f"  Promedio entidades por post: {reporte['avg_entities_per_post']:.2f}")
    print(f"  Severidad promedio: {reporte['severity_analysis']['average_severity']:.2f}")
    print(f"  Incidentes alta severidad: {reporte['severity_analysis']['high_severity_incidents']}")
    print(f"  Palabras promedio por post: {reporte['word_statistics']['avg_words_per_post']:.1f}")

    print(f"\n  Top 5 ubicaciones:")
    for ubicacion, count in list(reporte['top_locations'].items())[:5]:
        print(f"    - {ubicacion}: {count}")

    # Save enriched dataset
    output_path = os.path.join(os.path.dirname(__file__), 'accidents.csv')
    df_enriquecido['extracted_locations'] = df_enriquecido['extracted_locations'].apply(
        lambda x: ', '.join(x) if isinstance(x, list) else x
    )
    df_enriquecido.to_csv(output_path, index=False)
    print(f"\n✓ Dataset enriquecido guardado en: {output_path}")

    print("\n" + "=" * 80)
    print("✅ ANÁLISIS NLP AVANZADO COMPLETADO")
    print("=" * 80)


if __name__ == "__main__":
    main()