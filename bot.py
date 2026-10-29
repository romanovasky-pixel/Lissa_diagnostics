import os
import threading
import telebot
from telebot import types
from telebot.apihelper import ApiTelegramException

BOT_TOKEN = os.getenv("BOT_TOKEN", "9275626458:AAFKTK5kJoRfy-lxbZcWoGEJ8HNtxsTVVC0")
# После /revoke в @BotFather укажите токен в переменной окружения BOT_TOKEN на Bothost.

CHANNEL_ID = "@lissa_ai_m"
CHANNEL_LINK = "https://t.me/lissa_ai_m"
GAME_LINK = "https://t.me/LissaAibot_bot"

REMINDER_DELAY_SEC = 15 * 60  # 15 минут

WELCOME_TEXT = """🦊 Привет! Я подготовила для тебя «Диагностику масштаба» — технику, которая покажет, на каком уровне твой мозг начинает сопротивляться.

Но сначала давай договоримся: файл доступен только подписчикам моего канала. Там я пишу мысли о целях и дисциплине, которые не влезают в Instagram.

👇 Нажми кнопку ниже, чтобы подписаться, а потом возвращайся сюда за диагностикой."""

REMINDER_TEXT = """🦊 Кстати, диагностика уже ждёт тебя в канале!

Ты заглядывала, но подписка ещё не подтвердилась. Подпишись и нажми «Проверить подписку» — и я сразу пришлю материал."""

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

# user_id -> True, если напоминание уже отправлено или не нужно
_reminded = set()
_lock = threading.Lock()


def is_subscribed(user_id: int) -> bool:
    try:
        member = bot.get_chat_member(CHANNEL_ID, user_id)
        return member.status in ("member", "administrator", "creator")
    except ApiTelegramException:
        return False


def send_reminder_later(chat_id: int, user_id: int):
    def worker():
        timer = threading.Timer(REMINDER_DELAY_SEC, _send_reminder, args=(chat_id, user_id))
        timer.daemon = True
        timer.start()

    threading.Thread(target=worker, daemon=True).start()


def _send_reminder(chat_id: int, user_id: int):
    with _lock:
        if user_id in _reminded:
            return
        _reminded.add(user_id)

    if is_subscribed(user_id):
        return  # уже подписался — не беспокоим

    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("📢 Подписаться на канал", url=CHANNEL_LINK),
        types.InlineKeyboardButton("✅ Проверить подписку", callback_data="check"),
    )
    try:
        bot.send_message(chat_id, REMINDER_TEXT, reply_markup=markup)
    except ApiTelegramException:
        pass  # пользователь заблокировал бота или чат недоступен


def main_menu_markup() -> types.InlineKeyboardMarkup:
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("📢 Подписаться на канал", url=CHANNEL_LINK),
        types.InlineKeyboardButton("✅ Я подписалась — получить диагностику", callback_data="check"),
    )
    return markup


def after_gift_markup() -> types.InlineKeyboardMarkup:
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("🦊 Хочу в игру «Лисса.Ai: Эволюция»", url=GAME_LINK),
    )
    return markup


@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(message.chat.id, WELCOME_TEXT, reply_markup=main_menu_markup())


@bot.callback_query_handler(func=lambda call: call.data == "check")
def check_sub(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id

    if is_subscribed(user_id):
        with _lock:
            _reminded.add(user_id)  # отменяем напоминание
        bot.answer_callback_query(call.id, "Подписка подтверждена!")
        bot.send_message(chat_id, LEAD_MAGNET_TEXT, reply_markup=after_gift_markup(), disable_web_page_preview=False)
        try:
            bot.edit_message_reply_markup(chat_id, call.message.message_id, reply_markup=None)
        except ApiTelegramException:
            pass
    else:
        bot.answer_callback_query(
            call.id,
            "Вы ещё не подписались на канал ❌",
            show_alert=True,
        )
        send_reminder_later(chat_id, user_id)


if __name__ == "__main__":
    bot.infinity_polling()
