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

    # tabs para diferentes visualizaciones
    tab1, tab2, tab3, tab4 = st.tabs([
        "Mapa por país", 
        "Gráfico de línea temporal",
        "Emisiones por tipo",
        "Evolución por región"
    ])
    
    with tab1:
        st.header("Emisiones de CO₂ por país")
        
        # panel lateral de control
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
    
    with tab2:
        st.header("Evolución temporal de emisiones globales")
        
        # calcular totales por año
        df_total_year = (
            df_co2.groupby('year', as_index=False)
            .agg({'co2': 'sum'})
            .rename(columns={'co2': 'co2_total'})
        )
        
        # crear gráfico de línea
        fig_line = px.line(
            df_total_year,
            x='year',
            y='co2_total',
            title='Evolución de emisiones de CO₂: Global'
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
            rangeslider_visible=True,
            rangeslider_thickness=0.05,
            range=[df_total_year['year'].min(), df_total_year['year'].max()]
        )
        
        fig_line.update_yaxes(
            showgrid=True,
            gridcolor='lightgray',
            griddash='dash',
            gridwidth=1,
            range=[0, df_total_year['co2_total'].max() * 1.05]
        )
        
        st.plotly_chart(fig_line, use_container_width=True)
    
    with tab3:
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
        
        years = sorted(df_emissions['year'].unique())
        year_initial = 2024 if 2024 in years else years[-1]
        
        df_initial = df_emissions[df_emissions['year'] <= year_initial]
        
        totals_initial = {
            'Total (fossil fuels and land-use change)': df_initial['total'].sum(),
            'Fossil fuels': df_initial['fossil_fuels'].sum(),
            'Land-use change': df_initial['land_use_change'].sum()
        }
        df_plot_initial = pd.DataFrame(list(totals_initial.items()), columns=['tipo', 'emisiones'])
        df_plot_initial = df_plot_initial.sort_values('emisiones', ascending=True)
        
        fig_bar = go.Figure(
            data=[go.Bar(
                y=df_plot_initial['tipo'],
                x=df_plot_initial['emisiones'],
                orientation='h',
                marker=dict(color=['#E74C3C', '#3498DB', '#2ECC71'])
            )]
        )
        
        frames = []
        for year_frame in years:
            df_range = df_emissions[df_emissions['year'] <= year_frame]
            
            totals = {
                'Total (fossil fuels and land-use change)': df_range['total'].sum(),
                'Fossil fuels': df_range['fossil_fuels'].sum(),
                'Land-use change': df_range['land_use_change'].sum()
            }
            
            df_plot = pd.DataFrame(list(totals.items()), columns=['tipo', 'emisiones'])
            df_plot = df_plot.sort_values('emisiones', ascending=True)
            
            colors = []
            for tipo in df_plot['tipo']:
                if 'Total' in tipo:
                    colors.append('#E74C3C')
                elif 'Fossil' in tipo:
                    colors.append('#3498DB')
                else:
                    colors.append('#2ECC71')
            
            frames.append(go.Frame(
                data=[go.Bar(
                    y=df_plot['tipo'],
                    x=df_plot['emisiones'],
                    orientation='h',
                    marker=dict(color=colors)
                )],
                name=str(year_frame)
            ))
        
        fig_bar.frames = frames
        
        active_index = years.index(year_initial)
        
        steps = []
        for i, year_step in enumerate(years):
            steps.append({
                'args': [
                    [str(year_step)],
                    {
                        'frame': {'duration': 300, 'redraw': True},
                        'mode': 'immediate',
                        'transition': {'duration': 300}
                    }
                ],
                'label': str(year_step),
                'method': 'animate'
            })
        
        fig_bar.update_layout(
            title='Emisiones acumuladas de CO₂ por tipo',
            title_x=0.5,
            showlegend=False,
            xaxis_title='Emisiones totales (toneladas)',
            yaxis_title='Tipo de emisión',
            sliders=[{
                'active': active_index,
                'yanchor': 'top',
                'y': 0,
                'xanchor': 'left',
                'currentvalue': {
                    'prefix': 'Hasta año: ',
                    'visible': True,
                    'xanchor': 'right'
                },
                'steps': steps
            }],
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
        
        fig_bar.update_xaxes(showgrid=True)
        fig_bar.update_yaxes(showgrid=False)
        
        st.plotly_chart(fig_bar, use_container_width=True)
    
    with tab4:
        st.header("Evolución de emisiones por región")
        
        # calcular porcentajes por país
        df_regions = df_co2.groupby(['year', 'country'], as_index=False).agg({'co2': 'sum'})
        df_regions['total_year'] = df_regions.groupby('year')['co2'].transform('sum')
        df_regions['percentage'] = (df_regions['co2'] / df_regions['total_year']) * 100
        
        # top 10 países
        top_countries = df_regions.groupby('country')['co2'].sum().nlargest(10).index
        df_top = df_regions[df_regions['country'].isin(top_countries)]
        
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
            title='Evolución de emisiones de CO₂ por región (% del total)',
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
            rangeslider_visible=True,
            rangeslider_thickness=0.05,
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


if __name__ == '__main__':
    main()
