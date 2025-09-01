import streamlit as st
import datetime
import json
import os
import pytz

# --- Importe suas classes e funções aqui ---
# Certifique-se de que a classe PC_Card está em 'card.py'
# e as funções de persistência e manipulação estão em 'functions.py'
from card import PC_Card
from functions import carregar_dados, salvar_dados, adicionar_pc, deletar_pc, toggle_manutencao

# --- Lógica de Autenticação ---
st.set_page_config(layout="wide")
st.title("Área de Gerenciamento")

# Acesso à lista de usuários autorizados
if "gerenciamento" in st.secrets:
    usuarios_autorizados = st.secrets["gerenciamento"]["usuarios"]
else:
    usuarios_autorizados = []

# Inicializa as variáveis de sessão para o login
if "logado" not in st.session_state:
    st.session_state.logado = False
if "email" not in st.session_state:
    st.session_state.email = ""
if "pcs" not in st.session_state:
    st.session_state.pcs = carregar_dados()

if not st.session_state.logado:
    # --- Interface de Login ---
    st.info("Esta é uma área restrita. Por favor, faça login para continuar.")
    email_digitado = st.text_input("Digite seu e-mail:")
    
    if st.button("Entrar"):
        if email_digitado in usuarios_autorizados:
            st.session_state.logado = True
            st.session_state.email = email_digitado
            st.success("Login bem-sucedido! A página será recarregada.")
            st.rerun()
        else:
            st.error("E-mail não autorizado.")
else:
    # --- Conteúdo da Página de Gerenciamento (após o login) ---
    st.success(f"Bem-vindo, {st.session_state.email}!")
    st.markdown("---")
    
    # Adicionar Novo PC
    with st.expander("Adicionar Novo PC"):
        with st.form("form_novo_pc", clear_on_submit=True):
            url = st.text_input("URL do PC")
            nome = st.text_input("Nome do PC")
            gpu = st.text_input("GPU")
            submit_button = st.form_submit_button("Criar Card")

        if submit_button and nome:
            adicionar_pc(url, nome, gpu)
            st.success(f"PC '{nome}' adicionado com sucesso!")
            st.rerun()

    st.markdown("---")

    # Exibição dos Cards
    st.header("Cards de PCs")
    if not st.session_state.pcs:
        st.info("Nenhum PC cadastrado ainda. Use o formulário acima para adicionar um.")
    else:
        num_cards = len(st.session_state.pcs)
        for i in range(0, num_cards, 3):
            cols = st.columns(3)
            for j in range(3):
                if i + j < num_cards:
                    with cols[j]:
                        pc = st.session_state.pcs[i + j]

                        cor, status_text = "green", "Disponível"
                        if pc.em_manutencao:
                            cor = "blue"
                            status_text = "Em Manutenção"
                        else:
                            fuso_horario_brasil = pytz.timezone('America/Sao_Paulo')
                            agora = datetime.datetime.now(fuso_horario_brasil)
                            cor_status, status_info = pc.esta_ocupado(agora)
                            
                            if cor_status == "ocupado":
                                cor = "red"
                                status_text = "Ocupado agora"
                            elif cor_status == "quase_ocupado":
                                cor = "yellow"
                                status_text = status_info
                            else: # "disponivel"
                                cor = "green"
                                if status_info == "N/A":
                                    status_text = "Disponível"
                                else:
                                    status_text = status_info

                        card_style = f"background-color: {cor}; padding: 15px; border-radius: 10px; min-height: 250px; display: flex; flex-direction: column; justify-content: space-between; margin-bottom: 20px; color: black;"

                        st.markdown(
                            f"""
                            <div style='{card_style}'>
                                <div>
                                    <h4>{pc.nome}</h4>
                                    <p><strong>URL:</strong> {pc.url}</p>
                                    <p><strong>GPU:</strong> {pc.gpu}</p>
                                </div>
                            </div>
                            """, unsafe_allow_html=True
                        )
                        
                        with st.container():
                            st.markdown(f"**Status:** {status_text}")
                            
                            st.markdown("**Próximos Agendamentos:**")
                            if pc.agendamentos:
                                for inicio, fim in pc.agendamentos:
                                    st.markdown(f"- **Início:** {inicio.strftime('%d/%m %H:%M')} | **Fim:** {fim.strftime('%d/%m %H:%M')}")
                            else:
                                st.markdown("Nenhum agendamento futuro.")
                            
                            st.checkbox("Em Manutenção", value=pc.em_manutencao, key=f"manutencao_{i+j}", on_change=toggle_manutencao, args=(i+j,))
                            
                            col_btn1, col_btn2 = st.columns(2)
                            
                            with col_btn1:
                                with st.popover("Agendar Uso", help="Clique para agendar um período de uso."):
                                    st.markdown(f"**Agendando para:** {pc.nome}")
                                    
                                    with st.form(key=f"form_agendar_{i+j}", clear_on_submit=False):
                                        col_form1, col_form2 = st.columns(2)
                                        with col_form1:
                                            data_inicio = st.date_input("Data de Início", key=f"data_inicio_form_{i+j}", value=datetime.date.today())
                                            hora_inicio = st.time_input("Hora de Início", key=f"hora_inicio_form_{i+j}", value=datetime.time(9, 0))
                                        with col_form2:
                                            data_fim = st.date_input("Data de Fim", key=f"data_fim_form_{i+j}", value=datetime.date.today())
                                            hora_fim = st.time_input("Hora de Fim", key=f"hora_fim_form_{i+j}", value=datetime.time(17, 0))

                                        confirmar_btn = st.form_submit_button("Confirmar Agendamento")
                                        
                                        if confirmar_btn:
                                            data_hora_inicio = datetime.datetime.combine(data_inicio, hora_inicio)
                                            data_hora_fim = datetime.datetime.combine(data_fim, hora_fim)
                                            
                                            agora = datetime.datetime.now()
                                            conflito = False
                                            
                                            if data_hora_inicio < agora:
                                                st.error("Não é possível agendar uma data no passado.")
                                                conflito = True
                                            elif data_hora_inicio >= data_hora_fim:
                                                st.error("A data e hora de início devem ser anteriores à data e hora de fim.")
                                                conflito = True
                                            else:
                                                for inicio_existente, fim_existente in pc.agendamentos:
                                                    if not (data_hora_fim <= inicio_existente or data_hora_inicio >= fim_existente):
                                                        st.error("O agendamento se sobrepõe a um agendamento existente.")
                                                        conflito = True
                                                        break

                                            if not conflito:
                                                pc.agendar_uso(data_hora_inicio, data_hora_fim)
                                                salvar_dados(st.session_state.pcs)
                                                st.success(f"Agendamento para **{pc.nome}** confirmado de {data_hora_inicio.strftime('%d/%m/%Y %H:%M')} a {data_hora_fim.strftime('%d/%m/%Y %H:%M')}!")
                                                st.rerun()

                            
                            # Botão de edição dentro de uma coluna separada para organização
                            with col_btn2:
                                with st.popover("Editar"):
                                    st.markdown(f"**Editando:** {pc.nome}")
                                    
                                    # Formulário de edição
                                    with st.form(key=f"form_editar_{i+j}"):
                                        novo_nome = st.text_input("Nome do PC", value=pc.nome, key=f"edit_nome_{i+j}")
                                        nova_url = st.text_input("URL", value=pc.url, key=f"edit_url_{i+j}")
                                        nova_gpu = st.text_input("GPU", value=pc.gpu, key=f"edit_gpu_{i+j}")
                                        
                                        st.markdown("---")
                                        st.markdown("##### Gerenciar Agendamentos")
                                        if pc.agendamentos:
                                            agendamentos_a_remover = st.multiselect(
                                                "Selecione agendamentos para remover:",
                                                options=[f"{inicio.strftime('%d/%m/%Y %H:%M')} - {fim.strftime('%d/%m/%Y %H:%M')}" for inicio, fim in pc.agendamentos],
                                                key=f"remover_agendamentos_{i+j}"
                                            )
                                        else:
                                            st.info("Nenhum agendamento para remover.")
                                        
                                        salvar_btn = st.form_submit_button("Salvar Alterações")
                                        deletar_card_btn = st.form_submit_button("Deletar Card")
                                        
                                        if salvar_btn:
                                            pc.nome = novo_nome
                                            pc.url = nova_url
                                            pc.gpu = nova_gpu
                                            
                                            if pc.agendamentos and agendamentos_a_remover:
                                                agendamentos_atuais_str = [f"{inicio.strftime('%d/%m/%Y %H:%M')} - {fim.strftime('%d/%m/%Y %H:%M')}" for inicio, fim in pc.agendamentos]
                                                novos_agendamentos = [pc.agendamentos[k] for k, item in enumerate(agendamentos_atuais_str) if item not in agendamentos_a_remover]
                                                pc.agendamentos = novos_agendamentos
                                            
                                            salvar_dados(st.session_state.pcs)
                                            st.success("Card atualizado com sucesso!")
                                            st.rerun()

                                        if deletar_card_btn:
                                            deletar_pc(i+j)

    if st.button("Sair"):
        st.session_state.logado = False
        st.rerun()