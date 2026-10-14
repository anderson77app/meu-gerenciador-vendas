import streamlit as st
import pandas as pd
from datetime import datetime
import os

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

# Carregar dados
df_clientes = carregar_dados(ARQUIVO_CLIENTES, ["Nome"])
df_produtos = carregar_dados(ARQUIVO_PRODUTOS, ["Produto", "Preco"])
df_vendas = carregar_dados(ARQUIVO_VENDAS, ["Data", "Cliente", "Produto", "Quantidade", "Valor_Unitario", "Total", "Status"])

# Preencher com um exemplo inicial se estiver vazio
if df_clientes.empty:
    df_clientes = pd.DataFrame({"Nome": ["Cliente Exemplo"]})
    salvar_dados(df_clientes, ARQUIVO_CLIENTES)
if df_produtos.empty:
    df_produtos = pd.DataFrame({"Produto": ["Produto Exemplo"], "Preco": [10.0]})
    salvar_dados(df_produtos, ARQUIVO_PRODUTOS)

# --- INTERFACE DO APLICATIVO ---
st.title("📦 Gerenciador de Negócio")

menu = st.sidebar.radio("Navegação", ["📝 Registar Venda", "⚙️ Gerir Cadastros", "📊 Fecho do Mês"])

# Aviso sobre o Modo Dia/Noite
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
                # Buscar preço
                preco = df_produtos.loc[df_produtos["Produto"] == produto_selecionado, "Preco"].values[0]
                total = preco * quantidade
                
                nova_venda = pd.DataFrame([{
                    "Data": datetime.now().strftime("%d/%m/%Y %H:%M"),
                    "Cliente": cliente_selecionado,
                    "Produto": produto_selecionado,
                    "Quantidade": quantidade,
                    "Valor_Unitario": preco,
                    "Total": total,
                    "Status": "Pendente (Fiado)"
                }])
                
                df_vendas = pd.concat([df_vendas, nova_venda], ignore_index=True)
                salvar_dados(df_vendas, ARQUIVO_VENDAS)
                st.success(f"Venda de R$ {total:.2f} registada para {cliente_selecionado} com sucesso!")

elif menu == "⚙️ Gerir Cadastros":
    st.header("Adicionar ou Excluir")
    
    tab1, tab2 = st.tabs(["👤 Clientes", "🛒 Produtos"])
    
    with tab1:
        st.subheader("➕ Adicionar Cliente")
        with st.form("form_add_cliente", clear_on_submit=True):
            novo_cliente = st.text_input("Nome do Cliente")
            if st.form_submit_button("Guardar Cliente"):
                if novo_cliente and novo_cliente not in df_clientes["Nome"].values:
                    df_clientes = pd.concat([df_clientes, pd.DataFrame([{"Nome": novo_cliente}])], ignore_index=True)
                    salvar_dados(df_clientes, ARQUIVO_CLIENTES)
                    st.success(f"Cliente '{novo_cliente}' adicionado!")
                    st.rerun() # Atualiza a tela na hora
                else:
                    st.error("Nome inválido ou já existe.")
                    
        st.divider() # Linha de separação
        
        st.subheader("🗑️ Excluir Cliente")
        cliente_excluir = st.selectbox("Selecione para excluir:", df_clientes["Nome"].tolist(), key="del_cli")
        if st.button("🚨 Excluir Cliente Selecionado"):
            df_clientes = df_clientes[df_clientes["Nome"] != cliente_excluir]
            salvar_dados(df_clientes, ARQUIVO_CLIENTES)
            st.success(f"Cliente '{cliente_excluir}' foi removido!")
            st.rerun() # Atualiza a tela na hora

    with tab2:
        st.subheader("➕ Adicionar Produto")
        with st.form("form_add_produto", clear_on_submit=True):
            novo_produto = st.text_input("Nome do Produto")
            preco_produto = st.number_input("Preço de Venda (R$)", min_value=0.1, step=0.5)
            if st.form_submit_button("Guardar Produto"):
                if novo_produto and novo_produto not in df_produtos["Produto"].values:
                    df_produtos = pd.concat([df_produtos, pd.DataFrame([{"Produto": novo_produto, "Preco": preco_produto}])], ignore_index=True)
                    salvar_dados(df_produtos, ARQUIVO_PRODUTOS)
                    st.success(f"Produto '{novo_produto}' adicionado!")
                    st.rerun() # Atualiza a tela na hora
                else:
                    st.error("Produto inválido ou já existe.")

        st.divider() # Linha de separação

        st.subheader("🗑️ Excluir Produto")
        produto_excluir = st.selectbox("Selecione para excluir:", df_produtos["Produto"].tolist(), key="del_prod")
        if st.button("🚨 Excluir Produto Selecionado"):
            df_produtos = df_produtos[df_produtos["Produto"] != produto_excluir]
            salvar_dados(df_produtos, ARQUIVO_PRODUTOS)
            st.success(f"Produto '{produto_excluir}' foi removido!")
            st.rerun() # Atualiza a tela na hora

elif menu == "📊 Fecho do Mês":
    st.header("Contas a Receber")
    
    if not df_vendas.empty:
        pendentes = df_vendas[df_vendas["Status"] == "Pendente (Fiado)"]
        if not pendentes.empty:
            resumo = pendentes.groupby("Cliente")["Total"].sum().reset_index()
            st.write("### Total a cobrar por cliente")
            st.dataframe(resumo, use_container_width=True, hide_index=True)
            
            st.write("### Histórico Completo")
            st.dataframe(pendentes, use_container_width=True, hide_index=True)
        else:
            st.info("Todos os clientes estão em dia!")
    else:
        st.warning("Nenhuma venda registada.")
