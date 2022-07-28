import os
import textwrap

import django
from django.core.exceptions import ObjectDoesNotExist
from dotenv import load_dotenv
from telegram import (KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove,
                      Update)
from telegram.ext import (CallbackContext, CommandHandler, ConversationHandler,
                          Filters, MessageHandler, Updater)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'meetup.settings')
django.setup()

from bot.models import Event, EventGroup, Profile, Question, Presentation


MAIN_MENU_CHOICE, \
    EVENT_GROUP_CHOICE, \
    EVENT_CHOICE, \
    QUESTION, \
    SAVE_QUESTION, \
    ANSWER = range(6)

MAIN_MENU_BUTTON_CAPTION = 'Главное меню'
BACK_BUTTON_CAPTION = 'Назад'


def start(update: Update, context: CallbackContext) -> int:
    """Send a message when the command /start is issued."""
    tg_user = update.effective_user
    user_profile, _ = Profile.objects.get_or_create(
        telegram_id=tg_user['id'],
        defaults={
            'name': tg_user['first_name'],
            'telegram_username': tg_user['username'],
        })

    keyboard = [[KeyboardButton('Программа'), KeyboardButton('Задать вопрос')]]
    if user_profile.is_speaker:
        keyboard.append([KeyboardButton('Ответить на вопрос')])
    markup = ReplyKeyboardMarkup(
        keyboard=keyboard, resize_keyboard=True, one_time_keyboard=True)

    update.message.reply_text(
        f'Привет {user_profile.name}', reply_markup=markup)

    return MAIN_MENU_CHOICE


def choose_event_group(update: Update, context: CallbackContext) -> int:
    """Ask the user to select an event group"""
    groups = EventGroup.objects.all()
    buttons = [[KeyboardButton(group.title) for group in groups]]
    buttons.append([KeyboardButton(MAIN_MENU_BUTTON_CAPTION)])
    markup = ReplyKeyboardMarkup(
        keyboard=buttons, resize_keyboard=True, one_time_keyboard=True)
    update.message.reply_text('Какая секция?', reply_markup=markup)

    return EVENT_GROUP_CHOICE


def choose_event(update: Update, context: CallbackContext) -> int:
    """Ask the user to select an event"""
    events = Event.objects.filter(event_group__title=update.message.text)
    if not events:
        return start(update, context)
    num_cols = 2
    buttons = []
    row = []
    for event in events:
        row.append(
            KeyboardButton(
                f'{event.time_from:%H:%M} {event.title}'
            )
        )
        if len(row) == num_cols:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    buttons.append([KeyboardButton(BACK_BUTTON_CAPTION)])
    markup = ReplyKeyboardMarkup(
        keyboard=buttons, resize_keyboard=True)
    update.message.reply_text('Какое мероприятие?', reply_markup=markup)

    return EVENT_CHOICE


def show_event(update: Update, context: CallbackContext) -> int:
    """Show event description"""
    event_title = update.message.text[6:]
    presentations = Presentation.objects \
        .filter(event__title=event_title) 
    if not presentations:
        return start(update, context)

    text_blocks = [
        f'<b><i>{presentations[0].event}</i></b>\n',
    ]
    for presentation in presentations:
        text_blocks.append(
            f'<b>{presentation.title}</b>\n{presentation.speaker}\n',
        )
    update.message.reply_html('\n'.join(text_blocks))

    return EVENT_CHOICE


def ask_question(update, context):
    text = 'Задайте вопрос спикеру'
    context.user_data['questioner_id'] = update.message.chat.id
    context.user_data['question'] = update.message.text
    update.message.reply_text(text)

    return SAVE_QUESTION


def save_question(update, context):
    print(context.user_data['event'])
    text = 'Ваш вопрос направлен спикеру'
    Question.objects.get_or_create(
        event=context.user_data['event'],
        text=update.message.text,
        listener=Profile.objects.get(
            telegram_id=context.user_data['questioner_id'])
    )
    buttons = [KeyboardButton('Задать новый вопрос')]
    reply_markup = ReplyKeyboardMarkup(
        keyboard=[buttons],
        resize_keyboard=True,
        one_time_keyboard=True)
    update.message.reply_text(
        text,
        reply_markup=reply_markup
    )

    return QUESTION


def new_question_from_the_speaker(update, context):
    speaker_id = update.message.chat.id
    question = get_questions_from_the_speaker(speaker_id)
    context.user_data['question'] = question
    buttons = [
        KeyboardButton('Пропустить'),
        KeyboardButton(MAIN_MENU_BUTTON_CAPTION),
    ]
    reply_markup = ReplyKeyboardMarkup(
        keyboard=[buttons],
        resize_keyboard=True,
        one_time_keyboard=True)
    update.message.reply_text(
        question.text,
        reply_markup=reply_markup
    )
    return ANSWER


def get_questions_from_the_speaker(speaker_id: str) -> list:
    speaker = Profile.objects.get(telegram_id=speaker_id)
    presentation = Presentation.objects.get(speaker=speaker)
    question = Question.objects.filter(
        presentation=presentation).filter(is_active=True)[0]
    return question


def answer_the_question(update, context):
    listener_id = context.user_data['question'].listener.telegram_id
    context.bot.send_message(chat_id=listener_id, text=update.message.text)


def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('SOS!')


def main() -> None:
    """Start the bot."""
    load_dotenv()
    tg_token = os.getenv("TG_TOKEN")

    updater = Updater(tg_token)
    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler('start', start),
        ],
        states={
            MAIN_MENU_CHOICE: [
                MessageHandler(Filters.regex('^Программа$'),
                               choose_event_group),
                MessageHandler(Filters.regex('^Задать вопрос$'),
                               ask_question),
                MessageHandler(Filters.regex('^Ответить на вопрос$'),
                               new_question_from_the_speaker),
            ],
            EVENT_GROUP_CHOICE: [
                MessageHandler(Filters.regex(f'^{MAIN_MENU_BUTTON_CAPTION}$'),
                               start),
                MessageHandler(Filters.text,
                               choose_event),
            ],
            EVENT_CHOICE: [
                MessageHandler(Filters.regex(f'^{BACK_BUTTON_CAPTION}$'),
                               choose_event_group),
                MessageHandler(Filters.text,
                               show_event),
            ],
            QUESTION: [
                MessageHandler(Filters.regex('^Задать вопрос$'), ask_question),
                MessageHandler(Filters.regex(
                    '^Задать новый вопрос$'), ask_question),
            ],
            SAVE_QUESTION: [
                MessageHandler(Filters.text, save_question),
            ],
            ANSWER: [
                MessageHandler(Filters.text, answer_the_question)
            ],
        },
        fallbacks=[CommandHandler('start', start)],
        per_user=True,
        per_chat=True,
        allow_reentry=True
    )

    dispatcher.add_handler(conv_handler)
    dispatcher.add_handler(CommandHandler("help", help_command))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
