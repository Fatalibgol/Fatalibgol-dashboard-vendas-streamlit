import streamlit as st
import pandas as pd
import plotly.express as px

# --- Configuração da Página ---
st.set_page_config(layout="wide")

# --- Título do Dashboard ---
st.title('Dashboard de Vendas Olist 📊')

# --- Carregando os Dados ---
@st.cache_data
def carregar_dados():
    df = pd.read_csv('olist_orders_dataset.csv')
    df_clientes = pd.read_csv('olist_customers_dataset.csv')
    df = pd.merge(df, df_clientes, on='customer_id')
    df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])
    return df

df_completo = carregar_dados()

# --- BARRA LATERAL (Sidebar) ---
st.sidebar.header('Filtros Interativos')

# Filtro 1: Seleção de Múltiplos Estados
lista_estados = sorted(df_completo['customer_state'].unique())
lista_estados.insert(0, 'Todos')
estados_selecionados = st.sidebar.multiselect('Selecione o Estado', lista_estados, default=['Todos'])

# Filtro 2: Seleção de Período
data_minima = df_completo['order_purchase_timestamp'].min().date()
data_maxima = df_completo['order_purchase_timestamp'].max().date()
data_inicio = st.sidebar.date_input('Data Início', value=data_minima, min_value=data_minima, max_value=data_maxima)
data_fim = st.sidebar.date_input('Data Fim', value=data_maxima, min_value=data_minima, max_value=data_maxima)

# --- Lógica de Filtragem ---
data_inicio_ts = pd.to_datetime(data_inicio)
data_fim_ts = pd.to_datetime(data_fim)

if 'Todos' not in estados_selecionados:
    df_filtrado = df_completo[df_completo['customer_state'].isin(estados_selecionados)]
else:
    df_filtrado = df_completo

df_filtrado = df_filtrado[(df_filtrado['order_purchase_timestamp'] >= data_inicio_ts) & 
                          (df_filtrado['order_purchase_timestamp'] <= data_fim_ts)]

# --- PÁGINA PRINCIPAL ---

# Separador
st.markdown("---")

# ## SEÇÃO NOVA: KPIs (Métricas Chave) ##
st.header('Métricas Principais')

# Criando 2 colunas para exibir os KPIs lado a lado
col1, col2 = st.columns(2)

# KPI 1: Total de Pedidos
total_pedidos = df_filtrado.shape[0]
col1.metric("Total de Pedidos", value=total_pedidos)

# KPI 2: Total de Clientes Únicos
total_clientes = df_filtrado['customer_unique_id'].nunique()
col2.metric("Total de Clientes Únicos", value=total_clientes)

# Separador
st.markdown("---")

# --- GRÁFICOS ---
st.header('Análises Visuais')

# Gráfico 1: Pedidos por Estado
contagem_estados = df_filtrado['customer_state'].value_counts().reset_index()
contagem_estados.columns = ['Estado', 'Contagem de Pedidos']
fig_pedidos_estado = px.bar(
    contagem_estados, x='Contagem de Pedidos', y='Estado', orientation='h',
    title='Número de Pedidos por Estado', text='Contagem de Pedidos'
)
fig_pedidos_estado.update_layout(yaxis={'categoryorder': 'total ascending'})
st.plotly_chart(fig_pedidos_estado, use_container_width=True)


# ## SEÇÃO NOVA: Gráfico de Vendas ao Longo do Tempo ##

# 1. Preparar os dados para o gráfico de linha
# Agrupamos os pedidos por mês e contamos a quantidade
vendas_mensais = df_filtrado.set_index('order_purchase_timestamp').resample('M').agg({'order_id': 'count'}).reset_index()
vendas_mensais.columns = ['Mês', 'Quantidade de Pedidos']

# 2. Criar o gráfico de linha
fig_vendas_mensais = px.line(
    vendas_mensais,
    x='Mês',
    y='Quantidade de Pedidos',
    title='Vendas Mensais ao Longo do Tempo',
    labels={'Mês': 'Mês da Compra', 'Quantidade de Pedidos': 'Total de Pedidos'}
)

# 3. Exibir o gráfico
st.plotly_chart(fig_vendas_mensais, use_container_width=True)