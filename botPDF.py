from telegram import Update, InputFile
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from PIL import Image
import os


# دیکشنری برای ذخیره عکس‌های هر کاربر
user_images = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! این یک بیوتیکی برای تبدیل فایل PDF به فایل JPG است.")
    
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    photo = update.message.photo[-1] # آخرین کیفیت عکس
    file = await photo.get_file()

    file_path = f"images/{user_id}_{photo.file_unique_id}.jpg"
    await file.download_to_drive(file_path)

    # ذخیره مسیر عکس در لیست مربوط به کاربر
    if user_id not in user_images:
        user_images[user_id] = []
    user_images[user_id].append(file_path)

    await update.message.reply_text("📸 عکس ذخیره شد! ادامه بده یا اسم PDF رو بفرست.")    


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    file_name = update.message.text.strip()
    
    if user_id not in user_images or not user_images[user_id]:
        await update.message.reply_text(" اول عکس‌هاتو بفرست بعد اسم فایلو بده مهندس")
        return
    
    # ساخت PDF
    images = [Image.open(img).convert("RGB") for img in user_images[user_id]]
    pdf_path = f"{file_name}.pdf"
    images[0].save(pdf_path, save_all=True, append_images=images[1:])
    
    
    # ارسال PDF به کاربر
    await update.message.reply_document(InputFile(pdf_path))
    
    # پاکسازی
    for img in user_images[user_id]:
        os.remove(img)
    del user_images[user_id]
    os.remove(pdf_path)

def main():
    app = Application.builder().token("8463897398:AAFTYG-3ViOjRfuvESko9iOikiCVWT-k1dE").build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.run_polling()

if __name__ == "__main__":
    main()