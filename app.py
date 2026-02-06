import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF
from datetime import datetime
import tempfile

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="AtivaGestão | Simulador", page_icon="🐂", layout="wide")

# --- CLASSE DO PDF (LAYOUT) ---
class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, 'AtivaGestao - Relatorio Tecnico', 0, 1, 'C') # Sem acento para evitar erro
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, 'Gabriel Oliveira | Consultoria Zootecnica', 0, 0, 'C')

def gerar_pdf(dados, resultados, conclusao):
    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    # Função para limpar texto (remove emojis e acentos chatos)
    def limpar(t):
        # Substitui emojis por texto
        t = t.replace("✅", "[SUCESSO]").replace("🚨", "[ALERTA]").replace("💰", "")
        return t.encode('latin-1', 'replace').decode('latin-1')

    pdf.cell(0, 10, limpar(f"Data da Simulação: {datetime.now().strftime('%d/%m/%Y')}"), 0, 1)
    pdf.ln(10)
    
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, limpar("1. Parâmetros do Lote"), 0, 1)
    pdf.set_font("Arial", size=12)
    for k, v in dados.items():
        pdf.cell(0, 8, limpar(f"- {k}: {v}"), 0, 1)
    
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, limpar("2. Resultado Financeiro"), 0, 1)
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 8, limpar(f"Custo Total: R$ {resultados['Custo']}"), 0, 1)
    pdf.cell(0, 8, limpar(f"Receita Bruta: R$ {resultados['Receita']}"), 0, 1)
    
    # Destaque do Lucro
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 8, limpar(f"LUCRO PROJETADO: R$ {resultados['Lucro']}"), 0, 1)
    pdf.cell(0, 8, limpar(f"ROI (Retorno): {resultados['ROI']}"), 0, 1)
    
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, limpar("3. Parecer Técnico"), 0, 1)
    pdf.set_font("Arial", size=12)
    # Multi_cell para o texto longo da conclusão
    pdf.multi_cell(0, 8, limpar(conclusao))
    
    return pdf.output(dest='S').encode('latin-1')

# --- APP VISUAL (Igual ao anterior) ---
st.title("🐂 AtivaGestão | Simulador de Lucro")
st.markdown("---")

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

# Cálculos
peso_final = peso_entrada + (gmd_esperado * dias_cocho)
peso_final_arrobas = peso_final / 30
custo_total = ((peso_entrada / 30) * valor_arroba_compra * qtd_animais) + (custo_dieta * dias_cocho * qtd_animais)
receita_bruta = peso_final_arrobas * valor_arroba_venda * qtd_animais
lucro_total = receita_bruta - custo_total
roi = (lucro_total / custo_total) * 100

# Exibição
col1, col2, col3, col4 = st.columns(4)
col1.metric("Peso Final", f"{peso_final:.1f} kg")
col2.metric("Custo Total", f"R$ {custo_total:,.2f}")
col3.metric("Receita", f"R$ {receita_bruta:,.2f}")
col4.metric("Lucro", f"R$ {lucro_total:,.2f}", f"{roi:.1f}% ROI")

st.markdown("---")

# Gráfico
dados_grafico = pd.DataFrame({
    "Categoria": ["Investimento", "Retorno"],
    "Valor": [custo_total, receita_bruta]
})
fig = px.bar(dados_grafico, x="Categoria", y="Valor", color="Categoria", 
             color_discrete_sequence=["#ef5350", "#66bb6a"], text_auto='.2s')
st.plotly_chart(fig, use_container_width=True)

# Texto de Conclusão PROFISSIONAL
break_even = (custo_total/qtd_animais)/(peso_final/30)

analise_texto = f"""
PREMISSAS ZOOTÉCNICAS:
A viabilidade deste cenário depende da manutenção rigorosa de um Ganho Médio Diário (GMD) de {gmd_esperado} kg durante {dias_cocho} dias.

ANÁLISE DE EQUILÍBRIO:
Para não haver prejuízo (Break-even), a arroba deve ser vendida por, no mínimo, R$ {break_even:.2f}.

CONCLUSÃO:
{'[SUCESSO] Margem Líquida Positiva. Operação Viável.' if lucro_total > 0 else '[ALERTA] Margem Negativa. Risco de Prejuízo Iminente.'}
"""
st.info(analise_texto)

# --- BOTÃO MÁGICO DE PDF ---
st.markdown("---")
st.subheader("📄 Exportar Relatório")

# Preparar dados para o PDF
dados_pdf = {
    "Qtd Animais": str(qtd_animais),
    "Peso Entrada": f"{peso_entrada} kg",
    "Valor @ Compra": f"R$ {valor_arroba_compra}",
    "Valor @ Venda": f"R$ {valor_arroba_venda}",
    "Dieta": f"R$ {custo_dieta}/dia",
    "GMD": f"{gmd_esperado} kg/dia"
}
resultados_pdf = {
    "Custo": f"{custo_total:,.2f}",
    "Receita": f"{receita_bruta:,.2f}",
    "Lucro": f"{lucro_total:,.2f}",
    "ROI": f"{roi:.1f}%"
}

# Botão
pdf_bytes = gerar_pdf(dados_pdf, resultados_pdf, analise_texto)
st.download_button(
    label="📥 Baixar Relatório em PDF",
    data=pdf_bytes,
    file_name="Relatorio_AtivaGestao.pdf",
    mime="application/pdf"
)
