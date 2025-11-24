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

### Áreas donde se utilizó IA:

1. **Generación de código base**
   - Estructura inicial de la aplicación Streamlit
   - Templates de visualizaciones con Plotly Express y Graph Objects
   - Funciones de carga y procesamiento de datos con Pandas y GeoPandas

2. **Optimización de código**
   - Queries eficientes de agregación y filtrado con Pandas
   - Implementación de `@st.cache_data` para optimización de rendimiento
   - Operaciones geoespaciales con GeoPandas (joins, proyecciones)

3. **Desarrollo de funcionalidades interactivas**
   - Sistema de navegación por pestañas con radio buttons
   - Controles dinámicos del sidebar (sliders, multiselect, checkboxes)
   - Sincronización de estado entre controles y visualizaciones

4. **Visualizaciones personalizadas**
   - Configuración de layouts de Plotly (títulos, ejes, leyendas)
   - Paletas de colores y estilos consistentes
   - Hover templates personalizados

5. **Documentación**
   - Comentarios explicativos en código
   - Docstrings de funciones
   - Contenido de la sección de documentación de la app
   - Este README.md

### Proceso de revisión:

- ✅ **Todo el código generado fue revisado línea por línea**
- ✅ **Se realizaron adaptaciones manuales** para ajustar a los requisitos específicos
- ✅ **Se probó exhaustivamente** cada funcionalidad y visualización
- ✅ **Se validó la precisión** de cálculos y agregaciones de datos
- ✅ **Se optimizó el rendimiento** mediante profiling y ajustes manuales

### Limitaciones de la IA:

La IA fue utilizada como herramienta de productividad, pero **no** para:
- Toma de decisiones de diseño (paletas, escalas, tipos de gráficos)
- Análisis e interpretación de datos
- Selección de datasets y fuentes
- Arquitectura general de la aplicación

Todo el diseño conceptual, las decisiones analíticas y la validación de resultados fueron realizados manualmente por el equipo de desarrollo.

## 👨‍💻 Autores

Este proyecto fue desarrollado en equipo por estudiantes de la Universidad del Desarrollo (UDD) para el curso de Visualización de Información (2025).

### Equipo de desarrollo:

**Adrián Espinoza** - Líder de Proyecto
- GitHub: [@adrianespinoza1998](https://github.com/adrianespinoza1998)
- Rol: Arquitectura de la aplicación, integración de visualizaciones, documentación técnica

**Rodrigo Castro** - Desarrollador Backend
- GitHub: [@Rcastrovera](https://github.com/Rcastrovera)
- Rol: Procesamiento de datos geoespaciales, optimización de queries, implementación de cache

**Sebastián González** - Desarrollador Frontend
- GitHub: [@segovis-dot](https://github.com/segovis-dot)
- Rol: Diseño de interfaz, controles interactivos, experiencia de usuario

**Vanessa Camaggi** - Analista de Datos
- GitHub: [@vanessacamaggi-ui](https://github.com/vanessacamaggi-ui)
- Rol: Análisis de datos, validación de cálculos, documentación de fuentes

### Contribuciones:

Todos los miembros del equipo contribuyeron activamente en:
- 🎨 Diseño de visualizaciones
- 📊 Análisis y validación de datos
- 💻 Revisión de código
- 📝 Documentación del proyecto
- 🧪 Testing y control de calidad

### Contacto:

Para preguntas o colaboraciones, pueden contactarnos a través de nuestros perfiles de GitHub o crear un issue en el repositorio.

## 📝 Licencia y Uso de Datos

### Licencia del Proyecto

Este proyecto está desarrollado con fines educativos para el curso de Visualización de Información de la Universidad del Desarrollo (UDD).

**Código fuente**: El código de esta aplicación está disponible bajo licencia MIT. Eres libre de usar, modificar y distribuir el código siempre que se mantenga la atribución a los autores originales.

### Licencia de los Datos

Los datos utilizados en este proyecto provienen de fuentes externas con sus propias licencias:

#### 1. Our World in Data
- **Licencia**: [Creative Commons BY 4.0](https://creativecommons.org/licenses/by/4.0/)
- **Requisito**: Atribución obligatoria al usar los datos
- **Fuente**: [Our World in Data - CO₂ and Greenhouse Gas Emissions](https://ourworldindata.org/co2-emissions)
- **Términos de uso**: [Our World in Data - Terms of Use](https://ourworldindata.org/about#legal)

**Cómo citar OWID**:
```
Hannah Ritchie, Pablo Rosado and Max Roser (2023) - "CO₂ and Greenhouse Gas Emissions". 
Published online at OurWorldInData.org. 
Retrieved from: 'https://ourworldindata.org/co2-emissions' [Online Resource]
```

#### 2. Global Carbon Project
- **Licencia**: Creative Commons Attribution 4.0 International License
- **Fuente**: [Global Carbon Budget](https://globalcarbonbudget.org/)
- **Citación requerida**: Global Carbon Project (2024)

**Cómo citar GCP**:
```
Friedlingstein et al. (2024), Global Carbon Budget 2024, Earth System Science Data, 
https://doi.org/10.5194/essd-16-4991-2024
```

#### 3. Natural Earth
- **Licencia**: Public Domain
- **Fuente**: [Natural Earth Data](https://www.naturalearthdata.com/)
- **Uso**: Libre sin restricciones, atribución apreciada pero no requerida

### Responsabilidad de Uso

Si decides reutilizar los datos o el código de este proyecto:

✅ **Debes**:
- Dar crédito apropiado a Our World in Data y Global Carbon Project
- Mantener las atribuciones originales
- Verificar la versión más reciente de los datos en las fuentes originales
- Revisar y cumplir con los términos de uso de cada fuente

❌ **No debes**:
- Presentar los datos como propios
- Usar los datos sin atribución adecuada
- Modificar los datos sin documentar los cambios

### Descargo de Responsabilidad

Los datos presentados en esta aplicación son recopilados y procesados por terceros (Our World in Data, Global Carbon Project). Si bien se ha realizado un esfuerzo para garantizar la precisión, los autores de esta aplicación no se responsabilizan por errores en los datos originales o en su interpretación. Para uso académico, investigación o toma de decisiones, se recomienda consultar las fuentes originales directamente.

## 🙏 Agradecimientos

- [Our World in Data](https://ourworldindata.org/) por proporcionar datos de alta calidad sobre emisiones de CO₂
- [Natural Earth](https://www.naturalearthdata.com/) por los shapefiles de países
- [Streamlit](https://streamlit.io/) por el framework de desarrollo
- [Plotly](https://plotly.com/) por las herramientas de visualización

---

**Proyecto desarrollado para el curso de Visualización de Información - Universidad del Desarrollo (UDD) - 2025**


