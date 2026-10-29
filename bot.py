import os
import telebot
from telebot import types
from telebot.apihelper import ApiTelegramException

BOT_TOKEN = os.getenv("BOT_TOKEN", "9275626458:AAFKTK5kJoRfy-lxbZcWoGEJ8HNtxsTVVC0")
# После /revoke в @BotFather укажите токен в переменной окружения BOT_TOKEN на Bothost.

CHANNEL_ID = "@lissa_ai_m"
CHANNEL_LINK = "https://t.me/lissa_ai_m"

WELCOME_TEXT = """🦊 Привет! Я подготовила для тебя «Диагностику масштаба» — технику, которая покажет, на каком уровне твой мозг начинает сопротивляться.

Но сначала давай договоримся: файл доступен только подписчикам моего канала. Там я пишу мысли о целях и дисциплине, которые не влезают в Instagram.

👇 Нажми кнопку ниже, чтобы подписаться, а потом возвращайся сюда за диагностикой."""

LEAD_MAGNET_TEXT = """🎁 Твой подарок: Диагностика масштаба

Часто мы ставим слишком «безопасные» цели, потому что боимся замахнуться на большее. Наш мозг защищает нас от разочарований, выбирая привычное.

Но именно масштаб цели определяет масштаб твоих действий.

Давай проверим твой настоящий масштаб. Возьми лист бумаги или открой заметки и напиши 4 списка целей:

💰 На 100 000 ₽
(Что я куплю или сделаю на эти деньги?)

💰 На 500 000 ₽

💰 На 1 000 000 ₽

💰 На 10 000 000 ₽

Напротив каждой цели напиши, что изменится в тебе, когда ты этого достигнешь.

А теперь главный вопрос: какой из этих списков было писать страшнее всего? Именно там и находится твой настоящий потенциал.

_____________________

🦊 Если ты хочешь не просто написать список, а превратить эти цифры в реальность — я создала игру «Лисса.Ai: Эволюция».

Внутри: гайд «От глобального к локальному», рабочая тетрадь на 30 дней и закрытый канал с ежедневной мотивацией.

👇 Начать свой путь можно прямо здесь:
https://t.me/LissaAibot_bot"""

bot = telebot.TeleBot(BOT_TOKEN)


def is_subscribed(user_id: int) -> bool:
    try:
        member = bot.get_chat_member(CHANNEL_ID, user_id)
        return member.status in ("member", "administrator", "creator")
    except ApiTelegramException:
        return False


@bot.message_handler(commands=["start"])
def start(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("📢 Подписаться на канал", url=CHANNEL_LINK),
        types.InlineKeyboardButton("✅ Я подписалась — получить диагностику", callback_data="check"),
    )
    bot.send_message(message.chat.id, WELCOME_TEXT, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == "check")
def check_sub(call):
    user_id = call.from_user.id

    if is_subscribed(user_id):
        bot.answer_callback_query(call.id, "Подписка подтверждена!")
        bot.send_message(call.message.chat.id, LEAD_MAGNET_TEXT, disable_web_page_preview=False)
        try:
            bot.edit_message_reply_markup(
                call.message.chat.id,
                call.message.message_id,
                reply_markup=None,
            )
        except ApiTelegramException:
            pass
    else:
        bot.answer_callback_query(
            call.id,
            "Вы ещё не подписались на канал ❌",
            show_alert=True,
        )


if __name__ == "__main__":
    bot.infinity_polling()
