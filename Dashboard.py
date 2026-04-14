import streamlit as st
import requests
import pandas as pd
import plotly.express as px

# 1. Configurações da Página
st.set_page_config(
    page_title="Dashboard Executivo de Vendas",
    page_icon="📈",
    layout='wide',
    initial_sidebar_state="expanded"
)

# 2. Funções Auxiliares e Cache
@st.cache_data(ttl=600)
def carregar_dados(regiao: str, ano: int | str) -> pd.DataFrame:
    url = "https://labdados.com/produtos"
    query_string = {}
    if regiao and regiao != 'Brasil':
         query_string['regiao'] = regiao.lower()
    if ano:
         query_string['ano'] = ano
    
    try:
        response = requests.get(url, params=query_string)
        response.raise_for_status()
        df = pd.DataFrame.from_dict(response.json())
        df['Data da Compra'] = pd.to_datetime(df['Data da Compra'], format='%d/%m/%Y')
        return df
    except requests.exceptions.RequestException:
        st.error("Falha na comunicação com a API.")
        return pd.DataFrame()

def formata_numero(valor: float, prefixo: str = '') -> str:
    for unidade in ['', 'mil', 'mi']:
        if valor < 1000:
            return f'{prefixo} {valor:.2f} {unidade}'.strip()
        valor /= 1000
    return f'{prefixo} {valor:.2f} bi'.strip()

def padronizar_layout_grafico(fig):
    fig.update_layout(
        template="plotly_dark",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=20, r=20, t=50, b=20),
        xaxis=dict(showgrid=False, zeroline=False),
        yaxis=dict(showgrid=True, gridcolor="#333333", zeroline=False),
        font=dict(color="#FAFAFA")
    )
    return fig

# 3. Interface e Filtros (Sidebar)
st.sidebar.markdown("### Filtros Globais")

regioes = ['Brasil', 'Centro-Oeste', 'Nordeste', 'Norte', 'Sudeste', 'Sul']
regiao_selecionada = st.sidebar.selectbox('Região', regioes)

todos_anos = st.sidebar.checkbox('Todo o período', value=True)
ano_selecionado = '' if todos_anos else st.sidebar.slider('Ano', 2020, 2023)

# 4. Extração e Tratamento de Dados
dados = carregar_dados(regiao_selecionada, ano_selecionado)

if dados.empty:
    st.warning("Sem dados para os filtros aplicados.")
    st.stop()

vendedores_disponiveis = sorted(dados['Vendedor'].unique())
filtro_vendedores = st.sidebar.multiselect("Vendedores", vendedores_disponiveis)
if filtro_vendedores:
    dados = dados[dados['Vendedor'].isin(filtro_vendedores)]

df_locais = dados[['Local da compra', 'lat', 'lon']].drop_duplicates('Local da compra')

# Tabelas Agrupadas
receita_estados = dados.groupby("Local da compra", as_index=False)['Preço'].sum()
receita_estados = receita_estados.merge(df_locais, on='Local da compra').sort_values('Preço', ascending=False)

receita_mensal = dados.set_index('Data da Compra').groupby(pd.Grouper(freq='ME'))['Preço'].sum().reset_index()
receita_mensal['Ano'] = receita_mensal['Data da Compra'].dt.year
receita_mensal['Mes'] = receita_mensal['Data da Compra'].dt.strftime('%b')

receita_categorias = dados.groupby('Categoria do Produto', as_index=False)['Preço'].sum().sort_values('Preço', ascending=False)

vendas_estados = dados.groupby('Local da compra', as_index=False)['Preço'].count().rename(columns={'Preço': 'Quantidade'})
vendas_estados = vendas_estados.merge(df_locais, on='Local da compra').sort_values('Quantidade', ascending=False)

vendas_mensal = dados.set_index('Data da Compra').groupby(pd.Grouper(freq='ME'))['Preço'].count().reset_index().rename(columns={'Preço': 'Quantidade'})
vendas_mensal['Ano'] = vendas_mensal['Data da Compra'].dt.year
vendas_mensal['Mes'] = vendas_mensal['Data da Compra'].dt.strftime('%b')

vendas_categorias = dados.groupby('Categoria do Produto', as_index=False)['Preço'].count().rename(columns={'Preço': 'Quantidade'}).sort_values('Quantidade', ascending=False)

# CORREÇÃO APLICADA AQUI
vendedores = dados.groupby('Vendedor').agg(Receita=('Preço', 'sum'), Quantidade=('Preço', 'count')).reset_index()

# 5. Construção dos Gráficos
cor_primaria = "#00D2D3"
cor_secundaria = "#556DE8"

fig_mapa_receita = px.scatter_geo(receita_estados, lat='lat', lon='lon', scope='south america', size='Preço', template='plotly_dark', hover_name='Local da compra', hover_data={'lat': False, 'lon': False}, title='Receita por Estado', color_discrete_sequence=[cor_primaria])
fig_mapa_receita.update_geos(bgcolor="rgba(0,0,0,0)", showcountries=True, countrycolor="#333333", showland=True, landcolor="#1E1E1E")
fig_mapa_receita.update_layout(margin=dict(l=0, r=0, t=40, b=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")

fig_receita_mensal = padronizar_layout_grafico(
    px.line(receita_mensal, x='Mes', y='Preço', markers=True, color='Ano', line_dash='Ano', title='Evolução da Receita Mensal')
).update_layout(yaxis_title='', xaxis_title='')

fig_receita_estados = padronizar_layout_grafico(
    px.bar(receita_estados.head(5), x='Local da compra', y='Preço', text_auto='.2s', title='Top 5 Estados (Receita)', color_discrete_sequence=[cor_primaria])
).update_layout(yaxis_title='', xaxis_title='')

fig_receita_categorias = padronizar_layout_grafico(
    px.bar(receita_categorias, x='Preço', y='Categoria do Produto', orientation='h', text_auto='.2s', title='Receita por Categoria', color_discrete_sequence=[cor_primaria])
).update_layout(yaxis={'categoryorder': 'total ascending'}, yaxis_title='', xaxis_title='')

fig_mapa_vendas = px.scatter_geo(vendas_estados, lat='lat', lon='lon', scope='south america', size='Quantidade', template='plotly_dark', hover_name='Local da compra', hover_data={'lat': False, 'lon': False}, title='Volume de Vendas por Estado', color_discrete_sequence=[cor_secundaria])
fig_mapa_vendas.update_geos(bgcolor="rgba(0,0,0,0)", showcountries=True, countrycolor="#333333", showland=True, landcolor="#1E1E1E")
fig_mapa_vendas.update_layout(margin=dict(l=0, r=0, t=40, b=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")

fig_vendas_mensal = padronizar_layout_grafico(
    px.line(vendas_mensal, x='Mes', y='Quantidade', markers=True, color='Ano', line_dash='Ano', title='Evolução do Volume de Vendas')
).update_layout(yaxis_title='', xaxis_title='')

fig_vendas_estados = padronizar_layout_grafico(
    px.bar(vendas_estados.head(5), x='Local da compra', y='Quantidade', text_auto=True, title='Top 5 Estados (Volume)', color_discrete_sequence=[cor_secundaria])
).update_layout(yaxis_title='', xaxis_title='')

fig_vendas_categorias = padronizar_layout_grafico(
    px.bar(vendas_categorias, x='Quantidade', y='Categoria do Produto', orientation='h', text_auto=True, title='Volume por Categoria', color_discrete_sequence=[cor_secundaria])
).update_layout(yaxis={'categoryorder': 'total ascending'}, yaxis_title='', xaxis_title='')

# 6. Renderização da UI (Main)
st.title("DASHBOARD DE VENDAS")

# Resumo Executivo (KPIs Globais)
st.markdown("### Resumo Executivo")
kpi1, kpi2, kpi3 = st.columns(3)
kpi1.metric("Receita Total", formata_numero(dados['Preço'].sum(), 'R$'))
kpi2.metric("Volume de Vendas", formata_numero(dados.shape[0]))
kpi3.metric("Ticket Médio", formata_numero(dados['Preço'].sum() / dados.shape[0], 'R$'))

st.markdown("---")

# Abas de Análise Detalhada
aba1, aba2, aba3 = st.tabs(["Visão de Receita", "Visão de Volume", "Análise de Vendedores"])

with aba1:
    col1, col2 = st.columns(2, gap="large")
    with col1:
        st.plotly_chart(fig_mapa_receita, use_container_width=True)
        st.plotly_chart(fig_receita_estados, use_container_width=True)
    with col2:
        st.plotly_chart(fig_receita_mensal, use_container_width=True)
        st.plotly_chart(fig_receita_categorias, use_container_width=True)

with aba2:
    col1, col2 = st.columns(2, gap="large")
    with col1:
        st.plotly_chart(fig_mapa_vendas, use_container_width=True)
        st.plotly_chart(fig_vendas_estados, use_container_width=True)
    with col2:
        st.plotly_chart(fig_vendas_mensal, use_container_width=True)
        st.plotly_chart(fig_vendas_categorias, use_container_width=True)

with aba3:
    qtd_vendedores = st.slider('Top N Vendedores para Análise', min_value=2, max_value=20, value=5)
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2, gap="large")
    with col1:
        top_receita = vendedores.sort_values('Receita', ascending=False).head(qtd_vendedores)
        fig_rec_vend = padronizar_layout_grafico(
            px.bar(top_receita, x='Receita', y='Vendedor', orientation='h', text_auto='.2s', title=f'Top {qtd_vendedores} em Receita', color_discrete_sequence=[cor_primaria])
        ).update_layout(yaxis={'categoryorder': 'total ascending'}, yaxis_title="", xaxis_title="")
        st.plotly_chart(fig_rec_vend, use_container_width=True)
        
    with col2:
        top_qtd = vendedores.sort_values('Quantidade', ascending=False).head(qtd_vendedores)
        fig_qtd_vend = padronizar_layout_grafico(
            px.bar(top_qtd, x='Quantidade', y='Vendedor', orientation='h', text_auto=True, title=f'Top {qtd_vendedores} em Volume', color_discrete_sequence=[cor_secundaria])
        ).update_layout(yaxis={'categoryorder': 'total ascending'}, yaxis_title="", xaxis_title="")
        st.plotly_chart(fig_qtd_vend, use_container_width=True)