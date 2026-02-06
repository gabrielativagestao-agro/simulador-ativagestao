import streamlit as st
import pandas as pd
import plotly.express as px

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="AtivaGestão | Simulador",
    page_icon="🐂",
    layout="wide"
)

# --- CABEÇALHO ---
st.title("🐂 AtivaGestão | Simulador de Lucro")
st.markdown("---")

# --- BARRA LATERAL (INPUTS) ---
with st.sidebar:
    st.header("📝 Dados do Lote")
    
    qtd_animais = st.number_input("Qtd de Animais", min_value=1, value=50)
    peso_entrada = st.number_input("Peso de Entrada (kg)", value=300.0)
    
    st.subheader("💰 Mercado")
    valor_arroba_compra = st.number_input("Valor @ Compra (R$)", value=280.00)
    valor_arroba_venda = st.number_input("Valor @ Venda (R$)", value=310.00)
    
    st.subheader("🍽️ Nutrição & Tempo")
    custo_dieta = st.number_input("Custo Dieta (R$/cab/dia)", value=12.50)
    dias_cocho = st.number_input("Dias de Cocho", value=90)
    gmd_esperado = st.number_input("GMD Esperado (kg/dia)", value=1.500, format="%.3f")

# --- CÁLCULOS (A MÁGICA) ---
# 1. Peso Final
peso_final = peso_entrada + (gmd_esperado * dias_cocho)
peso_final_arrobas = peso_final / 30

# 2. Custos
custo_boi_magro = (peso_entrada / 30) * valor_arroba_compra * qtd_animais
custo_alimentar = custo_dieta * dias_cocho * qtd_animais
custo_operacional = 0 # Pode adicionar depois se quiser
custo_total = custo_boi_magro + custo_alimentar + custo_operacional

# 3. Receita
receita_bruta = peso_final_arrobas * valor_arroba_venda * qtd_animais

# 4. Indicadores
lucro_total = receita_bruta - custo_total
lucro_por_cabeca = lucro_total / qtd_animais
roi = (lucro_total / custo_total) * 100

# --- EXIBIÇÃO DO DASHBOARD ---

# Linha de Métricas (KPIs)
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(label="Peso Final (Médio)", value=f"{peso_final:.1f} kg", delta=f"{peso_final_arrobas:.1f} @")

with col2:
    st.metric(label="Custo Total do Lote", value=f"R$ {custo_total:,.2f}")

with col3:
    st.metric(label="Receita Bruta", value=f"R$ {receita_bruta:,.2f}")

with col4:
    # Cor condicional para o lucro
    st.metric(label="Lucro Projetado 💰", value=f"R$ {lucro_total:,.2f}", delta=f"{roi:.1f}% ROI")

st.markdown("---")

# --- GRÁFICOS E ANÁLISE ---
col_grafico, col_texto = st.columns([2, 1])

with col_grafico:
    st.subheader("📊 Raio-X Financeiro")
    
    # Montando dados para o gráfico
    dados_grafico = pd.DataFrame({
        "Categoria": ["Investimento (Custos)", "Retorno (Receita)"],
        "Valor": [custo_total, receita_bruta],
        "Cor": ["#B22222", "#2E8B57"] # Vermelho e Verde
    })
    
    fig = px.bar(dados_grafico, x="Categoria", y="Valor", text_auto='.2s', 
                 color="Categoria", color_discrete_sequence=["#ef5350", "#66bb6a"])
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

with col_texto:
    st.subheader("📋 Relatório Rápido")
    st.info(f"""
    **Resumo da Estratégia:**
    
    Para lucrar **R$ {lucro_por_cabeca:,.2f}** por cabeça, precisamos que o gado ganhe **{gmd_esperado}kg/dia** durante **{dias_cocho} dias**.
    
    O ponto de equilíbrio (Break-even) é vender a arroba por, no mínimo, **R$ {(custo_total/qtd_animais)/(peso_final/30):.2f}**.
    
    Abaixo disso, temos prejuízo.
    """)
    
    if lucro_total > 0:
        st.success("✅ Cenário VIÁVEL e LUCRATIVO.")
    else:
        st.error("🚨 Cenário de PREJUÍZO. Revise custos ou preço de venda.")

# Rodapé
st.markdown("---")
st.caption("Desenvolvido por **Gabriel Oliveira | AtivaGestão** - Tecnologia Zootécnica")
