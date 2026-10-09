import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- CONFIGURAÇÕES INICIAIS ---
st.set_page_config(page_title="Gestão de Vendas", layout="centered")
ARQUIVO_VENDAS = 'vendas.csv'

# Dados de exemplo (No futuro, você pode colocar isso em outro CSV ou Banco de Dados)
CLIENTES = ["João Silva", "Maria Oliveira", "Carlos Souza", "Ana Costa"]
PRODUTOS = {
    "Água": 2.50,
    "Refrigerante": 5.00,
    "Cerveja": 6.50,
    "Salgado": 7.00
}

# Função para carregar vendas salvas
def carregar_vendas():
    if os.path.exists(ARQUIVO_VENDAS):
        return pd.read_csv(ARQUIVO_VENDAS)
    else:
        return pd.DataFrame(columns=["Data", "Cliente", "Produto", "Quantidade", "Valor_Unitario", "Total", "Status"])

# Função para salvar nova venda
def registrar_venda(cliente, produto, quantidade):
    df = carregar_vendas()
    preco = PRODUTOS[produto]
    total = preco * quantidade
    
    nova_venda = pd.DataFrame([{
        "Data": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "Cliente": cliente,
        "Produto": produto,
        "Quantidade": quantidade,
        "Valor_Unitario": preco,
        "Total": total,
        "Status": "Pendente (Fiado)"
    }])
    
    df = pd.concat([df, nova_venda], ignore_index=True)
    df.to_csv(ARQUIVO_VENDAS, index=False)
    return total

# --- INTERFACE DO APLICATIVO ---
st.title("📦 Gerenciador de Negócio")

# Menu de navegação lateral
menu = st.sidebar.radio("Menu", ["📝 Registrar Venda", "📊 Fechamento do Mês"])

if menu == "📝 Registrar Venda":
    st.header("Nova Venda")
    st.write("Registre o pedido rapidamente aqui.")

    # Formulário de venda rápida
    with st.form("form_venda", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            cliente_selecionado = st.selectbox("Nome do Cliente", CLIENTES)
        with col2:
            produto_selecionado = st.selectbox("Produto", list(PRODUTOS.keys()))
            
        quantidade = st.number_input("Quantidade", min_value=1, value=1, step=1)
        
        botao_salvar = st.form_submit_button("✅ Confirmar Venda", use_container_width=True)

        if botao_salvar:
            total_venda = registrar_venda(cliente_selecionado, produto_selecionado, quantidade)
            st.success(f"Venda de R$ {total_venda:.2f} registrada para {cliente_selecionado} com sucesso!")

elif menu == "📊 Fechamento do Mês":
    st.header("Controle de Clientes (Contas a Receber)")
    
    df_vendas = carregar_vendas()
    
    if not df_vendas.empty:
        # Filtra apenas o que está pendente
        pendentes = df_vendas[df_vendas["Status"] == "Pendente (Fiado)"]
        
        if not pendentes.empty:
            # Agrupa o valor total que cada cliente está devendo
            resumo_clientes = pendentes.groupby("Cliente")["Total"].sum().reset_index()
            resumo_clientes.columns = ["Cliente", "Total Devendo (R$)"]
            
            st.write("### Resumo de Dívidas por Cliente")
            st.dataframe(resumo_clientes, use_container_width=True, hide_index=True)
            
            st.write("### Extrato Detalhado")
            cliente_filtro = st.selectbox("Ver detalhes do cliente:", ["Todos"] + CLIENTES)
            
            if cliente_filtro != "Todos":
                st.dataframe(pendentes[pendentes["Cliente"] == cliente_filtro], hide_index=True)
            else:
                st.dataframe(pendentes, hide_index=True)
        else:
            st.info("Nenhuma conta pendente. Todos estão em dia!")
    else:
        st.warning("Nenhuma venda registrada ainda.")
