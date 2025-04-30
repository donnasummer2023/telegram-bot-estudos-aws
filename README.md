# 🤖 Bot Telegram de Estudo AWS

Este bot foi criado para auxiliar no registro diário de estudos para certificações da AWS. Ele interage com o usuário, registra dados no Google Sheets e motiva com mensagens positivas (previamente configuradas).

## 🔧 Funcionalidades

- `/start` — inicia a conversa e envia mensagem motivacional
- `/checkin` — escolhe o tópico de estudo
- `/checkout` — registra o que foi praticado e sentimento após o estudo

## 📚 Tecnologias

- Python
- Telegram Bot API
- Google Sheets API (via gspread)
- Railway (hospedagem)
- Flask (keep alive)
- dotenv

## 📦 Rodando localmente

1. Clone o repositório
2. Crie o arquivo `.env` com base no `.env.example`
3. Instale as dependências:
