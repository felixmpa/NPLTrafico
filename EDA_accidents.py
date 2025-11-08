import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
import os
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Configurar estilo de visualización
plt.style.use('default')
sns.set_palette("husl")

class AccidentsEDA:
    def __init__(self, csv_path):
        """Initialize EDA with accidents dataset"""
        self.csv_path = csv_path
        self.df = None
        self.load_data()
    
    def load_data(self):
        """Load and prepare the accidents dataset"""
        print("📊 ANÁLISIS EXPLORATORIO DE DATOS - ACCIDENTES DE TRÁFICO")
        print("=" * 70)
        
        try:
            self.df = pd.read_csv(self.csv_path)
            print(f"✅ Dataset cargado exitosamente: {len(self.df)} registros")
        except Exception as e:
            print(f"❌ Error cargando dataset: {e}")
            return
    
    def basic_info(self):
        """Display basic dataset information"""
        print("\n📋 INFORMACIÓN BÁSICA DEL DATASET")
        print("-" * 50)
        
        print(f"📏 Dimensiones: {self.df.shape[0]} filas x {self.df.shape[1]} columnas")
        print(f"📅 Período: {self.df['year'].min()} - {self.df['year'].max()}")
        print(f"💾 Memoria utilizada: {self.df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
        
        print("\n📊 Tipos de datos:")
        for col, dtype in self.df.dtypes.items():
            null_count = self.df[col].isnull().sum()
            null_pct = (null_count / len(self.df)) * 100
            print(f"  {col:<25} {str(dtype):<10} | Nulos: {null_count:>3} ({null_pct:>5.1f}%)")
    
    def severity_analysis(self):
        """Analyze severity scores and patterns"""
        print("\n🚨 ANÁLISIS DE SEVERIDAD")
        print("-" * 50)
        
        severity_stats = self.df['severity_score'].describe()
        print("📈 Estadísticas de severidad:")
        for stat, value in severity_stats.items():
            print(f"  {stat:<10}: {value:.3f}")
        
        # Categorizar severidad
        self.df['severity_category'] = pd.cut(
            self.df['severity_score'], 
            bins=[0, 0.3, 0.7, 1.0], 
            labels=['Leve', 'Moderado', 'Grave'],
            include_lowest=True
        )
        
        severity_counts = self.df['severity_category'].value_counts()
        print(f"\n🏷️ Distribución por categorías:")
        for category, count in severity_counts.items():
            pct = (count / len(self.df)) * 100
            print(f"  {category:<10}: {count:>3} ({pct:>5.1f}%)")
        
        # Severidad por plataforma
        print(f"\n📱 Severidad promedio por plataforma:")
        platform_severity = self.df.groupby('platform')['severity_score'].agg(['mean', 'count']).round(3)
        for platform, stats in platform_severity.iterrows():
            print(f"  {platform:<12}: {stats['mean']:.3f} (n={stats['count']})")
    
    def location_analysis(self):
        """Analyze location patterns"""
        print("\n📍 ANÁLISIS DE UBICACIONES")
        print("-" * 50)
        
        # Contar ubicaciones extraídas
        locations_with_data = self.df[self.df['extracted_locations'].notna() & 
                                     (self.df['extracted_locations'] != '')]
        
        print(f"📊 Posts con ubicaciones extraídas: {len(locations_with_data)} ({len(locations_with_data)/len(self.df)*100:.1f}%)")
        print(f"📊 Promedio de entidades por post: {self.df['entities_found'].mean():.2f}")
        
        # Extraer todas las ubicaciones
        all_locations = []
        for locations_str in locations_with_data['extracted_locations']:
            if pd.notna(locations_str) and locations_str:
                locations = [loc.strip() for loc in locations_str.split(',')]
                all_locations.extend(locations)
        
        location_counts = Counter(all_locations)
        
        print(f"\n🏆 Top 15 ubicaciones más mencionadas:")
        for i, (location, count) in enumerate(location_counts.most_common(15), 1):
            print(f"  {i:>2}. {location:<25}: {count:>3} veces")
        
        return location_counts
    
    def temporal_analysis(self):
        """Analyze temporal patterns"""
        print("\n⏰ ANÁLISIS TEMPORAL")
        print("-" * 50)
        
        # Análisis por hora
        print("🕐 Distribución por hora del día:")
        # Definir los intervalos de 3 horas
        bins = [(0, 2), (3, 5), (6, 8), (9, 11), (12, 14), (15, 17), (18, 20), (21, 23)]

        total = 0
        for start, end in bins:
            # Contar cuántos registros caen dentro de ese rango
            mask = (self.df['hour'] >= start) & (self.df['hour'] <= end)
            count = mask.sum()
            total += count
            pct = (count / len(self.df)) * 100
            print(f"  {start:>2}:00-{end:>2}:59: {count:>3} ({pct:>4.1f}%)")

        print(f"\n✅ Total registros contabilizados: {total} ({(total/len(self.df))*100:.1f}%)")
        
        # Análisis por día de la semana
        print("\n📅 Distribución por día de la semana:")
        day_counts = self.df['day_of_week'].value_counts().sort_index()
        days = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
        for day_num, day_name in enumerate(days):
            count = day_counts.get(day_num, 0)
            pct = (count / len(self.df)) * 100
            print(f"  {day_name:<10}: {count:>3} ({pct:>4.1f}%)")
        
        # Fin de semana vs días laborables
        weekend_pct = (self.df['is_weekend'].sum() / len(self.df)) * 100
        print(f"\n📊 Fin de semana: {self.df['is_weekend'].sum()} ({weekend_pct:.1f}%)")
        print(f"📊 Días laborables: {(~self.df['is_weekend']).sum()} ({100-weekend_pct:.1f}%)")
    
    def engagement_analysis(self):
        """Analyze social media engagement"""
        print("\n💬 ANÁLISIS DE ENGAGEMENT")
        print("-" * 50)
        
        # Estadísticas de engagement
        engagement_cols = ['likes', 'comments_count', 'video_views']
        
        for col in engagement_cols:
            if col in self.df.columns:
                stats = self.df[col].describe()
                print(f"\n📊 {col.replace('_', ' ').title()}:")
                print(f"  Promedio: {stats['mean']:.1f}")
                print(f"  Mediana:  {stats['50%']:.1f}")
                print(f"  Máximo:   {stats['max']:.0f}")
        
        # Correlación entre severidad y engagement
        print(f"\n🔗 Correlación severidad vs engagement:")
        for col in engagement_cols:
            if col in self.df.columns:
                corr = self.df['severity_score'].corr(self.df[col])
                print(f"  Severidad vs {col.replace('_', ' ')}: {corr:.3f}")
    
    def text_analysis(self):
        """Analyze text characteristics"""
        print("\n📝 ANÁLISIS DE TEXTO")
        print("-" * 50)
        
        word_stats = self.df['word_count'].describe()
        print("📖 Estadísticas de palabras por post:")
        for stat, value in word_stats.items():
            print(f"  {stat:<10}: {value:.1f}")
        
        # Posts más largos y más cortos
        longest_post = self.df.loc[self.df['word_count'].idxmax()]
        shortest_post = self.df.loc[self.df['word_count'].idxmin()]
        
        print(f"\n📏 Post más largo: {longest_post['word_count']} palabras")
        longest_text = str(longest_post['text']) if pd.notna(longest_post['text']) else "Texto no disponible"
        print(f"   Texto: {longest_text[:100]}...")
        
        print(f"\n📏 Post más corto: {shortest_post['word_count']} palabras")
        shortest_text = str(shortest_post['text']) if pd.notna(shortest_post['text']) else "Texto no disponible"
        print(f"   Texto: {shortest_text[:100]}...")
        
        # Confianza en análisis
        confidence_stats = self.df['confidence_score'].describe()
        print(f"\n🎯 Estadísticas de confianza en el análisis:")
        for stat, value in confidence_stats.items():
            print(f"  {stat:<10}: {value:.3f}")
            
    def outlier_analysis(self):
        """Analyze severity distribution and outliers by day of week"""
        print("\n📊 ANÁLISIS DE OUTLIERS - SEVERIDAD POR DÍA")
        print("-" * 60)

        if 'day_of_week' not in self.df.columns or 'severity_score' not in self.df.columns:
            print("⚠️ No hay columnas 'day_of_week' o 'severity_score' para el análisis.")
            return

        # Días en orden lógico
        day_labels = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
        self.df['day_name'] = self.df['day_of_week'].replace(dict(zip(range(7), day_labels)))

        # Estadísticas por día
        print("📈 Severidad promedio por día:")
        day_stats = self.df.groupby('day_name')['severity_score'].describe()[['mean', 'min', 'max']].round(3)
        print(day_stats)

        # 🎨 Boxplot por día
        plt.figure(figsize=(10, 6))
        sns.boxplot(
            data=self.df,
            x='day_name',
            y='severity_score',
            palette='coolwarm',
            linewidth=1.2,
            boxprops=dict(alpha=0.8),
            medianprops=dict(color='yellow', linewidth=2)
        )
        plt.title("📦 Distribución de Severidad por Día de la Semana", fontsize=13, pad=12)
        plt.xlabel("Día de la semana")
        plt.ylabel("Score de Severidad")
        plt.grid(axis='y', linestyle='--', alpha=0.6)
        plt.tight_layout()
        plt.show()
    
    def create_visualizations(self):
        """Create data visualizations"""
        print("\n📈 GENERANDO VISUALIZACIONES")
        print("-" * 50)
        
        # Crear directorio para gráficos
        plots_dir = "plots"
        os.makedirs(plots_dir, exist_ok=True)
        
        # 1. Distribución de severidad
        plt.figure(figsize=(12, 8))
        
        plt.subplot(2, 3, 1)
        self.df['severity_score'].hist(bins=20, alpha=0.7, color='skyblue', edgecolor='black')
        plt.title('Distribución de Severidad')
        plt.xlabel('Score de Severidad')
        plt.ylabel('Frecuencia')
        
        plt.subplot(2, 3, 2)
        severity_counts = self.df['severity_category'].value_counts()
        plt.pie(severity_counts.values, labels=severity_counts.index, autopct='%1.1f%%', startangle=90)
        plt.title('Severidad por Categorías')
        
        # 2. Análisis temporal
        plt.subplot(2, 3, 3)
        hour_counts = self.df['hour'].value_counts().sort_index()
        plt.plot(hour_counts.index, hour_counts.values, marker='o', color='orange')
        plt.title('Accidentes por Hora del Día')
        plt.xlabel('Hora')
        plt.ylabel('Cantidad')
        plt.xticks(range(0, 24, 4))
        
        plt.subplot(2, 3, 4)
        day_counts = self.df['day_of_week'].value_counts().sort_index()
        days = ['L', 'M', 'X', 'J', 'V', 'S', 'D']
        plt.bar(days, [day_counts.get(i, 0) for i in range(7)], color='lightcoral')
        plt.title('Accidentes por Día de la Semana')
        plt.xlabel('Día')
        plt.ylabel('Cantidad')
        
        # 3. Análisis de texto
        plt.subplot(2, 3, 5)
        self.df['word_count'].hist(bins=15, alpha=0.7, color='lightgreen', edgecolor='black')
        plt.title('Distribución de Palabras por Post')
        plt.xlabel('Número de Palabras')
        plt.ylabel('Frecuencia')
        
        # 4. Entidades encontradas
        plt.subplot(2, 3, 6)
        entities_counts = self.df['entities_found'].value_counts().sort_index()
        plt.bar(entities_counts.index, entities_counts.values, color='mediumpurple')
        plt.title('Entidades Encontradas por Post')
        plt.xlabel('Número de Entidades')
        plt.ylabel('Cantidad de Posts')
        
        plt.tight_layout()
        plot_path = os.path.join(plots_dir, 'accidents_eda_overview.png')
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        print(f"✅ Gráfico general guardado: {plot_path}")
        
        # Mapa de calor de correlaciones
        plt.figure(figsize=(10, 8))
        numeric_cols = ['severity_score', 'confidence_score', 'word_count', 'entities_found', 
                       'likes', 'comments_count', 'hour']
        numeric_cols = [col for col in numeric_cols if col in self.df.columns]
        
        correlation_matrix = self.df[numeric_cols].corr()
        sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0, 
                    square=True, linewidths=0.5)
        plt.title('Matriz de Correlación - Variables Numéricas')
        plt.tight_layout()
        
        corr_path = os.path.join(plots_dir, 'accidents_correlation_matrix.png')
        plt.savefig(corr_path, dpi=300, bbox_inches='tight')
        print(f"✅ Matriz de correlación guardada: {corr_path}")
        
        plt.show()
    
    def generate_insights_report(self):
        """Generate key insights report"""
        print("\n💡 INSIGHTS CLAVE")
        print("=" * 70)
        
        insights = []
        
        # Insight 1: Severidad general
        avg_severity = self.df['severity_score'].mean()
        high_severity_pct = (self.df['severity_score'] > 0.7).mean() * 100
        insights.append(f"🎯 Severidad promedio: {avg_severity:.2f} - {high_severity_pct:.1f}% son incidentes graves")
        
        # Insight 2: Cobertura de ubicaciones
        location_coverage = (self.df['extracted_locations'].notna() & 
                           (self.df['extracted_locations'] != '')).mean() * 100
        insights.append(f"📍 Cobertura de ubicaciones: {location_coverage:.1f}% de posts tienen ubicaciones extraídas")
        
        # Insight 3: Hora pico
        peak_hour = self.df['hour'].value_counts().idxmax()
        peak_count = self.df['hour'].value_counts().max()
        insights.append(f"🕐 Hora pico de reportes: {peak_hour}:00 ({peak_count} reportes)")
        
        # Insight 4: Día más activo
        peak_day = self.df['day_of_week'].value_counts().idxmax()
        if isinstance(peak_day, str):
            peak_day_name = peak_day
        else:
            days = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
            peak_day_name = days[peak_day] if 0 <= peak_day < len(days) else str(peak_day)
        insights.append(f"📅 Día con más reportes: {peak_day_name}")
        
        # Insight 5: Relación palabras-severidad
        word_severity_corr = self.df['word_count'].corr(self.df['severity_score'])
        if abs(word_severity_corr) > 0.1:
            direction = "positiva" if word_severity_corr > 0 else "negativa"
            insights.append(f"📝 Correlación {direction} entre longitud del texto y severidad: {word_severity_corr:.3f}")
        
        # Insight 6: Plataforma más activa
        most_active_platform = self.df['platform'].value_counts().idxmax()
        platform_pct = (self.df['platform'] == most_active_platform).mean() * 100
        insights.append(f"📱 Plataforma más activa: {most_active_platform} ({platform_pct:.1f}% de reportes)")
        
        for i, insight in enumerate(insights, 1):
            print(f"{i}. {insight}")
        
        # Generar reporte en archivo
        report_path = "accidents_eda_report.txt"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("REPORTE EDA - ANÁLISIS DE ACCIDENTES DE TRÁFICO\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Dataset: {self.csv_path}\n")
            f.write(f"Registros analizados: {len(self.df)}\n\n")
            
            f.write("INSIGHTS PRINCIPALES:\n")
            f.write("-" * 30 + "\n")
            for i, insight in enumerate(insights, 1):
                f.write(f"{i}. {insight}\n")
        
        print(f"\n✅ Reporte completo guardado: {report_path}")
    
    def run_full_analysis(self):
        """Run complete EDA analysis"""
        if self.df is None:
            print("❌ No se pudo cargar el dataset")
            return
        
        self.basic_info()
        self.severity_analysis()
        self.location_analysis()
        self.temporal_analysis()
        self.engagement_analysis()
        self.text_analysis()
        self.outlier_analysis()
        self.create_visualizations()
        self.generate_insights_report()
        
        print("\n" + "=" * 70)
        print("✅ ANÁLISIS EDA COMPLETADO")
        print("=" * 70)


def run():
    """Main function to run EDA analysis"""
    accidents_path = os.path.join("ETL", "accidents.csv")
    
    if not os.path.exists(accidents_path):
        print(f"❌ Archivo no encontrado: {accidents_path}")
        print("💡 Ejecuta primero el análisis NPL para generar el archivo accidents.csv")
        return
    
    eda = AccidentsEDA(accidents_path)
    eda.run_full_analysis()


if __name__ == "__main__":
    run()