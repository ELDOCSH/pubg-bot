from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (ApplicationBuilder, CommandHandler, MessageHandler,
                          filters, ContextTypes, ConversationHandler, CallbackQueryHandler)

import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

ID, TYPE, AMOUNT, PAYMENT, SCREENSHOT = range(5)

WELCOME_MSG = """🎮 *أهلاً بيك في بوت شحن PUBG الرسمي!*

استخدم الأوامر التالية:

💰 /prices - عرض قائمة الأسعار
💳 /payment - طرق الدفع المتاحة
📝 /order - تقديم طلب شحن
🆘 /cancel - إلغاء الطلب
"""

PRICES_MSG = """💥 *عروض شحن PUBG* 💥

📲 *عن طريق تسجيل الدخول:*
8100 UC = 3800 جنيه
3850 UC = 1900 جنيه
1800 UC = 980 جنيه
660 UC = 410 جنيه
325 UC = 210 جنيه
60 UC = 50 جنيه

🌸 *الازدهار:*
1$ = 55 جنيه
3$ = 140 جنيه
5$ = 210 جنيه
برايم بلس = 450 جنيه
برايم عادي = 65 جنيه

🇰🇷 *ببجي الكورية (تسجيل دخول):*
60 = 55 / 180 = 145 / 310 = 245 / 380 = 280
660 = 450 / 1800 = 1125 / 3850 = 2200 / 8100 = 4350

🎯 *عن طريق ID فقط:*
8100 = 4350 / 3850 = 2175 / 1800 = 1125
660 = 460 / 325 = 240 / 60 = 55
"""

PAYMENT_MSG = """💳 *طرق الدفع:*

📱 *كاش اتصالات:*
`01120799753`

📱 *كاش فودافون:*
`01028819650`
`01066412453`

💳 *إنستاباي:*
`Ahmed436587`

🏦 *Binance:*
ID: 77910757
AhmedEldocsh

🔄 نقبل الدفع بأي عملة من داخل أو خارج مصر
📩 للتحويل بالعملة الأجنبية، تواصل معنا على الخاص
📸 ابعت سكرين في إيدك يا غالي ❤️
"""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[
        InlineKeyboardButton("📦 الأسعار", callback_data='prices'),
        InlineKeyboardButton("💳 الدفع", callback_data='payment')
    ], [
        InlineKeyboardButton("📝 اطلب شحن", callback_data='order')
    ]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_markdown_v2(WELCOME_MSG, reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == 'prices':
        await query.edit_message_text(PRICES_MSG, parse_mode='Markdown')
    elif data == 'payment':
        await query.edit_message_text(PAYMENT_MSG, parse_mode='Markdown')
    elif data == 'order':
        await query.edit_message_text("📌 اكتب *ID اللعبة*:", parse_mode='Markdown')
        return ID

async def prices(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_markdown_v2(PRICES_MSG)

async def payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_markdown_v2(PAYMENT_MSG)

async def order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📌 اكتب ID اللعبة:")
    return ID

async def get_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['id'] = update.message.text
    await update.message.reply_text("📱 نوع الشحن؟ (ID / تسجيل دخول / كوري):")
    return TYPE

async def get_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['type'] = update.message.text
    await update.message.reply_text("💎 الكمية المطلوبة؟")
    return AMOUNT

async def get_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['amount'] = update.message.text
    await update.message.reply_text("💰 وسيلة الدفع المستخدمة:")
    return PAYMENT

async def get_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['payment'] = update.message.text
    await update.message.reply_text("📸 ابعت صورة التحويل (سكرين):")
    return SCREENSHOT

async def get_screenshot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo_id = update.message.photo[-1].file_id if update.message.photo else "لا يوجد صورة"
    context.user_data['screenshot'] = photo_id

    order_summary = f"""📩 *طلب شحن جديد:*

👤 ID اللعبة: {context.user_data['id']}
📱 النوع: {context.user_data['type']}
💎 الكمية: {context.user_data['amount']}
💰 الدفع: {context.user_data['payment']}
📸 صورة: {'موجودة' if photo_id != 'لا يوجد صورة' else 'لا يوجد'}
"""

    await context.bot.send_message(chat_id=ADMIN_ID, text=order_summary, parse_mode='Markdown')
    if photo_id != "لا يوجد صورة":
        await context.bot.send_photo(chat_id=ADMIN_ID, photo=photo_id)

    await update.message.reply_text("✅ تم إرسال الطلب بنجاح! سيتم التواصل معك قريبًا.")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ تم إلغاء الطلب.")
    return ConversationHandler.END

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("order", order)],
        states={
            ID: [MessageHandler(filters.TEXT, get_id)],
            TYPE: [MessageHandler(filters.TEXT, get_type)],
            AMOUNT: [MessageHandler(filters.TEXT, get_amount)],
            PAYMENT: [MessageHandler(filters.TEXT, get_payment)],
            SCREENSHOT: [MessageHandler(filters.PHOTO | filters.TEXT, get_screenshot)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("prices", prices))
    app.add_handler(CommandHandler("payment", payment))
    app.add_handler(CommandHandler("cancel", cancel))
    app.add_handler(CommandHandler("order", order))
    app.add_handler(conv_handler)
    app.add_handler(CallbackQueryHandler(button_handler))

    app.run_polling()

if __name__ == '__main__':
    main()

