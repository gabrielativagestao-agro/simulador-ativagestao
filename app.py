import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="AtivaGestão | Simulador", page_icon="🐂", layout="wide")

# --- CLASSE DO PDF (LAYOUT) ---
class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, 'AtivaGestao - Laudo Tecnico de Viabilidade', 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, 'Gabriel Oliveira | Consultoria Zootecnica e Gestao de Dados', 0, 0, 'C')

def gerar_pdf(dados, resultados, conclusao):
    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    # Função para limpar texto (remove emojis e caracteres especiais para o PDF)
    def limpar(t):
        t = t.replace("✅", "[APROVADO]").replace("🚨", "[ALERTA CRITICO]").replace("💰", "")
        t = t.replace("🐂", "").replace("📊", "").replace("📉", "")
        return t.encode('latin-1', 'replace').decode('latin-1')

    pdf.cell(0, 10, limpar(f"Data da Emissão: {datetime.now().strftime('%d/%m/%Y')}"), 0, 1)
    pdf.ln(5)
    
    # Bloco 1: Parâmetros
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, limpar("1. Parâmetros Zootécnicos do Lote"), 0, 1)
    pdf.set_font("Arial", size=12)
    for k, v in dados.items():
        pdf.cell(0, 8, limpar(f"- {k}: {v}"), 0, 1)
    
    pdf.ln(5)
    
    # Bloco 2: Financeiro
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, limpar("2. Projeção Financeira"), 0, 1)
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 8, limpar(f"Custo Total de Produção: R$ {resultados['Custo']}"), 0, 1)
    pdf.cell(0, 8, limpar(f"Receita Bruta Estimada: R$ {resultados['Receita']}"), 0, 1)
    
    # Destaque do Lucro
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 8, limpar(f"MARGEM LÍQUIDA PROJETADA: R$ {resultados['Lucro']}"), 0, 1)
    pdf.cell(0, 8, limpar(f"ROI (Retorno sobre Capital): {resultados['ROI']}"), 0, 1)
    
    pdf.ln(10)
    
    # Bloco 3: Parecer (Onde brilha o Zootecnista)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, limpar("3. Parecer Técnico Especializado"), 0, 1)
    pdf.set_font("Arial", size=11)
    pdf.multi_cell(0, 8, limpar(conclusao))
    
    return pdf.output(dest='S').encode('latin-1')

# --- APP VISUAL (INTERFACE) ---
st.title("🐂 AtivaGestão | Inteligência Zootécnica")
st.markdown("---")

with st.sidebar:
    st.header("📝 Parâmetros de Entrada")
    qtd_animais = st.number_input("Qtd de Animais", min_value=1, value=50)
    peso_entrada = st.number_input("Peso de Entrada (kg)", value=300.0)
    
    st.subheader("💰 Cenário de Mercado")
    valor_arroba_compra = st.number_input("Valor @ Compra (R$)", value=280.00)
    valor_arroba_venda = st.number_input("Valor @ Venda (R$)", value=310.00)
    
    st.subheader("🧬 Eficiência & Nutrição")
    custo_dieta = st.number_input("Custo Dieta (R$/cab/dia)", value=12.50)
    dias_cocho = st.number_input("Dias de Trato (Confinamento)", value=90)
    gmd_esperado = st.number_input("GMD Meta (kg/dia)", value=1.500, format="%.3f")

# --- CÁLCULOS TÉCNICOS ---
peso_final = peso_entrada + (gmd_esperado * dias_cocho)
peso_final_arrobas = peso_final / 30
custo_total = ((peso_entrada / 30) * valor_arroba_compra * qtd_animais) + (custo_dieta * dias_cocho * qtd_animais)
receita_bruta = peso_final_arrobas * valor_arroba_venda * qtd_animais
lucro_total = receita_bruta - custo_total
roi = (lucro_total / custo_total) * 100
break_even = (custo_total/qtd_animais)/(peso_final/30)

# --- VISUALIZAÇÃO (DASHBOARD) ---
col1, col2, col3, col4 = st.columns(4)
col1.metric("Peso Final Projetado", f"{peso_final:.1f} kg")
col2.metric("Custo Operacional Total", f"R$ {custo_total:,.2f}")
col3.metric("Faturamento Bruto", f"R$ {receita_bruta:,.2f}")
col4.metric("Resultado Líquido", f"R$ {lucro_total:,.2f}", f"{roi:.1f}% ROI")

st.markdown("---")

# Gráfico
dados_grafico = pd.DataFrame({
    "Categoria": ["Custo de Produção (Investimento)", "Receita Bruta (Retorno)"],
    "Valor": [custo_total, receita_bruta]
})
fig = px.bar(dados_grafico, x="Categoria", y="Valor", color="Categoria", 
             color_discrete_sequence=["#ef5350", "#2E7D32"], text_auto='.2s')
fig.update_layout(title="Análise de Fluxo de Caixa do Lote")
st.plotly_chart(fig, use_container_width=True)

# --- TEXTO DE ESPECIALISTA (ZOOTECNISTA) ---
# Aqui está a mágica da autoridade técnica
analise_texto = f"""
ANÁLISE DE VIABILIDADE TÉCNICA:
A eficiência econômica deste projeto está estritamente condicionada ao desempenho biológico de {gmd_esperado} kg/dia.
Este índice é mandatório para garantir a diluição dos custos fixos e nutricionais ao longo dos {dias_cocho} dias de trato.

PONTO DE NIVELAMENTO (BREAK-EVEN):
Para cobrir os custos de aquisição e operacionais sem gerar prejuízo, o valor mínimo de venda da arroba deve ser R$ {break_even:.2f}.
Qualquer venda abaixo deste valor representa erosão de capital.

CONCLUSÃO DO ESPECIALISTA:
{'✅ [APROVADO] Operação com Margem Líquida Positiva. Recomendamos seguir o protocolo nutricional rigorosamente.' if lucro_total > 0 else '🚨 [ALERTA CRÍTICO] Risco Elevado. O custo de produção por arroba supera a receita projetada. Necessário rever dieta ou valor de compra.'}
"""
st.info(analise_texto)

# --- BOTÃO DE EXPORTAÇÃO ---
st.markdown("---")
st.subheader("📄 Área do Consultor")

dados_pdf = {
    "Qtd Animais": str(qtd_animais),
    "Peso Entrada": f"{peso_entrada} kg",
    "Valor @ Compra": f"R$ {valor_arroba_compra}",
    "Valor @ Venda": f"R$ {valor_arroba_venda}",
    "Custo Dieta": f"R$ {custo_dieta}/dia",
    "GMD Meta": f"{gmd_esperado} kg/dia"
}
resultados_pdf = {
    "Custo": f"{custo_total:,.2f}",
    "Receita": f"{receita_bruta:,.2f}",
    "Lucro": f"{lucro_total:,.2f}",
    "ROI": f"{roi:.1f}%"
}

pdf_bytes = gerar_pdf(dados_pdf, resultados_pdf, analise_texto)
st.download_button(
    label="📥 Baixar Laudo Técnico Oficial (PDF)",
    data=pdf_bytes,
    file_name="Laudo_Tecnico_AtivaGestao.pdf",
    mime="application/pdf"
)
