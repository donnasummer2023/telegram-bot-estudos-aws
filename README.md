# 🤖 AWS Study Bot Telegram

Um bot de Telegram para registrar sessões de estudo direcionadas. Ele permite iniciar e finalizar sessões, registrar o que foi estudado, práticas realizadas e sentimento ao final. Todos os dados são registrados em uma planilha do Google Sheets.

## Funcionalidades

- Comando `/checkin`: inicia uma sessão de estudo, permitindo escolher um tópico da planilha.
- Comando `/checkout`: finaliza a sessão, perguntando sobre prática e sentimento.
- Registros automáticos em uma Google Sheet (data, duração, conteúdo, prática, sentimento da sessão).
- Integração com grupo no Telegram para envio de resumo do estudo.
- Deploy contínuo com Railway.

## Tecnologias

- Python
- `python-telegram-bot`
- `gspread` para integração com Google Sheets
- `Flask` para manter o bot ativo no Railway
- Deploy via [Railway](https://railway.app/)

## Como rodar localmente

1. Clone o projeto:
```bash
git clone https://github.com/seu-usuario/aws-study-bot.git
cd aws-study-bot
