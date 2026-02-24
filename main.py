from telegram import (
    Update,
    BotCommand,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters
)
import nest_asyncio
import asyncio
from datetime import datetime

nest_asyncio.apply()

TOKEN = "8730267318:AAHRhhemeVaEs0JHad0TPLi48gobyfxh7ls"

usuarios = {}
mensajes = []


# Menú
def menu_principal():
    teclado = [
        [
            InlineKeyboardButton("📞 Contacto", callback_data="contacto"),
            InlineKeyboardButton("🕒 Horario", callback_data="horario"),
        ],
        [
            InlineKeyboardButton("📍 Ubicación", callback_data="ubicacion"),
            InlineKeyboardButton("❓ Ayuda", callback_data="ayuda"),
        ]
    ]
    return InlineKeyboardMarkup(teclado)


# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user

    usuarios[user.id] = {
        "nombre": user.first_name,
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M")
    }

    await update.message.reply_text(
        f"Hola {user.first_name} 👋\n¿En qué te ayudo?",
        reply_markup=menu_principal()
    )


# Respuestas automáticas
def respuesta_auto(texto):

    texto = texto.lower()

    if "hola" in texto:
        return "Hola 👋 ¿Cómo estás?"

    if "precio" in texto or "costo" in texto:
        return "Nuestros precios empiezan desde $100 MXN 💰"

    if "horario" in texto:
        return "Atendemos de lunes a viernes, 9am a 6pm ⏰"

    if "direccion" in texto or "ubicacion" in texto:
        return "Estamos en Mérida, Yucatán 📍"

    if "gracias" in texto:
        return "¡Con gusto! 😊"

    return None


# Guardar y responder
async def manejar_mensaje(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user
    texto = update.message.text

    mensajes.append({
        "id": user.id,
        "texto": texto,
        "fecha": datetime.now().strftime("%H:%M")
    })

    respuesta = respuesta_auto(texto)

    if respuesta:
        await update.message.reply_text(respuesta)
    else:
        await update.message.reply_text(
            "No entendí 😅 Usa el menú o escribe 'ayuda'."
        )


# Botones
async def botones(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    if query.data == "contacto":
        texto = "📞 WhatsApp: 999-000-0000"

    elif query.data == "horario":
        texto = "🕒 L-V: 9am a 6pm"

    elif query.data == "ubicacion":
        texto = "📍 Mérida, Yucatán"

    elif query.data == "ayuda":
        texto = "Escribe: hola, precio, horario, ubicación"

    else:
        texto = "Opción inválida"

    await query.edit_message_text(texto)


async def main():

    app = ApplicationBuilder().token(TOKEN).build()

    await app.bot.set_my_commands([
        BotCommand("start", "Iniciar"),
    ])

    app.add_handler(CommandHandler("start", start))

    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, manejar_mensaje)
    )

    app.add_handler(CallbackQueryHandler(botones))

    print("🤖 Bot automático activo...")

    await app.run_polling()


asyncio.get_event_loop().run_until_complete(main())
