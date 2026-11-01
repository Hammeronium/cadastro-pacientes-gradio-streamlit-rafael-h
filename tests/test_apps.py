"""Testes das duas versões: gravação no CSV, validação e limpeza do formulário."""
import importlib.util
from pathlib import Path

import pandas as pd
import pytest
from streamlit.testing.v1 import AppTest

RAIZ_PROJETO = Path(__file__).parent.parent
APP_GRADIO = RAIZ_PROJETO / "gradio_app" / "app.py"
APP_STREAMLIT = RAIZ_PROJETO / "streamlit_app" / "app.py"
COLUNAS_ESPERADAS = ["timestamp", "nome", "idade", "convenio", "prioridade", "motivo"]


@pytest.fixture
def app_gradio(tmp_path, monkeypatch):
    especificacao = importlib.util.spec_from_file_location("app_gradio", APP_GRADIO)
    modulo = importlib.util.module_from_spec(especificacao)
    especificacao.loader.exec_module(modulo)
    monkeypatch.setattr(modulo, "ARQUIVO_CSV", tmp_path / "pacientes.csv")
    return modulo


def test_gradio_cria_csv_com_cabecalho_e_acumula_linhas(app_gradio):
    app_gradio.cadastrar_paciente("Maria Souza", 34, "Unimed", 2, "Retorno")
    mensagem, tabela, *campos_limpos = app_gradio.cadastrar_paciente("José Lima", 71, "Bradesco Saúde", 5, "Dor no peito")

    dados = pd.read_csv(app_gradio.ARQUIVO_CSV, encoding="utf-8-sig")
    assert list(dados.columns) == COLUNAS_ESPERADAS
    assert dados["nome"].tolist() == ["Maria Souza", "José Lima"]
    assert dados.loc[1, "convenio"] == "Bradesco Saúde"
    assert "sucesso" in mensagem
    assert len(tabela) == 2
    assert campos_limpos == ["", None, None, 3, ""]


def test_gradio_recusa_cadastro_incompleto_sem_gravar(app_gradio):
    mensagem, *_ = app_gradio.cadastrar_paciente("   ", 30, "Particular", 1, "")
    assert mensagem.startswith("Erro")
    mensagem, *_ = app_gradio.cadastrar_paciente("Ana", None, "Particular", 1, "")
    assert "idade" in mensagem
    assert not app_gradio.ARQUIVO_CSV.exists()


def test_gradio_tabela_mostra_so_os_ultimos_cinco(app_gradio):
    for numero in range(7):
        _, tabela, *_ = app_gradio.cadastrar_paciente(f"Paciente {numero}", 40, "Outro", 1, "")
    assert tabela["nome"].tolist() == [f"Paciente {numero}" for numero in range(2, 7)]


def preencher_formulario_streamlit(app, nome, idade, convenio, prioridade, motivo):
    app.text_input(key="campo_nome").input(nome)
    app.number_input(key="campo_idade").set_value(idade)
    app.selectbox(key="campo_convenio").select(convenio)
    app.slider(key="campo_prioridade").set_value(prioridade)
    app.text_area(key="campo_motivo").input(motivo)
    app.button[0].click().run()


@pytest.fixture
def app_streamlit(tmp_path):
    # O app grava ao lado do próprio arquivo; uma cópia em pasta temporária evita sujar o projeto
    copia = tmp_path / "app.py"
    copia.write_text(APP_STREAMLIT.read_text(encoding="utf-8"), encoding="utf-8")
    app = AppTest.from_file(str(copia)).run()
    assert not app.exception
    return app, tmp_path / "pacientes.csv"


def test_streamlit_cadastra_acumula_na_sessao_e_limpa_formulario(app_streamlit):
    app, arquivo_csv = app_streamlit
    preencher_formulario_streamlit(app, "Maria Souza", 34, "Unimed", 2, "Retorno")
    preencher_formulario_streamlit(app, "José Lima", 71, "SulAmérica", 5, "Dor no peito")

    assert not app.exception
    assert app.success[0].value == "Paciente José Lima cadastrado!"
    assert app.session_state.pacientes["nome"].tolist() == ["Maria Souza", "José Lima"]
    assert app.text_input(key="campo_nome").value == ""
    assert app.number_input(key="campo_idade").value is None
    assert app.slider(key="campo_prioridade").value == 3
    dados = pd.read_csv(arquivo_csv, encoding="utf-8-sig")
    assert list(dados.columns) == COLUNAS_ESPERADAS
    assert dados["convenio"].tolist() == ["Unimed", "SulAmérica"]


def test_streamlit_recusa_sem_nome_e_mantem_o_que_foi_digitado(app_streamlit):
    app, arquivo_csv = app_streamlit
    preencher_formulario_streamlit(app, "", 50, "Particular", 4, "Exame")

    assert app.error[0].value == "Informe o nome do paciente."
    assert app.number_input(key="campo_idade").value == 50
    assert app.session_state.pacientes.empty
    assert not arquivo_csv.exists()
