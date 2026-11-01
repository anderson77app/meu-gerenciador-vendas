import streamlit as st
import pandas as pd
from datetime import datetime
import os
from fpdf import FPDF

# --- CONFIGURAÇÕES INICIAIS ---
st.set_page_config(page_title="Gestão de Vendas", layout="centered")

ARQUIVO_VENDAS = 'vendas.csv'
ARQUIVO_CLIENTES = 'clientes.csv'
ARQUIVO_PRODUTOS = 'produtos.csv'

# --- FUNÇÕES DE DADOS ---
def carregar_dados(arquivo, colunas):
    if os.path.exists(arquivo):
        return pd.read_csv(arquivo)
    return pd.DataFrame(columns=colunas)

def salvar_dados(df, arquivo):
    df.to_csv(arquivo, index=False)

def gerar_recibo_pdf(cliente, produto, qtde, preco, total, data):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="RECIBO DE VENDA", ln=True, align='C')
    pdf.line(10, 25, 200, 25)
    pdf.ln(10)
    pdf.set_font("Arial", '', 12)
    pdf.cell(200, 10, txt=f"Data: {data}", ln=True)
    pdf.cell(200, 10, txt=f"Cliente: {cliente}", ln=True)
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="Detalhes do Pedido:", ln=True)
    pdf.set_font("Arial", '', 12)
    pdf.cell(200, 10, txt=f"Produto: {produto}", ln=True)
    pdf.cell(200, 10, txt=f"Quantidade: {qtde}x (R$ {preco:.2f}/un)", ln=True)
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, txt=f"TOTAL: R$ {total:.2f}", ln=True)
    pdf.ln(15)
    pdf.set_font("Arial", 'I', 10)
    pdf.cell(200, 10, txt="Obrigado pela preferência!", ln=True, align='C')
    
    nome_arquivo = f"Recibo_{cliente.replace(' ', '_')}.pdf"
    pdf.output(nome_arquivo)
    return nome_arquivo

def gerar_extrato_pdf(cliente, df_cliente, total):
    pdf = FPDF()
    pdf.add_page()
    
    # Cabeçalho
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt=f"EXTRATO DE CONTA - {cliente}", ln=True, align='C')
    pdf.line(10, 25, 200, 25)
    pdf.ln(10)
    
    # Tabela (Cabeçalho)
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(45, 10, txt="Data", border=1)
    pdf.cell(85, 10, txt="Produto", border=1)
    pdf.cell(20, 10, txt="Qtd", border=1, align='C')
    pdf.cell(40, 10, txt="Total (R$)", border=1, align='C')
    pdf.ln()
    
    # Linhas da tabela
    pdf.set_font("Arial", '', 10)
    for index, row in df_cliente.iterrows():
        # Pega apenas a data (sem a hora) para economizar espaço, ou deixa tudo
        data_curta = str(row['Data']).split()[0]
        produto_curto = str(row['Produto'])[:35] # Corta nomes muito grandes
        
        pdf.cell(45, 10, txt=data_curta, border=1)
        pdf.cell(85, 10, txt=produto_curto, border=1)
        pdf.cell(20, 10, txt=str(row['Quantidade']), border=1, align='C')
        pdf.cell(40, 10, txt=f"{row['Total']:.2f}", border=1, align='C')
        pdf.ln()
        
    # Total Final
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(190, 10, txt=f"TOTAL A PAGAR: R$ {total:.2f}", ln=True, align='R')
    
    nome_arquivo = f"Extrato_{cliente.replace(' ', '_')}.pdf"
    pdf.output(nome_arquivo)
    return nome_arquivo

# Carregar dados
df_clientes = carregar_dados(ARQUIVO_CLIENTES, ["Nome"])
df_produtos = carregar_dados(ARQUIVO_PRODUTOS, ["Produto", "Preco"])
df_vendas = carregar_dados(ARQUIVO_VENDAS, ["Data", "Cliente", "Produto", "Quantidade", "Valor_Unitario", "Total", "Status"])

# --- INTERFACE DO APLICATIVO ---
st.title("📦 Gerenciador de Negócio")

menu = st.sidebar.radio("Navegação", ["📝 Registar Venda", "⚙️ Gerir Cadastros", "📊 Fechamento do Mês"])
st.sidebar.markdown("---")
st.sidebar.info("🌗 **Modo Dia / Noite:** Clique nos 3 pontinhos (⋮) no canto superior direito do ecrã, vá a **Settings**, e altere o **Theme**.")

if menu == "📝 Registar Venda":
    st.header("Nova Venda")
    
    lista_clientes = df_clientes["Nome"].tolist()
    lista_produtos = df_produtos["Produto"].tolist()
    
    if not lista_clientes or not lista_produtos:
        st.warning("Cadastre pelo menos um cliente e um produto antes de vender.")
    else:
        with st.form("form_venda", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                cliente_selecionado = st.selectbox("Nome do Cliente", lista_clientes)
            with col2:
                produto_selecionado = st.selectbox("Produto", lista_produtos)
                
            quantidade = st.number_input("Quantidade", min_value=1, value=1, step=1)
            botao_salvar = st.form_submit_button("✅ Confirmar Venda", use_container_width=True)

        if botao_salvar:
            preco = df_produtos.loc[df_produtos["Produto"] == produto_selecionado, "Preco"].values[0]
            total = preco * quantidade
            data_atual = datetime.now().strftime("%d/%m/%Y %H:%M")
            
            nova_venda = pd.DataFrame([{
                "Data": data_atual,
                "Cliente": cliente_selecionado,
                "Produto": produto_selecionado,
                "Quantidade": quantidade,
                "Valor_Unitario": preco,
                "Total": total,
                "Status": "Pendente (Fiado)"
            }])
            
            df_vendas = pd.concat([df_vendas, nova_venda], ignore_index=True)
            salvar_dados(df_vendas, ARQUIVO_VENDAS)
            st.success(f"Venda de R$ {total:.2f} registada!")
            
            arquivo_pdf = gerar_recibo_pdf(cliente_selecionado, produto_selecionado, quantidade, preco, total, data_atual)
            with open(arquivo_pdf, "rb") as pdf_file:
                st.download_button("📄 Baixar Recibo em PDF", data=pdf_file, file_name=arquivo_pdf, mime="application/pdf", type="primary")

elif menu == "⚙️ Gerir Cadastros":
    st.header("Adicionar ou Excluir")
    tab1, tab2 = st.tabs(["👤 Clientes", "🛒 Produtos"])
    
    with tab1:
        with st.form("form_add_cliente", clear_on_submit=True):
            novo_cliente = st.text_input("Nome do Cliente")
            if st.form_submit_button("Guardar Cliente"):
                if novo_cliente and novo_cliente not in df_clientes["Nome"].values:
                    df_clientes = pd.concat([df_clientes, pd.DataFrame([{"Nome": novo_cliente}])], ignore_index=True)
                    salvar_dados(df_clientes, ARQUIVO_CLIENTES)
                    st.success("Cliente adicionado!")
                    st.rerun()
        
        st.divider()
        if not df_clientes.empty:
            cliente_excluir = st.selectbox("Excluir Cliente:", df_clientes["Nome"].tolist(), key="del_cli")
            if st.button("🚨 Excluir Cliente"):
                df_clientes = df_clientes[df_clientes["Nome"] != cliente_excluir]
                salvar_dados(df_clientes, ARQUIVO_CLIENTES)
                st.success("Removido!")
                st.rerun()

    with tab2:
        with st.form("form_add_produto", clear_on_submit=True):
            novo_produto = st.text_input("Nome do Produto")
            preco_produto = st.number_input("Preço de Venda (R$)", min_value=0.1, step=0.5)
            if st.form_submit_button("Guardar Produto"):
                if novo_produto and novo_produto not in df_produtos["Produto"].values:
                    df_produtos = pd.concat([df_produtos, pd.DataFrame([{"Produto": novo_produto, "Preco": preco_produto}])], ignore_index=True)
                    salvar_dados(df_produtos, ARQUIVO_PRODUTOS)
                    st.success("Produto adicionado!")
                    st.rerun()
        
        st.divider()
        if not df_produtos.empty:
            produto_excluir = st.selectbox("Excluir Produto:", df_produtos["Produto"].tolist(), key="del_prod")
            if st.button("🚨 Excluir Produto"):
                df_produtos = df_produtos[df_produtos["Produto"] != produto_excluir]
                salvar_dados(df_produtos, ARQUIVO_PRODUTOS)
                st.success("Removido!")
                st.rerun()

elif menu == "📊 Fechamento do Mês":
    st.header("Contas a Receber")
    
    if not df_vendas.empty:
        pendentes = df_vendas[df_vendas["Status"] == "Pendente (Fiado)"]
        if not pendentes.empty:
            # Resumo Geral
            resumo = pendentes.groupby("Cliente")["Total"].sum().reset_index()
            st.write("### Resumo de Valores a Cobrar")
            st.dataframe(resumo, use_container_width=True, hide_index=True)
            
            st.divider()
            
            # Gerador de Extrato Individual
            st.write("### 🖨️ Gerar Extrato Individual")
            cliente_extrato = st.selectbox("Selecione o Cliente para criar o extrato:", resumo["Cliente"].tolist())
            
            if cliente_extrato:
                df_cliente = pendentes[pendentes["Cliente"] == cliente_extrato]
                total_cliente = resumo[resumo["Cliente"] == cliente_extrato]["Total"].values[0]
                
                # Mostra uma prévia na tela
                st.write(f"**Prévia das compras de {cliente_extrato}:**")
                st.dataframe(df_cliente[["Data", "Produto", "Quantidade", "Total"]], use_container_width=True, hide_index=True)
                
                # Botão de Download do PDF
                arquivo_extrato = gerar_extrato_pdf(cliente_extrato, df_cliente, total_cliente)
                with open(arquivo_extrato, "rb") as pdf_file:
                    st.download_button(
                        label=f"📄 Baixar Extrato de {cliente_extrato} (PDF)",
                        data=pdf_file,
                        file_name=arquivo_extrato,
                        mime="application/pdf",
                        type="primary"
                    )
        else:
            st.info("Nenhuma conta pendente. Todos os clientes estão em dia!")
    else:
        st.warning("Nenhuma venda registada.")
