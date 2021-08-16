import telebot
from telebot import types
import datetime
import locale
from main import db, Day, Region, User
from PIL import Image, ImageDraw, ImageFont
import requests

locale.setlocale(locale.LC_TIME, 'uz_UZ')
bot = telebot.TeleBot("TOKEN")

ROWS_PER_PAGE = 6


def draw_picture(s, f, d):
    img = Image.open("img.png")
    i = ImageDraw.Draw(img)
    font = ImageFont.truetype('fonts/Roboto-Light.ttf', 36)
    font2 = ImageFont.truetype('fonts/vivaldi.ttf', 74)
    i.text((95, 396), s, font=font, fill=(248, 248, 248))
    i.text((423, 396), f, font=font, fill=(248, 248, 248))
    i.text((220, 205), d.lower(), font=font2, fill=(252, 244, 244))
    return img


@bot.message_handler(commands=['start'])
def start(message):
    user = User.query.filter_by(user_id=message.chat.id).first()
    if user is None:
        new_user = User(user_id=message.chat.id)
        db.session.add(new_user)
        db.session.commit()
    time = datetime.datetime.now()
    first_day = Day.query.order_by(Day.id).first().saharlik
    last_day = Day.query.order_by(Day.id.desc()).first().saharlik
    if time > last_day:
        img = requests.get('https://imgur.com/iHywgEE.jpg').content
        text = "2021-yildagi Ramazon oyi nihoyasiga yetdi! Barchamizning iltijolarimiz qabul bo'lsin! 😊"
    elif time < first_day:
        img = requests.get('https://imgur.com/iHywgEE.jpg').content
        text = "2021-yildagi Ramazon oyi Boshlanishiga sanoqli kunlar qoldi! Olloh o'zi sizga sabr bersin! 😊 "
    else:
        post = Day.query.filter(Day.saharlik <= time).order_by(Day.id.desc()).first()
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(types.InlineKeyboardButton("🗺 Viloyatni tanlash", callback_data='regions#1'),
                   types.InlineKeyboardButton("➡️ Ertaga", callback_data=f'tomorrow#{post.id}'))
        img = draw_picture(post.saharlik.strftime('%H:%M'), post.iftorlik.strftime('%H:%M'), time.strftime('%d-%B'))
        text = (f"<b>Assalomu alaykum va rahmatullohi va barakotuh!</b>\n\n"
                "🌙 Ramazon oyingiz muborak bo'lsin<a href='https://imgur.com/tJD0tAM.jpg'>,</a> "
                "Ramazon oyi munosabati bilan <a href='https://t.me/UzRoboUp'>UzRoboUP IT jamoasi</a> o'z "
                "kuzatuvchilariga kichik tuhfa sifatida "
                "taqvimni Telegram Bot ko'rinishida taqdim etadi\n\n"
                f"<b>Bugun sana: {time.strftime('%d-%B')}, Ro'zaning {post.id}-kuni.</b>\n\n"
                f"<i>Bugungi saharlik vaqti: {post.saharlik.strftime('%H:%M')}\nIftor vaqti: {post.iftorlik.strftime('%H:%M')}</i>\n\n<b>* Bu vaqt Toshkent shahri bo'yicha amal qiladi!</b>\n")
    bot.send_photo(message.chat.id,
                   photo=img,
                   caption=text,
                   parse_mode="HTML", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.message:
        if call.data.startswith('tomorrow#'):
            day_id = int(call.data.split('#')[1]) + 1
            post = Day.query.filter_by(id=day_id).first()
            markup = types.InlineKeyboardMarkup(row_width=2)
            markup.add(types.InlineKeyboardButton("🗺 Viloyatni tanlash", callback_data='regions#1'))
            img = draw_picture(post.saharlik.strftime('%H:%M'), post.iftorlik.strftime('%H:%M'), post.iftorlik.strftime('%d-%B'))
            text = (f"<b>Sana: {post.saharlik.strftime('%d-%B')}, Haftaning {post.day.lower()} kuni, Ro'zaning {post.id}-kuni.</b>\n\n"
                    f"<i>Bugungi saharlik vaqti: {post.saharlik.strftime('%H:%M')}\nIftor vaqti: {post.iftorlik.strftime('%H:%M')}</i>\n\n<b>* Bu vaqt Toshkent shahri bo'yicha amal qiladi!</b>\n")
            bot.edit_message_media(media=types.InputMediaPhoto(img, caption=text, parse_mode="HTML"), chat_id=call.message.chat.id, message_id=call.message.message_id)
            bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup)
        if call.data.startswith('regions#'):
            page = int(call.data.split("#")[1])
            regions = Region.query.paginate(page=page, per_page=ROWS_PER_PAGE)
            markup = types.InlineKeyboardMarkup(row_width=2)
            for i in regions.items:
                markup.add(types.InlineKeyboardButton(i.name, callback_data=f"region#{i.id}"))
            if not page == regions.pages:
                markup.add(types.InlineKeyboardButton("▶️ Keyingi sahifa", callback_data=f"regions#{page+1}"))
            if not page == 1:
                markup.add(types.InlineKeyboardButton("◀️ Avvlagi sahifa", callback_data=f"regions#{page - 1}"))
            bot.edit_message_caption(chat_id=call.message.chat.id, message_id=call.message.message_id, caption="<b>Siz yashaydigan hududni tanlang: </b>", reply_markup=markup, parse_mode="HTML")
        if call.data.startswith('region#'):
            markup = types.InlineKeyboardMarkup(row_width=1)
            markup.add(types.InlineKeyboardButton("🗺 Viloyatni tanlash", callback_data="regions#1"))
            region_id = int(call.data.split("#")[1])
            time = datetime.datetime.now()
            region = Region.query.filter_by(id=region_id).first()
            post = Day.query.filter(Day.saharlik <= time).order_by(Day.id.desc()).first()
            region_difference = region.different
            post_saharlik_year = int(post.saharlik.strftime("%Y"))
            post_saharlik_month = int(post.saharlik.strftime("%m"))
            post_saharlik_day = int(post.saharlik.strftime("%d"))
            post_saharlik_hour = int(post.saharlik.strftime("%H"))
            post_saharlik_minutes = int(post.saharlik.strftime("%M"))
            region_saharlik_time = datetime.datetime(year=post_saharlik_year, month=post_saharlik_month, day=post_saharlik_day, hour=post_saharlik_hour, minute=post_saharlik_minutes, second=0)
            if region_difference > 0:
                region_saharlik_time = region_saharlik_time + datetime.timedelta(minutes=abs(region_difference))
            else:
                region_saharlik_time = region_saharlik_time - datetime.timedelta(minutes=abs(region_difference))
            post_iftorlik_year = int(post.iftorlik.strftime("%Y"))
            post_iftorlik_month = int(post.iftorlik.strftime("%m"))
            post_iftorlik_day = int(post.iftorlik.strftime("%d"))
            post_iftorlik_hour = int(post.iftorlik.strftime("%H"))
            post_iftorlik_minutes = int(post.iftorlik.strftime("%M"))
            region_iftorlik_time = datetime.datetime(year=post_iftorlik_year, month=post_iftorlik_month, day=post_iftorlik_day, hour=post_iftorlik_hour, minute=post_iftorlik_minutes, second=0)
            if region_difference > 0:
                region_iftorlik_time = region_iftorlik_time + datetime.timedelta(minutes=abs(region_difference))
            else:
                region_iftorlik_time = region_iftorlik_time - datetime.timedelta(minutes=abs(region_difference))
            img = draw_picture(region_saharlik_time.strftime('%H:%M'), region_iftorlik_time.strftime('%H:%M'), time.strftime('%d-%B'))
            text = (f"""<i>{region.name} uchun saharlik va iftorlik vaqtlari</i>
            
<b>Sana: {time.strftime('%d-%B')}, Haftaning {post.day.lower()} kuni, Ro'zaning {post.id}-kuni.</b>

<i>Bugungi saharlik vaqti: {region_saharlik_time.strftime('%H:%M')}
Iftor vaqti: {region_iftorlik_time.strftime('%H:%M')}</i>
""")
            bot.edit_message_media(media=types.InputMediaPhoto(img, caption=text, parse_mode="HTML"),
                                   chat_id=call.message.chat.id, message_id=call.message.message_id)
            bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                          reply_markup=markup)


bot.polling(none_stop=True)
