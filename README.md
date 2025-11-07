# Transporte: Optimización del Tráfico y la Logística en Tiempo Real

Caso práctico 3 [COLABORATIVO 02]: Solución Agentica NLP

### Configurar Entorno Python
Versión de Python utilizada: 3.13.3

Activar el entorno virtual (macOS/Linux):
```bash
python -m venv venv
```
```bash 
source venv/bin/activate
```

Windows:
```bash
python -m venv venv
```
```bash
venv\Scripts\activate
```

### Instalar dependencias:
```bash
python -m pip install -r requirements.txt
```

### ETL

Vamos a utilizar el dataset extraído llamado **`instagram_posts.csv`**.
Para ello, es necesario ejecutar el siguiente comando:

```bash
python run_pipeline.py
```

Debes seleccionar las **opciones 1 y 2** para generar los archivos **.csv** con sus respectivas **clasificaciones mediante NLP** y los **datos genéricos** que simulan usuarios y puntos de interés.

---

El **dataset** ya está incluido en este proyecto. Sin embargo, si deseas **descargar datos desde otras cuentas de Instagram**, deberás **configurar tu propia instancia de Instaloader**.

> **Nota:** Asegúrate de revisar cuidadosamente la documentación oficial de Instaloader en [https://instaloader.github.io/](https://instaloader.github.io/) para evitar el bloqueo de tu cuenta y cumplir con los **términos de privacidad y uso de Instagram**.

```bash
python -m instaloader --login tu_usuario_de_instagram
```

### Ver recomendaciones

```bash
python run_pipeline.py
```

Debes seleccionar las opciones de recomendaciones desde el menú.
Es requisito haber ejecutado previamente el paso de ETL.