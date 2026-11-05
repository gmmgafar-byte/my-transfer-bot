import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

# تفعيل تسجيل الأخطاء
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# ضع توكن البوت الكامل الذي حصلت عليه من BotFather هنا بين علامات التنصيص
TOKEN = "9211948848:AAHbnxnne8H7WG-toFOHxqhQYP4Gv64AAbg"

# نسبة العمولة للمبالغ التي تساوي أو تزيد عن 25,000 (1%)
COMMISSION_RATE = 0.01

# معرف حسابك الشخصي (Username) الذي سيتم توجيه المستخدمين إليه
YOUR_USERNAME = "g_w_6"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
  keyboard = [
    [
        InlineKeyboardButton("FIB ⬅️ زين كاش", callback_data="fib_to_zain"),
        InlineKeyboardButton("زين كاش ➡️ FIB", callback_data="zain_to_fib"),
    ],
    [
        InlineKeyboardButton("FIB ⬅️ سوبر كي", callback_data="fib_to_superqi"),
        InlineKeyboardButton("سوبر كي ➡️ FIB", callback_data="superqi_to_fib"),
    ],
    [
        InlineKeyboardButton(
            "زين كاش ⬅️ سوبر كي", callback_data="zain_to_superqi"
        ),
        InlineKeyboardButton(
            "سوبر كي ➡️ زين كاش", callback_data="superqi_to_zain"
        ),
    ],
  ]
  reply_markup = InlineKeyboardMarkup(keyboard)

  await update.message.reply_text(
      "مرحباً بك في بوت التحويلات المالية 💸\n\n"
      "يرجى اختيار مسار التحويل المطلوب:",
      reply_markup=reply_markup,
  )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
  query = update.callback_query
  await query.answer()

  context.user_data["transfer_type"] = query.data

  names = {
      "fib_to_zain": "FIB إلى زين كاش",
      "zain_to_fib": "زين كاش إلى FIB",
      "fib_to_superqi": "FIB إلى سوبر كي",
      "superqi_to_fib": "سوبر كي إلى FIB",
      "zain_to_superqi": "زين كاش إلى سوبر كي",
      "superqi_to_zain": "سوبر كي إلى زين كاش",
  }

  selected_name = names.get(query.data, "تحويل")

  await query.edit_message_text(
      text=f"لقد اخترت التحويل من: **{selected_name}**.\n\n"
      "الرجاء إرسال **المبلغ المراد تحويله** بالأرقام فقط:",
      parse_mode="Markdown",
  )


async def calculate_amount(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
  if "transfer_type" not in context.user_data:
    await update.message.reply_text(
        "الرجاء البدء من جديد عبر إرسال الأمر /start"
    )
    return

  text = update.message.text.replace(",", "")
  try:
    amount = float(text)
  except ValueError:
    await update.message.reply_text(
        "❌ عذراً، يرجى إرسال أرقام صحيحة فقط للمبلغ."
    )
    return

  # تطبيق شرط العمولة الجديد
  if amount < 25000:
    commission = 250.0
    commission_text = "250 (عمولة ثابتة للمبالغ أقل من 25,000)"
  else:
    commission = amount * COMMISSION_RATE
    commission_text = f"{commission:,.2f} (بنسبة 1%)"

  total_amount = amount + commission

  response = (
      f"🧮 **تفاصيل عملية التحويل:**\n\n"
      f"💵 المبلغ الأساسي: `{amount:,.2f}`\n"
      f"📊 قيمة العمولة: `{commission_text}`\n"
      f"━━━━━━━━━━━━━━━\n"
      f"💰 المبلغ الإجمالي للقطع: `{total_amount:,.2f}`\n\n"
      "اضغط على الزر أدناه لإرسال الرقم أو الإيصال للإدارة:"
  )

  # إنشاء زر يوجه المستخدم إلى صفحتك الشخصية مباشرة
  keyboard = [[InlineKeyboardButton("📩 إرسال الرقم/الإيصال للإدارة", url=f"https://t.me/{YOUR_USERNAME}")],
              [InlineKeyboardButton("🔄 تحويل جديد (/start)", callback_data="restart_bot")]]
  
  reply_markup = InlineKeyboardMarkup(keyboard)

  context.user_data.pop("transfer_type", None)

  await update.message.reply_text(response, parse_mode="Markdown", reply_markup=reply_markup)


def main() -> None:
  application = Application.builder().token(TOKEN).build()

  application.add_handler(CommandHandler("start", start))
  application.add_handler(CallbackQueryHandler(button_handler))
  application.add_handler(
      MessageHandler(filters.TEXT & ~filters.COMMAND, calculate_amount)
  )

  application.run_polling()


if __name__ == "__main__":
  main()
