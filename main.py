import time
from utils import *
import locale

# Set Language
locale.setlocale(locale.LC_TIME, 'uz_UZ')


@bot.message_handler(commands=['start'])
def send_welcome(message):
    time = datetime.datetime.now().strftime('%d-%B')
    text = (f"<b>Assalomu alaykum va rahmatullohi va barakotuh!</b>\n\n"
            "🌙 Ramazon oyingiz muborak bo'lsin, "
            "Ramazon oyi munosabati bilan <a href='https://t.me/UzRoboUp'>UzRoboUP IT jamoasi</a> o'z "
            "kuzatuvchilariga kichik tuhfa sifatida "
            "taqvimni Telegram Bot ko'rinishida taqdim etadi\n\n"
            f"<b>Bugun sana: {time}</b>")
    bot.send_message(message.chat.id,
                     text=text,
                     parse_mode="HTML", disable_web_page_preview=True)


bot.remove_webhook()

time.sleep(0.1)

# Set webhook
bot.set_webhook(url='https://amurodov2005.pythonanywhere.com/1721163869:AAGwE_mvTiwzITGsYK9najKI2U2yKLv5MHY')

if __name__ == "__main__":
    app.run(debug=True, host='https://amurodov2005.pythonanywhere.com/')
