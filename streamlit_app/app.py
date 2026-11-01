"""Cadastro de pacientes da recepção: versão Streamlit, publicada no Streamlit Community Cloud."""
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd
import streamlit as st

ARQUIVO_CSV = Path(__file__).parent / "pacientes.csv"
COLUNAS = ["timestamp", "nome", "idade", "convenio", "prioridade", "motivo"]
CONVENIOS = ["Particular", "Unimed", "Bradesco Saúde", "SulAmérica", "Outro"]
IDADE_MAXIMA = 120
PRIORIDADE_PADRAO = 3
QUANTIDADE_ULTIMOS = 5
# utf-8-sig grava o BOM no início do arquivo, o que faz o Excel mostrar os acentos corretamente
CODIFICACAO_CSV = "utf-8-sig"
# O servidor do Streamlit Community Cloud roda em UTC; sem fixar o fuso, o cadastro sai 3 horas adiantado
FUSO_HORARIO = ZoneInfo("America/Sao_Paulo")
VALORES_INICIAIS_FORMULARIO = {
    "campo_nome": "",
    "campo_idade": None,
    "campo_convenio": None,
    "campo_prioridade": PRIORIDADE_PADRAO,
    "campo_motivo": "",
}


def validar(nome, idade, convenio):
    if not nome.strip():
        return "Informe o nome do paciente."
    if idade is None:
        return "Informe a idade do paciente."
    if convenio is None:
        return "Selecione o convênio."
    return None


def gravar_no_csv(linha):
    # No Streamlit Community Cloud este arquivo some quando o app reinicia; o download abaixo é a cópia que fica
    arquivo_ja_existe = ARQUIVO_CSV.exists()
    pd.DataFrame([linha], columns=COLUNAS).to_csv(
        ARQUIVO_CSV,
        mode="a" if arquivo_ja_existe else "w",
        header=not arquivo_ja_existe,
        index=False,
        encoding=CODIFICACAO_CSV,
    )


st.set_page_config(page_title="Cadastro de Pacientes", layout="centered")
st.title("Cadastro de Pacientes")

if "pacientes" not in st.session_state:
    st.session_state.pacientes = pd.DataFrame(columns=COLUNAS)

# O formulário só é limpo depois de um cadastro válido; com erro, a recepção corrige sem redigitar tudo
if st.session_state.get("limpar_formulario", True):
    st.session_state.update(VALORES_INICIAIS_FORMULARIO)
    st.session_state.limpar_formulario = False

with st.form("cadastro"):
    nome = st.text_input("Nome do paciente", key="campo_nome")
    idade = st.number_input("Idade", min_value=0, max_value=IDADE_MAXIMA, value=None, step=1, key="campo_idade")
    convenio = st.selectbox("Convênio", CONVENIOS, index=None, placeholder="Selecione", key="campo_convenio")
    prioridade = st.slider("Prioridade do atendimento (5 = urgente)", 1, 5, key="campo_prioridade")
    motivo = st.text_area("Motivo da consulta / observações", key="campo_motivo")
    enviado = st.form_submit_button("Cadastrar", type="primary", width="stretch")

if enviado:
    erro = validar(nome, idade, convenio)
    if erro:
        st.error(erro)
    else:
        nova_linha = {
            "timestamp": datetime.now(FUSO_HORARIO).strftime("%Y-%m-%d %H:%M:%S"),
            "nome": nome.strip(),
            "idade": int(idade),
            "convenio": convenio,
            "prioridade": int(prioridade),
            "motivo": motivo.strip(),
        }
        gravar_no_csv(nova_linha)
        st.session_state.pacientes = pd.concat(
            [st.session_state.pacientes, pd.DataFrame([nova_linha], columns=COLUNAS)],
            ignore_index=True,
        )
        st.session_state.mensagem_sucesso = f"Paciente {nova_linha['nome']} cadastrado!"
        st.session_state.limpar_formulario = True
        st.rerun()

if "mensagem_sucesso" in st.session_state:
    st.success(st.session_state.pop("mensagem_sucesso"))

st.subheader("Últimos pacientes cadastrados nesta sessão")
st.dataframe(st.session_state.pacientes.tail(QUANTIDADE_ULTIMOS), hide_index=True, width="stretch")

csv = st.session_state.pacientes.to_csv(index=False).encode(CODIFICACAO_CSV)
st.download_button(
    "Baixar CSV",
    csv,
    "pacientes.csv",
    "text/csv",
    disabled=st.session_state.pacientes.empty,
    width="stretch",
)
