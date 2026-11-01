# Cadastro de Pacientes: Gradio x Streamlit

Atividade Prática da Aula 1 da disciplina Aplicações em Data Science.

A mesma aplicação de coleta de dados foi construída duas vezes: um formulário de cadastro de pacientes para a recepção de um consultório médico. O objetivo é comparar na prática as duas bibliotecas. O formulário tem os campos nome, idade, convênio, prioridade de 1 a 5 (5 = urgente) e motivo da consulta. Cada envio grava uma linha com data e hora.

## Estrutura

```
gradio_app/app.py       versão Gradio, executada localmente, grava gradio_app/pacientes.csv
streamlit_app/app.py    versão Streamlit, publicada no Streamlit Community Cloud
requirements.txt        dependências (gradio, streamlit, pandas)
tests/test_apps.py      testes automatizados das duas versões
evidencias/             pacientes.csv gerado nos testes, print do Gradio local e prints do Streamlit no celular
```

## Como executar

```
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt

python gradio_app\app.py              # abre em http://127.0.0.1:7860
streamlit run streamlit_app\app.py    # abre em http://localhost:8501
```

Para abrir a versão Gradio no celular, há duas opções. Na mesma rede Wi-Fi, trocar a última linha por `demo.launch(server_name="0.0.0.0")` e acessar `http://IP-do-computador:7860`. Para um link público temporário, usar `demo.launch(share=True)`.

Para rodar os testes: `pip install pytest` e depois `python -m pytest tests`.

## Publicação no Streamlit Community Cloud

1. Enviar este repositório para o GitHub (público).
2. Em share.streamlit.io, entrar com a conta do GitHub e clicar em "Create app".
3. Selecionar o repositório, a branch `main` e o arquivo principal `streamlit_app/app.py`.
4. Aguardar o build e testar pelo link `*.streamlit.app`, também no celular.

## Decisões de implementação

- **Mesmos campos e regras nas duas versões.** O nome é obrigatório, a idade vai de 0 a 120 e o convênio é obrigatório. Um cadastro inválido mostra a mensagem de erro, não grava nada e mantém o que já foi digitado. Depois de um cadastro válido, o formulário é limpo para o próximo paciente.
- **Coluna única.** O layout é simples e em coluna única, como pede o enunciado para uso em celular.
- **CSV em `utf-8-sig`.** O arquivo é gravado com BOM para que o Excel mostre corretamente acentos como "Bradesco Saúde".
- **Gravação dupla no Streamlit.** A versão Streamlit grava no `pacientes.csv` (mesma lógica da versão Gradio) e acumula a sessão em `st.session_state`. Como o disco do Streamlit Community Cloud é efêmero, o botão "Baixar CSV" exporta os cadastros da sessão.
- **Horário de Brasília.** A data e a hora são gravadas no fuso `America/Sao_Paulo`. O servidor do Streamlit Community Cloud roda em UTC, e sem esse ajuste os primeiros testes no celular registraram o cadastro 3 horas adiantado.
- **Caminho do CSV fixo.** O arquivo é resolvido a partir da pasta do próprio script, então o app grava no mesmo lugar de qualquer pasta em que for iniciado.

## Comparação

| Aspecto | Gradio | Streamlit |
|---|---|---|
| Modelo de execução | Eventos: só a função ligada ao botão roda | O script inteiro roda de novo a cada interação |
| Formulário | Componentes soltos dentro de `gr.Blocks`, ligados por `botao.click` | `st.form` agrupa os campos e envia tudo de uma vez |
| Estado | A tabela é relida do CSV a cada cadastro | `st.session_state` guarda os dados da sessão |
| Limpar campos | A função devolve os novos valores dos campos | É preciso redefinir o `session_state` antes de desenhar os campos |
| Publicação | Local, link `share=True` temporário ou Hugging Face Spaces | Streamlit Community Cloud direto do GitHub |
| Persistência na nuvem | (não publicada nesta atividade) | Disco efêmero, daí o botão de download |

Observação: no Gradio 6, o campo Idade vazio aparece na tela como "0". Se a recepção não preencher a idade, o cadastro pode ser gravado com idade 0. No Streamlit, o campo fica realmente vazio e a validação exige o preenchimento.

## Evidências

| Arquivo | Conteúdo |
|---|---|
| `evidencias/print_gradio_local.png` | Versão Gradio rodando localmente, com os últimos pacientes cadastrados |
| `evidencias/pacientes.csv` | Arquivo gravado pela versão Gradio durante os testes (pacientes fictícios) |
| `evidencias/print_streamlit_celular_formulario.jpeg` | App publicado no Streamlit Community Cloud, aberto no celular |
| `evidencias/print_streamlit_celular_cadastro.jpeg` | Cadastro confirmado no celular, com a tabela da sessão e o botão Baixar CSV |

Os prints do celular foram tirados antes do ajuste de fuso horário, por isso mostram os cadastros com 3 horas a mais que o relógio do aparelho.
