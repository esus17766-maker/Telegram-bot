import os
import asyncio
import sqlite3
from datetime import datetime
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

# =====================================
# CONFIGURACIÓN
# =====================================

TOKEN = os.getenv("TOKEN")
ADMIN_ID = 123456789  # 🔴 REEMPLAZA CON TU ID REAL

# =====================================
# BASE DE DATOS
# =====================================

def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        username TEXT,
        first_name TEXT,
        created_at TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        product_id TEXT,
        status TEXT,
        created_at TEXT
    )
    """)

    conn.commit()
    conn.close()

def register_user(user):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
    INSERT OR IGNORE INTO users (id, username, first_name, created_at)
    VALUES (?, ?, ?, ?)
    """, (user.id, user.username, user.first_name, datetime.now()))

    conn.commit()
    conn.close()

def create_order(user_id, product_id):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO orders (user_id, product_id, status, created_at)
    VALUES (?, ?, ?, ?)
    """, (user_id, product_id, "pending", datetime.now()))

    conn.commit()
    conn.close()

# =====================================
# PRODUCTOS
# =====================================

PRODUCTS = {
    "video1": {
        "name": "🔥 Video Exclusivo #1",
        "price": "$10",
        "file": "video1.mp4"
    },
    "pack1": {
        "name": "💎 Pack Premium",
        "price": "$25",
        "file": "pack1.zip"
    }
}

# =====================================
# COMANDOS GENERALES
# =====================================

async def set_commands(app):
    commands = [
        BotCommand("start", "Iniciar"),
        BotCommand("menu", "Ver catálogo"),
        BotCommand("id", "Ver mi ID"),
    ]
    await app.bot.set_my_commands(commands)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    register_user(update.effective_user)

    await update.message.reply_text(
        "🔥 Bienvenida al contenido exclusivo.\n\n"
        "Usa /menu para ver el catálogo."
    )

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = []

    for product_id, product in PRODUCTS.items():
        keyboard.append([
            InlineKeyboardButton(
                f"{product['name']} - {product['price']}",
                callback_data=f"buy_{product_id}"
            )
        ])

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Selecciona el contenido que deseas comprar:",
        reply_markup=reply_markup
    )

async def get_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"Tu ID es: {update.effective_user.id}"
    )

# =====================================
# BOTONES DE COMPRA
# =====================================

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data.startswith("buy_"):
        product_id = query.data.replace("buy_", "")
        product = PRODUCTS[product_id]

        create_order(query.from_user.id, product_id)

        await query.edit_message_text(
            f"Has seleccionado:\n\n"
            f"{product['name']}\n"
            f"Precio: {product['price']}\n\n"
            "Realiza el pago y envía el comprobante aquí."
        )

        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"🛒 Nuevo pedido pendiente\n"
                 f"Usuario: {query.from_user.id}\n"
                 f"Producto: {product['name']}"
        )

# =====================================
# PANEL ADMIN
# =====================================

async def aprobar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    order_id = int(context.args[0])

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("SELECT user_id, product_id FROM orders WHERE id=?", (order_id,))
    order = cursor.fetchone()

    if not order:
        await update.message.reply_text("Pedido no encontrado.")
        return

    user_id, product_id = order

    cursor.execute("UPDATE orders SET status='approved' WHERE id=?", (order_id,))
    conn.commit()
    conn.close()

    product = PRODUCTS[product_id]

    await context.bot.send_message(
        chat_id=user_id,
        text="✅ Pago confirmado. Aquí tienes tu contenido:"
    )

    await context.bot.send_document(
        chat_id=user_id,
        document=open(product["file"], "rb")
    )

    await update.message.reply_text("Pedido aprobado y contenido enviado.")

# =====================================
# MAIN
# =====================================

async def main():
    init_db()

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("menu", menu))
    app.add_handler(CommandHandler("id", get_id))
    app.add_handler(CommandHandler("aprobar", aprobar))
    app.add_handler(CallbackQueryHandler(button_handler))

    await set_commands(app)

    print("🚀 Bot profesional activo...")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
