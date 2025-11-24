import os

import geopandas as gpd
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ============================
# configuración de la app
# ============================
st.set_page_config(
    page_title='mapa de emisiones de co₂',
    layout='wide'
)

BASE_DIR = os.path.dirname(__file__)
SHP_PATH = os.path.join(BASE_DIR, 'data', 'raw', '50m_cultural', 'ne_50m_admin_0_countries.shp')
CSV_PATH = os.path.join(BASE_DIR, 'data', 'raw', 'emissions_per_country', 'annual-co2-emissions-per-country.csv')
CSV_FOSSIL_PATH = os.path.join(BASE_DIR, 'data', 'raw', 'co2-fossil-plus-land-use', 'co2-fossil-plus-land-use.csv')



# ============================
# carga y preparación de datos
# ============================
@st.cache_data
def load_world(shp_path: str):
    """
    carga el shapefile de países y construye:
    - world_master: maestro de países indexado por iso3
    - geojson_world: geometría en formato geojson para plotly
    """
    if not os.path.exists(shp_path):
        raise FileNotFoundError(f'no se encontró el shapefile: {shp_path}')

    world = gpd.read_file(shp_path)

    # estandarizar columna iso3
    world = world.rename(columns={'ISO_A3': 'code'})
    world['code'] = world['code'].str.upper()

    # maestro de países: una sola fila por code
    world_master = (
        world[['code', 'NAME', 'geometry']]
        .drop_duplicates(subset=['code'])
        .rename(columns={'NAME': 'country'})
        .set_index('code')
    )

    geojson_world = world_master['geometry'].__geo_interface__

    return world_master, geojson_world


@st.cache_data
def load_emissions(csv_path: str) -> pd.DataFrame:
    """
    carga el csv de emisiones y lo deja listo para usar
    con columnas: country, code, year, co2
    """
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f'no se encontró el csv de emisiones: {csv_path}')

    df = pd.read_csv(csv_path)

    df = df.rename(columns={'Entity': 'country', 'Code': 'code', 'Year': 'year'})
    df['code'] = df['code'].str.upper()

    # filtrar a códigos iso válidos
    df = df[df['code'].str.len() == 3]

    # quedarnos con la columna de emisiones (asumimos una métrica principal)
    value_col = [c for c in df.columns if c not in ['country', 'code', 'year']]
    if not value_col:
        raise ValueError('no se encontró ninguna columna de emisiones distinta de country/code/year')

    df = df.rename(columns={value_col[0]: 'co2'})

    return df[['country', 'code', 'year', 'co2']]


@st.cache_data
def load_fossil_emissions(csv_path: str) -> pd.DataFrame:
    """
    carga el csv de emisiones fósiles y cambio de uso de suelo
    """
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f'no se encontró el csv de emisiones fósiles: {csv_path}')

    df = pd.read_csv(csv_path)
    
    df = df.rename(columns={
        'Entity': 'country',
        'Code': 'code',
        'Year': 'year',
        'Annual CO₂ emissions including land-use change': 'total',
        'Annual CO₂ emissions from land-use change': 'land_use_change',
        'Annual CO₂ emissions': 'fossil_fuels'
    })
    
    df = df.drop(columns=['code'], errors='ignore')
    
    return df


# ============================
# lógica de visualización
# ============================
def make_co2_map(df_co2: pd.DataFrame,
                 world_master: gpd.GeoDataFrame,
                 geojson_world: dict,
                 year: int):
    """
    genera el mapa de emisiones de co₂ por país para un año dado.
    respeta tu lógica original, pero preparado para streamlit.
    """
    # emisiones del año seleccionado, agregadas por país
    co2_year = (
        df_co2[df_co2['year'] == year][['code', 'co2']]
        .groupby('code', as_index=False)
        .agg({'co2': 'sum'})
        .set_index('code')
    )

    # unir al maestro: aquí nunca se pierden países
    world_y = world_master.join(co2_year, how='left')

    # países con dato vs sin dato
    g_with = world_y[world_y['co2'].notna()].reset_index()
    g_no = world_y[world_y['co2'].isna()].reset_index()

    # capa 1: países con dato → escala continua
    fig = px.choropleth(
        g_with,
        geojson=geojson_world,
        locations='code',            # usa el iso3
        color='co2',
        hover_name='country',
        projection='natural earth',
        color_continuous_scale='Reds'
    )

    # capa 2: países sin dato → gris, sin leyenda
    if not g_no.empty:
        fig_grey = px.choropleth(
            g_no,
            geojson=geojson_world,
            locations='code',
            color_discrete_sequence=['#d0d0d0'],
            hover_name='country',
            projection='natural earth'
        )
        for trace in fig_grey.data:
            trace.showlegend = False
            fig.add_trace(trace)

    fig.update_geos(fitbounds='locations', visible=False)
    fig.update_layout(
        title_text=f'emisiones de co₂ por país en {year}',
        title_x=0.5,
        height=600
    )

    return fig


# ============================
# app principal
# ============================
def main():
    st.title('mapa interactivo de emisiones de co₂')
    st.markdown(
        """
        esta aplicación muestra las emisiones anuales de co₂ por país usando datos de our world in data.
        puedes explorar distintos años y comparar cómo cambia el mapa a lo largo del tiempo.
        """
    )

    # cargar datos
    world_master, geojson_world = load_world(SHP_PATH)
    df_co2 = load_emissions(CSV_PATH)
    df_fossil = load_fossil_emissions(CSV_FOSSIL_PATH)

    # selector de visualización en sidebar
    st.sidebar.header('Navegación')
    selected_tab = st.sidebar.radio(
        'Selecciona una visualización:',
        ['Mapa por país', 'Evolución temporal', 'Emisiones por tipo', 'Evolución por región', 'Documentación'],
        label_visibility='collapsed'
    )
    
    # mostrar controles según la pestaña seleccionada
    if selected_tab == 'Mapa por país':
        st.sidebar.markdown('---')
        st.sidebar.header('controles')

        min_year = int(df_co2['year'].min())
        max_year = int(df_co2['year'].max())

        # años que usabas en el notebook como casos de estudio
        años_destacados = [1751, 1851, 1951, 2024]
        años_destacados = [a for a in años_destacados if min_year <= a <= max_year]

        preset = st.sidebar.selectbox(
            'años destacados',
            options=['ninguno'] + [str(a) for a in años_destacados],
            index=0
        )

        if preset != 'ninguno':
            year_default = int(preset)
        else:
            year_default = max_year

        year = st.sidebar.slider(
            'año',
            min_value=min_year,
            max_value=max_year,
            value=year_default,
            step=1
        )

        st.sidebar.markdown(
            """
            usa el slider para moverte año a año y el selector de
            años destacados para saltar rápidamente a hitos históricos.
            """
        )
    
    elif selected_tab == 'Evolución temporal':
        # calcular totales por año para los controles
        df_total_year = (
            df_co2.groupby('year', as_index=False)
            .agg({'co2': 'sum'})
            .rename(columns={'co2': 'co2_total'})
        )
        
        st.sidebar.markdown('---')
        st.sidebar.header('Controles de rango temporal')
        
        min_year_global = int(df_total_year['year'].min())
        max_year_global = int(df_total_year['year'].max())
        
        year_range = st.sidebar.slider(
            'Rango de años',
            min_value=min_year_global,
            max_value=max_year_global,
            value=(min_year_global, max_year_global),
            step=1,
            help='Selecciona el rango de años para visualizar en el gráfico'
        )
        
        st.sidebar.markdown('---')
        st.sidebar.header('Filtro de países')
        
        # obtener lista de países disponibles
        available_countries = sorted(df_co2['country'].unique())
        
        # checkbox para activar/desactivar filtro
        filter_countries = st.sidebar.checkbox(
            'Filtrar por países específicos',
            value=False,
            help='Activa para seleccionar países individuales'
        )
        
        if filter_countries:
            selected_countries = st.sidebar.multiselect(
                'Selecciona países',
                options=available_countries,
                default=['China', 'United States', 'India', 'Russia', 'Japan'],
                help='Puedes seleccionar múltiples países'
            )
        else:
            selected_countries = None
    
    elif selected_tab == 'Emisiones por tipo':
        # calcular emisiones por tipo para los controles
        df_emissions_ctrl = (
            df_fossil.groupby('year', as_index=False)
            .agg({
                'total': 'sum',
                'land_use_change': 'sum',
                'fossil_fuels': 'sum'
            })
        )
        
        years_ctrl = sorted(df_emissions_ctrl['year'].unique())
        
        st.sidebar.markdown('---')
        st.sidebar.header('Controles de año')
        
        year_selected = st.sidebar.slider(
            'Acumular hasta año',
            min_value=int(years_ctrl[0]),
            max_value=int(years_ctrl[-1]),
            value=2024 if 2024 in years_ctrl else int(years_ctrl[-1]),
            step=1,
            help='Selecciona hasta qué año se acumulan las emisiones'
        )
    
    elif selected_tab == 'Evolución por región':
        # calcular años disponibles para los controles
        years_regions = sorted(df_co2['year'].unique())
        
        st.sidebar.markdown('---')
        st.sidebar.header('Controles de rango temporal')
        
        year_range = st.sidebar.slider(
            'Rango de años',
            min_value=int(years_regions[0]),
            max_value=int(years_regions[-1]),
            value=(int(years_regions[0]), int(years_regions[-1])),
            step=1,
            help='Selecciona el rango de años para visualizar en el gráfico'
        )
        
        st.sidebar.markdown('---')
        st.sidebar.header('Filtro de países')
        
        # obtener lista de países disponibles
        available_countries_regions = sorted(df_co2['country'].unique())
        
        # checkbox para activar/desactivar filtro
        filter_countries_regions = st.sidebar.checkbox(
            'Filtrar por países específicos',
            value=False,
            help='Activa para seleccionar países individuales en lugar de top 10',
            key='filter_regions'
        )
        
        if filter_countries_regions:
            selected_countries_regions = st.sidebar.multiselect(
                'Selecciona países',
                options=available_countries_regions,
                default=['China', 'United States', 'India', 'Russia', 'Japan'],
                help='Puedes seleccionar múltiples países',
                key='multiselect_regions'
            )
        else:
            selected_countries_regions = None
    
    # renderizar contenido según la selección
    if selected_tab == 'Mapa por país':
        st.header("Emisiones de CO₂ por país")

        # generar mapa
        if year < min_year or year > max_year:
            st.warning(f'no hay datos para el año {year}. el rango válido es {min_year}–{max_year}.')
            return

        fig = make_co2_map(df_co2, world_master, geojson_world, year)
        st.plotly_chart(fig, use_container_width=True)

        # tabla resumen opcional
        st.markdown('---')
        st.subheader('tabla de emisiones por país en el año seleccionado')

        df_year = (
            df_co2[df_co2['year'] == year][['country', 'code', 'co2']]
            .groupby(['country', 'code'], as_index=False)
            .agg({'co2': 'sum'})
            .sort_values('co2', ascending=False)
        )

        st.dataframe(df_year, use_container_width=True)
    
    elif selected_tab == 'Evolución temporal':
        st.header("Evolución temporal de emisiones globales")
        
        if selected_countries and len(selected_countries) > 0:
            # modo: países seleccionados
            df_filtered = df_co2[df_co2['country'].isin(selected_countries)]
            df_filtered = df_filtered[
                (df_filtered['year'] >= year_range[0]) & 
                (df_filtered['year'] <= year_range[1])
            ]
            
            # agrupar por año y país
            df_by_country = df_filtered.groupby(['year', 'country'], as_index=False).agg({'co2': 'sum'})
            
            # crear gráfico de líneas múltiples
            fig_line = px.line(
                df_by_country,
                x='year',
                y='co2',
                color='country',
                title=f'Evolución de emisiones de CO₂ por país ({year_range[0]}-{year_range[1]})'
            )
            
            fig_line.update_traces(
                mode='lines+markers',
                line_width=2,
                marker=dict(size=4)
            )
            
            fig_line.update_layout(
                title_x=0.5,
                xaxis_title='Año',
                yaxis_title='Emisiones de CO₂ (toneladas)',
                hovermode='x unified',
                font=dict(
                    family='"Lato", "Arial", sans-serif',
                    size=12,
                    color='#333'
                ),
                title_font=dict(
                    size=16,
                    family='"Lato", "Arial", sans-serif'
                ),
                plot_bgcolor='#f8f9fa',
                legend=dict(
                    title='País',
                    orientation='v',
                    yanchor='top',
                    y=1,
                    xanchor='left',
                    x=1.02
                )
            )
            
            fig_line.update_xaxes(showgrid=False)
            fig_line.update_yaxes(
                showgrid=True,
                gridcolor='lightgray',
                griddash='dash',
                gridwidth=1
            )
            
            st.plotly_chart(fig_line, use_container_width=True)
            
            # tabla con datos por país
            st.markdown('---')
            st.subheader(f'Tabla de emisiones por país y año ({year_range[0]}-{year_range[1]})')
            
            df_display = df_by_country.copy()
            df_display = df_display.sort_values(['year', 'co2'], ascending=[False, False])
            df_display.columns = ['Año', 'País', 'Emisiones de CO₂']
            
            st.dataframe(df_display, use_container_width=True)
            
        else:
            # modo: global (todos los países agregados)
            df_total_year = (
                df_co2.groupby('year', as_index=False)
                .agg({'co2': 'sum'})
                .rename(columns={'co2': 'co2_total'})
            )
            
            # filtrar datos según el rango seleccionado
            df_total_year_filtered = df_total_year[
                (df_total_year['year'] >= year_range[0]) & 
                (df_total_year['year'] <= year_range[1])
            ]
            
            # crear gráfico de línea
            fig_line = px.line(
                df_total_year_filtered,
                x='year',
                y='co2_total',
                title=f'Evolución de emisiones de CO₂: Global ({year_range[0]}-{year_range[1]})'
            )
            
            fig_line.update_traces(
                mode='lines+markers',
                line_color='#3498DB',
                line_width=2,
                marker=dict(
                    size=4,
                    color='#3498DB',
                    symbol='circle'
                ),
                hovertemplate='<b>Año:</b> %{x}<br><b>CO₂:</b> %{y:,.0f} toneladas<extra></extra>'
            )
            
            fig_line.update_layout(
                title_x=0.5,
                xaxis_title='Año',
                yaxis_title='Emisiones totales de CO₂ (toneladas)',
                hovermode='x unified',
                font=dict(
                    family='"Lato", "Arial", sans-serif',
                    size=12,
                    color='#333'
                ),
                title_font=dict(
                    size=16,
                    family='"Lato", "Arial", sans-serif'
                ),
                plot_bgcolor='#f8f9fa'
            )
            
            fig_line.update_xaxes(
                showgrid=False,
                range=[df_total_year_filtered['year'].min(), df_total_year_filtered['year'].max()]
            )
            
            fig_line.update_yaxes(
                showgrid=True,
                gridcolor='lightgray',
                griddash='dash',
                gridwidth=1,
                range=[0, df_total_year_filtered['co2_total'].max() * 1.05]
            )
            
            st.plotly_chart(fig_line, use_container_width=True)
            
            # tabla resumen
            st.markdown('---')
            st.subheader(f'tabla de emisiones totales por año ({year_range[0]}-{year_range[1]})')
            
            df_total_year_display = df_total_year_filtered.copy()
            df_total_year_display = df_total_year_display.sort_values('year', ascending=False)
            df_total_year_display.columns = ['Año', 'Emisiones totales de CO₂']
            
            st.dataframe(df_total_year_display, use_container_width=True)
    
    elif selected_tab == 'Emisiones por tipo':
        st.header("Emisiones acumuladas por tipo")
        
        # calcular emisiones por tipo
        df_emissions = (
            df_fossil.groupby('year', as_index=False)
            .agg({
                'total': 'sum',
                'land_use_change': 'sum',
                'fossil_fuels': 'sum'
            })
        )
        
        # usar el año seleccionado del sidebar
        df_filtered = df_emissions[df_emissions['year'] <= year_selected]
        
        totals_filtered = {
            'Total (fossil fuels and land-use change)': df_filtered['total'].sum(),
            'Fossil fuels': df_filtered['fossil_fuels'].sum(),
            'Land-use change': df_filtered['land_use_change'].sum()
        }
        df_plot_filtered = pd.DataFrame(list(totals_filtered.items()), columns=['tipo', 'emisiones'])
        df_plot_filtered = df_plot_filtered.sort_values('emisiones', ascending=True)
        
        # asignar colores según el tipo
        colors = []
        for tipo in df_plot_filtered['tipo']:
            if 'Total' in tipo:
                colors.append('#E74C3C')
            elif 'Fossil' in tipo:
                colors.append('#3498DB')
            else:
                colors.append('#2ECC71')
        
        # crear gráfico sin animación
        fig_bar = go.Figure(
            data=[go.Bar(
                y=df_plot_filtered['tipo'],
                x=df_plot_filtered['emisiones'],
                orientation='h',
                marker=dict(color=colors)
            )]
        )
        
        fig_bar.update_layout(
            title=f'Emisiones acumuladas de CO₂ por tipo (hasta {year_selected})',
            title_x=0.5,
            showlegend=False,
            xaxis_title='Emisiones totales (toneladas)',
            yaxis_title='Tipo de emisión',
            height=600,
            font=dict(
                family='"Lato", "Arial", sans-serif',
                size=12,
                color='#333'
            ),
            title_font=dict(
                size=16,
                family='"Lato", "Arial", sans-serif'
            ),
            plot_bgcolor='#f8f9fa'
        )
        
        fig_bar.update_xaxes(
            showgrid=True,
            gridcolor='lightgray',
            griddash='dash',
            gridwidth=1,
            showline=False,
            zeroline=False
        )
        fig_bar.update_yaxes(
            showgrid=False,
            showline=False
        )
        
        st.plotly_chart(fig_bar, use_container_width=True)
        
        # tabla resumen
        st.markdown('---')
        st.subheader('tabla de emisiones por tipo y año')
        
        df_emissions_display = df_emissions.copy()
        df_emissions_display = df_emissions_display.sort_values('year', ascending=False)
        df_emissions_display.columns = ['Año', 'Total (fósiles + uso suelo)', 'Cambio uso suelo', 'Combustibles fósiles']
        
        st.dataframe(df_emissions_display, use_container_width=True)
    
    elif selected_tab == 'Evolución por región':
        st.header("Evolución de emisiones por región")
        
        # filtrar por rango de años del sidebar
        df_co2_filtered = df_co2[(df_co2['year'] >= year_range[0]) & (df_co2['year'] <= year_range[1])]
        
        # calcular porcentajes por país
        df_regions = df_co2_filtered.groupby(['year', 'country'], as_index=False).agg({'co2': 'sum'})
        df_regions['total_year'] = df_regions.groupby('year')['co2'].transform('sum')
        df_regions['percentage'] = (df_regions['co2'] / df_regions['total_year']) * 100
        
        # determinar qué países usar
        if selected_countries_regions and len(selected_countries_regions) > 0:
            # usar países seleccionados
            countries_to_plot = selected_countries_regions
            df_top = df_regions[df_regions['country'].isin(countries_to_plot)]
            title_suffix = f'(países seleccionados: {len(countries_to_plot)})'
        else:
            # usar top 10
            top_countries = df_regions.groupby('country')['co2'].sum().nlargest(10).index
            df_top = df_regions[df_regions['country'].isin(top_countries)]
            title_suffix = '(top 10 países)'
        
        df_pivot = df_top.pivot_table(
            index='year',
            columns='country',
            values='percentage',
            fill_value=0
        )
        
        fig_area = go.Figure()
        
        for country in df_pivot.columns:
            fig_area.add_trace(go.Scatter(
                x=df_pivot.index,
                y=df_pivot[country],
                name=country,
                mode='lines',
                stackgroup='one',
                groupnorm='percent',
                hovertemplate='<b>%{fullData.name}</b><br>' +
                              'Año: %{x}<br>' +
                              'Porcentaje: %{y:.1f}%<extra></extra>'
            ))
        
        fig_area.update_layout(
            title=f'Evolución de emisiones de CO₂ por región {title_suffix}',
            title_x=0.5,
            xaxis_title='Año',
            yaxis_title='Porcentaje de emisiones globales',
            hovermode='x unified',
            yaxis=dict(
                ticksuffix='%',
                range=[0, 100]
            ),
            legend=dict(
                orientation='v',
                yanchor='middle',
                y=0.5,
                xanchor='left',
                x=1.02
            ),
            height=600,
            font=dict(
                family='"Lato", "Arial", sans-serif',
                size=12,
                color='#333'
            ),
            title_font=dict(
                size=16,
                family='"Lato", "Arial", sans-serif'
            ),
            plot_bgcolor='#f8f9fa'
        )
        
        fig_area.update_xaxes(
            showgrid=False,
            range=[df_pivot.index.min(), df_pivot.index.max()]
        )
        
        fig_area.update_yaxes(
            showgrid=True,
            gridcolor='lightgray',
            griddash='dash',
            gridwidth=1,
            range=[0, 100]
        )
        
        st.plotly_chart(fig_area, use_container_width=True)
        
        # tabla resumen
        st.markdown('---')
        if selected_countries_regions and len(selected_countries_regions) > 0:
            st.subheader(f'Tabla de emisiones por país (países seleccionados)')
        else:
            st.subheader('Tabla de emisiones por país (top 10)')
        
        # filtrar top 10 y ordenar
        df_regions_table = df_top.copy()
        df_regions_table = df_regions_table.sort_values(['year', 'co2'], ascending=[False, False])
        
        df_regions_table = df_regions_table[['year', 'country', 'co2', 'percentage']].copy()
        df_regions_table.columns = ['Año', 'País', 'Emisiones de CO₂', 'Porcentaje del total (%)']
        df_regions_table['Porcentaje del total (%)'] = df_regions_table['Porcentaje del total (%)'].round(2)
        
        st.dataframe(df_regions_table, use_container_width=True)
    
    elif selected_tab == 'Documentación':
        st.header("📚 Documentación")
        
        # Introducción
        st.markdown("""
        Esta aplicación interactiva permite explorar y analizar las emisiones de CO₂ a nivel global 
        a través de múltiples visualizaciones y periodos temporales.
        """)
        
        # Datasets
        st.markdown("---")
        st.subheader("📊 Datasets utilizados")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **1. Annual CO₂ emissions per country**
            - **Fuente**: [Our World in Data](https://ourworldindata.org/co2-emissions)
            - **Periodo**: 1750 - 2024
            - **Unidad**: Toneladas de CO₂
            - **Cobertura**: ~200 países y territorios
            - **Variables**: País, código ISO3, año, emisiones totales
            """)
        
        with col2:
            st.markdown("""
            **2. CO₂ emissions from fossil fuels and land-use change**
            - **Fuente**: [Our World in Data](https://ourworldindata.org/co2-emissions)
            - **Periodo**: 1750 - 2024
            - **Unidad**: Toneladas de CO₂
            - **Variables**: Emisiones totales, combustibles fósiles, cambio de uso de suelo
            """)
        
        # Visualizaciones OWID
        st.markdown("---")
        st.subheader("🎨 Visualizaciones inspiradas en Our World in Data")
        
        st.markdown("""
        Esta aplicación recrea y adapta 4 visualizaciones clave de OWID:
        
        1. **Mapa coroplético por país**
           - Original: [Annual CO₂ emissions by region](https://ourworldindata.org/grapher/annual-co2-emissions-per-country)
           - Adaptación: Mapa interactivo con selector de año y países sin datos en gris
           
        2. **Evolución temporal**
           - Original: [Annual total CO₂ emissions](https://ourworldindata.org/grapher/annual-co2-emissions-per-country?country=~OWID_WRL)
           - Adaptación: Gráfico de línea con rangeslider y opción de filtrado por países
           
        3. **Emisiones por tipo**
           - Original: [Annual CO₂ emissions by source](https://ourworldindata.org/grapher/co2-fossil-plus-land-use)
           - Adaptación: Barras horizontales acumuladas con control de año mediante slider
           
        4. **Evolución por región**
           - Original: [Share of global CO₂ emissions](https://ourworldindata.org/grapher/annual-co-emissions-by-region)
           - Adaptación: Área apilada normalizada al 100% con selector de países
        """)
        
        # Decisiones de diseño
        st.markdown("---")
        st.subheader("🎯 Decisiones de diseño")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **1. Paleta de colores**
            - **Azul (#3498DB)**: Emisiones globales (neutralidad)
            - **Rojo (#E74C3C)**: Emisiones totales (alerta)
            - **Verde (#2ECC71)**: Cambio uso de suelo (naturaleza)
            - **Escala Reds**: Mapa coroplético (intensidad creciente)
            
            **Justificación**: Colores intuitivos que facilitan la interpretación 
            inmediata del tipo de dato y su gravedad.
            """)
        
        with col2:
            st.markdown("""
            **2. Escalas y ejes**
            - **Escala lineal**: Para emisiones absolutas (toneladas)
            - **Normalización al 100%**: Para comparación de participación regional
            - **Grillas sutiles**: Líneas grises discontinuas para referencia sin saturar
            
            **Justificación**: Facilita comparaciones cuantitativas precisas y 
            visualización de proporciones sin distorsión.
            """)
        
        # Limitaciones
        st.markdown("---")
        st.subheader("⚠️ Limitaciones y consideraciones")
        
        st.warning("""
        **Países sin datos**
        - Algunos países no tienen datos para todos los años, especialmente antes de 1900
        - Los países sin datos se muestran en gris en el mapa
        
        **Agregaciones**
        - Los totales globales pueden incluir estimaciones para países sin datos completos
        - Las sumas por tipo de emisión pueden no coincidir exactamente debido a redondeos
        
        **Periodicidad**
        - Los datos más recientes (2023-2024) pueden estar sujetos a revisiones
        - Algunos países reportan con retraso, afectando la completitud de años recientes
        """)
        
        # Metodología
        st.markdown("---")
        st.subheader("🔬 Metodología técnica")
        
        st.markdown("""
        **Herramientas utilizadas:**
        - **Streamlit**: Framework web interactivo
        - **Plotly**: Visualizaciones interactivas
        - **GeoPandas**: Procesamiento de datos geoespaciales
        - **Pandas**: Manipulación y análisis de datos
        
        **Procesamiento de datos:**
        1. Carga de shapefiles Natural Earth (50m resolution)
        2. Estandarización de códigos ISO3 para unión de datos
        3. Agregación temporal y espacial según visualización
        4. Cálculo de porcentajes y normalizaciones
        
        **Optimizaciones:**
        - Cache de datos con `@st.cache_data`
        - Filtrado dinámico según controles del usuario
        - Renderizado condicional de visualizaciones
        """)
        
        # Fuentes y referencias
        st.markdown("---")
        st.subheader("📖 Fuentes y referencias")
        
        st.markdown("""
        - [Our World in Data - CO₂ and Greenhouse Gas Emissions](https://ourworldindata.org/co2-emissions)
        - [Natural Earth - Country Boundaries](https://www.naturalearthdata.com/)
        - [Global Carbon Project](https://www.globalcarbonproject.org/)
        - [Plotly Documentation](https://plotly.com/python/)
        - [Streamlit Documentation](https://docs.streamlit.io/)
        """)
        
        # Uso de IA
        st.markdown("---")
        st.info("""
        **📝 Declaración de uso de IA**
        
        Esta aplicación fue desarrollada con asistencia de GitHub Copilot para:
        - Generación de código base de Streamlit y Plotly
        - Optimización de queries de pandas y geopandas
        - Estructuración de layout y componentes interactivos
        - Documentación y comentarios en código
        
        Todo el código fue revisado, adaptado y probado manualmente para asegurar 
        su correcta funcionalidad y alineación con los requisitos del proyecto.
        """)


if __name__ == '__main__':
    main()
