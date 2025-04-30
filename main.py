import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters, ConversationHandler
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
from dotenv import load_dotenv
import base64

# NEW: Flask para manter o bot vivo
from flask import Flask
import threading

# ========== SERVIDOR FLASK ==========
app_web = Flask('')

@app_web.route('/')
def home():
    return "Bot está vivo!"

def run():
    app_web.run(host='0.0.0.0', port=8080)

t = threading.Thread(target=run)
t.start()
# ====================================

# Carrega variáveis de ambiente
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# NEW: Salva e decodifica o credentials.json via base64
cred_data = base64.b64decode(os.getenv("GOOGLE_CREDS_B64"))
with open("credentials.json", "wb") as f:
    f.write(cred_data)

# Logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Conexão com Google Sheets
scope = [
    "https://spreadsheets.google.com/feeds",
    'https://www.googleapis.com/auth/spreadsheets',
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)
log_sheet = client.open("Log de Estudos AWS").worksheet("Log")
content_sheet = client.open("Log de Estudos AWS").worksheet("Conteudo")

# Variáveis do bot
user_sessions = {}
CHECKIN_TOPIC, CHECKOUT_PRACTICE, CHECKOUT_FEELING = range(3)

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Olá! Use /checkin para começar seus estudos e /checkout quando terminar.")
    frases = [
        "Você é mais forte do que imagina. Continue firme! 💪",
        "O esforço de hoje é o sucesso de amanhã. 🚀",
        "Cada passo te leva mais perto da certificação! 🧠",
        "Não desista! Grandes conquistas levam tempo. ⏳",
        "Estudar com foco é superpoder. Use o seu! ⚡️",
    ]
    index = datetime.now().timetuple().tm_yday % len(frases)
    await update.message.reply_text(frases[index])

# /checkin
async def checkin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    topics = content_sheet.col_values(1)[1:]
    context.user_data["topics"] = topics
    lista = "\n".join([f"{i+1}. {topic}" for i, topic in enumerate(topics)])
    await update.message.reply_text(f"O que você vai estudar hoje?\n\n{lista}\n\nResponda com o número do tópico.")
    return CHECKIN_TOPIC

async def handle_checkin_topic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    try:
        escolha = int(update.message.text.strip()) - 1
        topico = context.user_data["topics"][escolha]
    except (ValueError, IndexError):
        await update.message.reply_text("Por favor, envie um número válido correspondente ao tópico.")
        return CHECKIN_TOPIC
    user_sessions[user_id] = {
        "user": update.effective_user.username,
        "topic": topico,
        "start_time": datetime.now()
    }
    await update.message.reply_text("Beleza! Quando terminar, envie /checkout.")
    return ConversationHandler.END

# /checkout
async def checkout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "O que você praticou hoje? \n\nSe não praticou, apenas responda: 'Nada. Apenas teoria hoje.'"
    )
    return CHECKOUT_PRACTICE

async def handle_checkout_practice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in user_sessions:
        await update.message.reply_text("Você precisa fazer /checkin antes de usar /checkout.")
        return ConversationHandler.END
    user_sessions[user_id]["practice"] = update.message.text
    sentimentos = [
        "1. Consegui aprender bem 👍",
        "2. Achei desafiador, mas foi bom 💡",
        "3. Fiquei um pouco confusa 😕",
        "4. Tive dificuldade 😓",
        "5. Não consegui focar 😞"
    ]
    await update.message.reply_text("Como se sentiu ao estudar?\n\n" + "\n".join(sentimentos))
    return CHECKOUT_FEELING

async def handle_checkout_feeling(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    input_text = update.message.text.strip()
    sentimentos_map = {
        "1": "Consegui aprender bem",
        "2": "Achei desafiador, mas foi bom",
        "3": "Fiquei um pouco confusa",
        "4": "Tive dificuldade",
        "5": "Não consegui focar"
    }
    sentimento = sentimentos_map.get(input_text, update.message.text)
    session = user_sessions.pop(user_id, None)
    if session:
        end_time = datetime.now()
        duration = end_time - session["start_time"]
        minutes = int(duration.total_seconds() / 60)
        row = [
            session["user"],
            session["start_time"].strftime("%d/%m/%Y"),
            f"{minutes} min",
            session["topic"],
            session["practice"],
            sentimento
        ]
        log_sheet.append_row(row)
        user_display = (
            f"@{update.effective_user.username}"
            if update.effective_user.username
            else update.effective_user.first_name
        )
        message = (
            f"🦉 *{user_display} — Check-in de {session['start_time'].strftime('%d/%m')}*\n\n"
            f"🕒 Tempo: {minutes}min\n"
            f"📘 Conteúdo: {session['topic']}\n"
            f"🚠 Prática: {session['practice']}\n"
            f"❤️ Sentimento: {sentimento}"
        )
        await context.bot.send_message(chat_id=-4634966616, text=message, parse_mode="Markdown")
    return ConversationHandler.END

async def get_chat_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat.id
    await update.message.reply_text(f"O chat_id do grupo é: {chat_id}")

# Inicializa o bot
if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    checkin_handler = ConversationHandler(
        entry_points=[CommandHandler("checkin", checkin)],
        states={CHECKIN_TOPIC: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_checkin_topic)]},
        fallbacks=[]
    )
    checkout_handler = ConversationHandler(
        entry_points=[CommandHandler("checkout", checkout)],
        states={
            CHECKOUT_PRACTICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_checkout_practice)],
            CHECKOUT_FEELING: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_checkout_feeling)]
        },
        fallbacks=[]
    )
    app.add_handler(checkin_handler)
    app.add_handler(checkout_handler)
    app.add_handler(CommandHandler("getid", get_chat_id))
    app.run_polling()
