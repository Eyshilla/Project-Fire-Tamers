import streamlit as st
import pandas as pd
import plotly.express as px

# Configuração inicial da página
st.set_page_config(page_title="NASA PSI-159 | Chamas Frias", layout="wide")

# Função para carregar os dados otimizada e em cache
@st.cache_data
def carregar_dados():
    # Lê o arquivo unificado que você criou (precisa estar na mesma pasta no GitHub)
    df = pd.read_csv("psi159_unificado.csv", on_bad_lines='skip')
    
    # Limpeza básica: remove espaços invisíveis nos cabeçalhos
    df.columns = df.columns.str.strip()
    
    # Força a conversão das colunas principais para números, ignorando erros/textos
    if 'Peak burner T (C )' in df.columns:
        df['Peak burner T (C )'] = pd.to_numeric(df['Peak burner T (C )'], errors='coerce')
    if 'approx p (bar)' in df.columns:
        df['approx p (bar)'] = pd.to_numeric(df['approx p (bar)'], errors='coerce')
        
    # Remove linhas onde as métricas principais estão vazias
    df = df.dropna(subset=['Peak burner T (C )', 'approx p (bar)', 'Fuel'])
    
    # Padroniza a coluna 'Cool flame?' para ficar visualmente limpa no gráfico
    if 'Cool flame?' in df.columns:
        df['Cool flame?'] = df['Cool flame?'].astype(str).str.strip().str.title()
        
    return df

df = carregar_dados()

# --- BARRA LATERAL (Painel de Controle) ---
st.sidebar.image("https://www.nasa.gov/wp-content/themes/nasa/assets/images/nasa-logo.svg", width=150)
st.sidebar.title("Parâmetros da Missão")

# Filtros dinâmicos com base nos dados reais do arquivo
combustivel = st.sidebar.selectbox("Selecione o Combustível (Fuel):", sorted(df['Fuel'].unique()))
df_filtrado = df[df['Fuel'] == combustivel]

st.sidebar.markdown("---")
st.sidebar.markdown("**Simulador de Ambiente**")
pressao_min = float(df['approx p (bar)'].min())
pressao_max = float(df['approx p (bar)'].max())
pressao_selecionada = st.sidebar.slider(
    "Pressão Aprox. (bar):", 
    pressao_min, pressao_max, 
    (pressao_min, pressao_max)
)

df_filtrado = df_filtrado[df_filtrado['approx p (bar)'].between(pressao_selecionada[0], pressao_selecionada[1])]

# --- ÁREA PRINCIPAL (Tabs/Abas) ---
st.title("🔥 Fogo Invisível: Explorando o PSI-159")
st.markdown("Dashboard interativo explorando as descobertas do experimento *Cool Flames Investigation with Gases* na ISS.")

tab1, tab2, tab3 = st.tabs(["O Fenômeno (Ensino Médio)", "Análise de Dados (Universitário)", "Impacto na Terra 🌍"])

# ABA 1: CONTEXTO
with tab1:
    st.header("O que é uma Chama Fria?")
    st.write("Na Terra, o fogo queima a temperaturas altíssimas e sobe em formato de chama. Na microgravidade da Estação Espacial Internacional, cientistas descobriram que certos gases queimam de forma esférica, quase invisível, e em temperaturas incrivelmente baixas.")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="Temp. Chama Normal (Terra)", value="~1500 °C")
    with col2:
        # Calcula a média das chamas frias ("Yes") daquele combustível
        df_cool = df_filtrado[df_filtrado['Cool flame?'] == 'Yes']
        if not df_cool.empty:
            temp_media = df_cool['Peak burner T (C )'].mean()
            st.metric(label="Temp. Média Chama Fria (ISS)", value=f"{temp_media:.0f} °C", delta="Mínima térmica alcançada")
        else:
            st.metric(label="Temp. Média Chama Fria (ISS)", value="Sem dados", delta="Ajuste os filtros")

# ABA 2: DADOS E GRÁFICOS
with tab2:
    st.header("Mapeamento Térmico vs Pressão")
    st.write("Analise em quais pressões e condições a chama fria se sustenta no espaço.")
    
    if not df_filtrado.empty:
        # Gráfico de Dispersão (Scatter) usando Plotly Express
        fig = px.scatter(
            df_filtrado, 
            x='approx p (bar)', 
            y='Peak burner T (C )', 
            color='Cool flame?', 
            hover_data=['Test', 'burn time (sec)'],
            color_discrete_map={'Yes': '#00BFFF', 'No': '#FF4500'},
            labels={
                "approx p (bar)": "Pressão da Câmara (bar)",
                "Peak burner T (C )": "Temperatura de Pico (°C)",
                "Cool flame?": "É Chama Fria?"
            }
        )
        fig.update_layout(template="plotly_dark") # Deixa o gráfico com visual moderno/espacial
        st.plotly_chart(fig, use_container_width=True)
        
        with st.expander("Tabela de Dados Filtrados"):
            st.dataframe(df_filtrado, use_container_width=True)
    else:
        st.warning("Nenhuma ignição registrada para esta combinação de filtros.")

# ABA 3: IMPACTO E SPIN-OFFS
with tab3:
    st.header("Aplicações das 'Cool Flames' na Terra")
    
    st.markdown("### 🚗 Motores 60% Mais Eficientes")
    st.write("Hoje, motores a combustão tradicionais operam com apenas 38% de eficiência, perdendo energia na forma de calor extremo. Compreender a estabilidade química da queima em baixas temperaturas (chama fria) permitirá o desenvolvimento de motores com combustão *ultra-pobre* (ultra-lean), capazes de atingir quase 60% de eficiência e reduzir drasticamente a emissão de poluentes.")
    
    st.markdown("### 🧯 Sistemas Avançados de Extinção")
    st.write("Estudar como materiais param de queimar (limite de inflamabilidade) no limite exato entre a chama quente e a fria fornece aos engenheiros de segurança na Terra os modelos matemáticos necessários para criar sistemas de supressão de incêndio que extinguem o fogo sem causar danos colaterais ou usar excesso de água.")
