import os
import asyncio
from telegram import (
    Update,
    BotCommand,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    CallbackQueryHandler
)

# ==============================
# TOKEN (VARIABLE DE ENTORNO)
# ==============================

TOKEN = os.getenv("TOKEN")

# ==============================
# COMANDOS DEL BOT
# ==============================

async def set_commands(app):
    commands = [
        BotCommand("start", "Iniciar el bot"),
        BotCommand("help", "Mostrar ayuda"),
        BotCommand("menu", "Abrir menú"),
        BotCommand("info", "Información del bot"),
    ]
    await app.bot.set_my_commands(commands)

# ==============================
# FUNCIONES DE COMANDOS
# ==============================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hola 👋 Soy tu bot profesional en Python.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Comandos disponibles:\n"
        "/start - Iniciar\n"
        "/help - Ayuda\n"
        "/menu - Abrir menú\n"
        "/info - Información"
    )

async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Bot creado con Python y desplegado en Railway."
    )

# ==============================
# MENÚ CON BOTONES
# ==============================

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📊 Estado", callback_data="estado")],
        [InlineKeyboardButton("ℹ️ Info", callback_data="info")],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Selecciona una opción:",
        reply_markup=reply_markup
    )

# ==============================
# MANEJO DE BOTONES
# ==============================

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "estado":
        await query.edit_message_text(
            "✅ El bot está funcionando correctamente en Railway."
        )

    elif query.data == "info":
        await query.edit_message_text(
            "🤖 Bot avanzado con botones interactivos."
        )

# ==============================
# FUNCIÓN PRINCIPAL
# ==============================

async def main():
    app = ApplicationBuilder().token(TOKEN).build()

    # Registrar comandos
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("menu", menu))
    app.add_handler(CommandHandler("info", info))

    # Registrar botones
    app.add_handler(CallbackQueryHandler(button_handler))

    # Configurar comandos oficiales
    await set_commands(app)

    print("🚀 Bot funcionando correctamente...")

    await app.run_polling()

# ==============================
# EJECUCIÓN
# ==============================

if __name__ == "__main__":
    asyncio.run(main())
