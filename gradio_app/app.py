"""Cadastro de pacientes da recepção: versão Gradio, executada localmente."""
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import gradio as gr
import pandas as pd

ARQUIVO_CSV = Path(__file__).parent / "pacientes.csv"
COLUNAS = ["timestamp", "nome", "idade", "convenio", "prioridade", "motivo"]
CONVENIOS = ["Particular", "Unimed", "Bradesco Saúde", "SulAmérica", "Outro"]
IDADE_MAXIMA = 120
QUANTIDADE_ULTIMOS = 5
# utf-8-sig grava o BOM no início do arquivo, o que faz o Excel mostrar os acentos corretamente
CODIFICACAO_CSV = "utf-8-sig"
# Horário de Brasília fixo, para o registro não depender do relógio do servidor (que na nuvem fica em UTC)
FUSO_HORARIO = ZoneInfo("America/Sao_Paulo")


def ultimos_pacientes():
    if not ARQUIVO_CSV.exists():
        return pd.DataFrame(columns=COLUNAS)
    return pd.read_csv(ARQUIVO_CSV, encoding=CODIFICACAO_CSV).tail(QUANTIDADE_ULTIMOS)


def validar(nome, idade, convenio):
    if not nome.strip():
        return "Informe o nome do paciente."
    if idade is None or not 0 <= idade <= IDADE_MAXIMA:
        return f"Informe uma idade entre 0 e {IDADE_MAXIMA}."
    if convenio not in CONVENIOS:
        return "Selecione o convênio."
    return None


def cadastrar_paciente(nome, idade, convenio, prioridade, motivo):
    erro = validar(nome, idade, convenio)
    if erro:
        # gr.skip() mantém os campos como estão para a recepção corrigir só o que faltou
        return f"Erro: {erro}", ultimos_pacientes(), gr.skip(), gr.skip(), gr.skip(), gr.skip(), gr.skip()

    linha = {
        "timestamp": datetime.now(FUSO_HORARIO).strftime("%Y-%m-%d %H:%M:%S"),
        "nome": nome.strip(),
        "idade": int(idade),
        "convenio": convenio,
        "prioridade": int(prioridade),
        "motivo": motivo.strip(),
    }
    novo = pd.DataFrame([linha], columns=COLUNAS)
    arquivo_ja_existe = ARQUIVO_CSV.exists()
    novo.to_csv(
        ARQUIVO_CSV,
        mode="a" if arquivo_ja_existe else "w",
        header=not arquivo_ja_existe,
        index=False,
        encoding=CODIFICACAO_CSV,
    )
    mensagem = f"Paciente {linha['nome']} cadastrado com sucesso às {linha['timestamp'][11:]}."
    # Limpa o formulário para o próximo paciente que chegar
    return mensagem, ultimos_pacientes(), "", None, None, 3, ""


with gr.Blocks(title="Cadastro de Pacientes") as demo:
    gr.Markdown("## Cadastro de Pacientes")
    # Coluna única: em tela de celular os campos ficam empilhados, sem rolagem lateral
    with gr.Column():
        nome = gr.Textbox(label="Nome do paciente")
        idade = gr.Number(label="Idade", value=None, minimum=0, maximum=IDADE_MAXIMA, precision=0)
        convenio = gr.Dropdown(CONVENIOS, label="Convênio", value=None)
        prioridade = gr.Slider(1, 5, value=3, step=1, label="Prioridade do atendimento (5 = urgente)")
        motivo = gr.Textbox(label="Motivo da consulta / observações", lines=3)
        botao = gr.Button("Cadastrar", variant="primary")
        saida_msg = gr.Textbox(label="Status", interactive=False)
        tabela = gr.Dataframe(label="Últimos pacientes cadastrados", interactive=False)

    botao.click(
        cadastrar_paciente,
        [nome, idade, convenio, prioridade, motivo],
        [saida_msg, tabela, nome, idade, convenio, prioridade, motivo],
    )
    demo.load(ultimos_pacientes, outputs=tabela)


if __name__ == "__main__":
    demo.launch()
