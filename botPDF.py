from telegram import Update, InputFile
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from PIL import Image
import os
import tempfile
import shutil

# دیکشنری برای ذخیره عکس‌های هر کاربر
user_images = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! این یک ربات برای تبدیل عکس‌ها به فایل PDF است. لطفاً عکس‌های خود را ارسال کنید و در نهایت نام فایل PDF را وارد نمایید.")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    
    # ایجاد پوشه موقت برای کاربر اگر وجود ندارد
    if user_id not in user_images:
        user_images[user_id] = {
            'temp_dir': tempfile.mkdtemp(),
            'photos': []
        }
    
    try:
        photo = update.message.photo[-1]  # آخرین کیفیت عکس
        file = await photo.get_file()

        # ذخیره عکس با ترتیب صحیح
        file_index = len(user_images[user_id]['photos'])
        file_path = os.path.join(user_images[user_id]['temp_dir'], f"{file_index:04d}.jpg")
        await file.download_to_drive(file_path)

        # ذخیره مسیر عکس
        user_images[user_id]['photos'].append(file_path)

        await update.message.reply_text(f"📸 عکس {len(user_images[user_id]['photos'])} ذخیره شد! عکس‌های بیشتری ارسال کنید یا نام فایل PDF را وارد نمایید.")
    
    except Exception as e:
        await update.message.reply_text("❌ خطایی در پردازش عکس رخ داد. لطفاً مجدداً تلاش کنید.")
        print(f"Error processing photo: {e}")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    file_name = update.message.text.strip()
    
    if user_id not in user_images or not user_images[user_id]['photos']:
        await update.message.reply_text("لطفاً ابتدا عکس‌های خود را ارسال کنید و سپس نام فایل را وارد نمایید.")
        return
    
    try:
        # اطمینان از پسوند PDF
        if not file_name.lower().endswith('.pdf'):
            file_name += '.pdf'
        
        # ساخت PDF
        photos = user_images[user_id]['photos']
        images = [Image.open(img).convert("RGB") for img in photos]
        
        pdf_path = os.path.join(user_images[user_id]['temp_dir'], file_name)
        images[0].save(pdf_path, save_all=True, append_images=images[1:])
        
        # ارسال PDF به کاربر
        await update.message.reply_document(
            document=InputFile(pdf_path, filename=file_name),
            caption=f"فایل PDF شما با نام '{file_name}' آماده است."
        )
        
    except Exception as e:
        await update.message.reply_text("❌ خطایی در ایجاد فایل PDF رخ داد. لطفاً مجدداً تلاش کنید.")
        print(f"Error creating PDF: {e}")
    
    finally:
        # پاکسازی بدون توجه به موفقیت یا شکست
        if user_id in user_images:
            try:
                shutil.rmtree(user_images[user_id]['temp_dir'])
            except:
                pass
            del user_images[user_id]

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id in user_images:
        try:
            shutil.rmtree(user_images[user_id]['temp_dir'])
        except:
            pass
        del user_images[user_id]
        await update.message.reply_text("عملیات کنسل شد و تمام عکس‌های ارسالی پاک شدند.")
    else:
        await update.message.reply_text("هیچ عملیاتی در حال انجام نیست.")

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"Update {update} caused error {context.error}")
    try:
        await update.message.reply_text("❌ متأسفانه خطایی رخ داده است. لطفاً مجدداً تلاش کنید.")
    except:
        pass

def main():
    # ایجاد توکن از محیط یا به صورت مستقیم (برای تست)
    token = os.getenv("8463897398:AAFTYG-3ViOjRfuvESko9iOikiCVWT-k1dE")
    app = Application.builder().token(os.getenv(token)).build()
    
    # اضافه کردن هندلرها
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("cancel", cancel))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    # اضافه کردن هندلر خطا
    app.add_error_handler(error_handler)
    
    print("ربات در حال اجرا است...")
    app.run_polling()

if __name__ == "__main__":
    main()