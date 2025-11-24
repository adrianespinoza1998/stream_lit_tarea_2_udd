# Visualización Interactiva de Emisiones de CO₂

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://your-app-url.streamlit.app)

## 📋 Descripción

Esta aplicación web interactiva permite explorar y analizar las emisiones globales de CO₂ a través de múltiples visualizaciones basadas en datos de [Our World in Data](https://ourworldindata.org/co2-emissions). La aplicación ofrece 4 tipos de visualizaciones principales:

- **Mapa coroplético por país**: Visualización geográfica de emisiones por país en un año específico
- **Evolución temporal**: Gráfico de línea mostrando la evolución de emisiones globales o por países seleccionados
- **Emisiones por tipo**: Comparación de emisiones por combustibles fósiles vs. cambio de uso de suelo
- **Evolución por región**: Análisis de la participación porcentual de los principales emisores a lo largo del tiempo

## 🚀 Instrucciones de ejecución local

### Prerrequisitos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)
- Git (opcional, para clonar el repositorio)

### Instalación

1. **Clonar el repositorio** (o descargar el ZIP)

```bash
git clone https://github.com/adrianespinoza1998/stream_lit_tutorial_udd.git
cd stream_lit_tutorial_udd
```

2. **Instalar dependencias**

```bash
pip install -r requirements.txt
```

3. **Ejecutar la aplicación**

```bash
streamlit run app.py
```

4. **Acceder a la aplicación**

La aplicación se abrirá automáticamente en tu navegador en `http://localhost:8501`

## 📦 Estructura del proyecto

```
stream_lit_tutorial_udd/
├── app.py                          # Aplicación principal de Streamlit
├── requirements.txt                # Dependencias del proyecto
├── README.md                       # Este archivo
├── data/
│   └── raw/
│       ├── 50m_cultural/          # Shapefiles de Natural Earth
│       ├── emissions_per_country/  # Dataset principal de emisiones
│       └── co2-fossil-plus-land-use/ # Dataset de emisiones por fuente
├── notebooks/
│   └── ejercicio_co2.ipynb        # Notebook de desarrollo
└── material/
    └── tarea_2.md                 # Especificaciones del proyecto
```

## 🛠️ Requisitos técnicos

### Librerías principales

- **streamlit** (≥1.29.0): Framework web para aplicaciones interactivas
- **plotly** (≥5.18.0): Visualizaciones interactivas
- **pandas** (≥2.0.0): Manipulación y análisis de datos
- **geopandas** (≥0.14.0): Procesamiento de datos geoespaciales

Ver `requirements.txt` para la lista completa de dependencias.

### Python version

Python 3.8+

## 📊 Fuentes de datos

### 1. Annual CO₂ emissions per country
- **Fuente**: [Our World in Data](https://ourworldindata.org/co2-emissions)
- **Proveedor original**: Global Carbon Project
- **Periodo**: 1750 - 2024
- **Actualización**: Noviembre 2024
- **Unidad**: Toneladas de CO₂
- **Cobertura**: ~200 países y territorios

### 2. CO₂ emissions from fossil fuels and land-use change
- **Fuente**: [Our World in Data](https://ourworldindata.org/co2-emissions)
- **Proveedor original**: Global Carbon Project
- **Periodo**: 1750 - 2024
- **Variables**: 
  - Emisiones totales
  - Emisiones por combustibles fósiles
  - Emisiones por cambio de uso de suelo

### 3. Natural Earth Shapefiles
- **Fuente**: [Natural Earth](https://www.naturalearthdata.com/)
- **Resolución**: 1:50m
- **Dataset**: Admin 0 - Countries

## 🎨 Características principales

### Interactividad
- Selección de años mediante sliders
- Filtrado por países específicos
- Rangos de años personalizables
- Navegación por pestañas

### Visualizaciones
- Mapas coropléticos con proyección Natural Earth
- Gráficos de línea con marcadores
- Barras horizontales animadas
- Áreas apiladas normalizadas

### Optimizaciones
- Cache de datos con `@st.cache_data`
- Carga dinámica de controles según pestaña activa
- Renderizado condicional de visualizaciones

## 📖 Documentación adicional

La aplicación incluye una sección completa de documentación accesible desde la pestaña "Documentación" que incluye:

- Descripción detallada de los datasets
- Justificación de decisiones de diseño
- Limitaciones y consideraciones metodológicas
- Referencias y fuentes

## 🤖 Declaración de uso de IA

Esta aplicación fue desarrollada con asistencia de **GitHub Copilot** para:

- Generación de código base de Streamlit y Plotly
- Optimización de queries de pandas y geopandas
- Estructuración de layout y componentes interactivos
- Documentación y comentarios en código

Todo el código fue revisado, adaptado y probado manualmente para asegurar su correcta funcionalidad y alineación con los requisitos del proyecto.

## 👨‍💻 Autores

**Adrián Espinoza**
- GitHub: [@adrianespinoza1998](https://github.com/adrianespinoza1998)

**Rodrigo Castro**
- GitHub: [@Rcastrovera](https://github.com/Rcastrovera)

**Sebastián González**
- GitHub: [@segovis-dot](https://github.com/segovis-dot)

**Vanessa Camaggi**
- GitHub: [@vanessacamaggi-ui](https://github.com/vanessacamaggi-ui)

## 📝 Licencia

Los datos utilizados provienen de Our World in Data y el Global Carbon Project. Por favor, revisa sus términos de uso:
- [Our World in Data - Terms of Use](https://ourworldindata.org/about#legal)
- [Global Carbon Project](https://www.globalcarbonproject.org/)

## 🙏 Agradecimientos

- [Our World in Data](https://ourworldindata.org/) por proporcionar datos de alta calidad sobre emisiones de CO₂
- [Natural Earth](https://www.naturalearthdata.com/) por los shapefiles de países
- [Streamlit](https://streamlit.io/) por el framework de desarrollo
- [Plotly](https://plotly.com/) por las herramientas de visualización

---

**Proyecto desarrollado para el curso de Visualización de Información - Universidad del Desarrollo (UDD) - 2025**


