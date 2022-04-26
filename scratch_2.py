import logging
from datetime import datetime
from telegram.ext import *
from telegram import *
from dnevnikru import Dnevnik
from collections import Counter

login = "andreyevsergey2005"
password = "setinov5"

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

logger = logging.getLogger(__name__)

TOKEN = '5225353944:AAGfXO0TWaKkrBJFakBbJ6LyHwFFOGyQeiY'

dn = 0   # Dnevnik(login=login, password=password)

reply_keyboard = [['Домашние задания на завтра'],
                  ['Расписание на неделю'],
                  ['Итоги недели'],
                  ['Оценки за четверть/семестр'],
                  ['Аккаунт']]

reply_keyboard2 = [['Оценки за неделю'], ['Изучаемые на недели темы'], ['Главное меню']]

switch = 1


def start(update, context):
    markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True)
    update.message.reply_text(
        "Приветствую! Я бот, позволяющий смотреть информацию с Вашего дневника.ру. "
        "Выберите интересующую вас в данный момент информацию",
        reply_markup=markup
    )


def first_response(update, context):
    # Сохраняем ответ в словаре.
    context.user_data['login'] = update.message.text
    update.message.reply_text(
        f"Введите пароль")
    return 2


def second_response(update, context):
    global dn, switch
    context.user_data['password'] = update.message.text
    # Используем user_data в ответе.
    update.message.reply_text(
        f"Все данные введены")
    dn = Dnevnik(login=context.user_data['login'], password=context.user_data['password'])
    switch = 1
    return ConversationHandler.END


def stop(update, context):
    global switch
    update.message.reply_text("Ввод данных аккаунта прерван")
    switch = 1
    return ConversationHandler.END


def help(update, context):
    update.message.reply_text(
        "Я пока не умею помогать... Я только ваше эхо.")


def homework(update, context):
    if not context.args:
        day = str(int(datetime.today().strftime('%d')) + 1) + datetime.today().strftime('.%m.%Y')
        homework = dn.homework(datefrom=day, days=0)
    elif int(context.args[0]) > 0:
        home_work = dn.homework(days=int(context.args[0]))
    answer = 'Всего заданий: ' + str(homework['homeworkCount']) + '\n'
    for i in range(len(homework['homework'])):
        answer = answer + str(i + 1) + '.' + homework['homework'][i][0] + ' | ' + homework['homework'][i][1] + '\n'
    update.message.reply_text(
        answer

    )
    print(dn.homework(days=2))


def echo(update, context):
    markup1 = ReplyKeyboardMarkup(reply_keyboard2, resize_keyboard=True)
    if update.message.text == 'Итоги недели':
        update.message.reply_text('Я владею следующей информацией об этом.\n'
                                  'Выберите интересующию Вас.',
                                  reply_markup=markup1)
    if dn != 0:
        if update.message.text == 'Оценки за неделю':
            marks_week(update)
        if update.message.text == 'Изучаемые на недели темы':
            learn_week(update)
        if update.message.text == 'Расписание на неделю':
            timetable_week(update)
        if update.message.text == 'Главное меню':
            start(update, context)
        if update.message.text == 'Оценки за четверть/семестр':
            marks(update, context)
        if update.message.text == 'Домашние задания на завтра':
            homework(update, context)
    if update.message.text == 'Аккаунт':
        account(update, context)

    else:
        update.message.reply_text('Данные аккаунта не указаны')


def marks_week(update):
    answer = dn.week(info='marks', weeks=0)
    print(answer)
    ans = 'Успеваемость: \n'
    for i in answer['marks']:
        ans = ans + '\n' + str(i)
    update.message.reply_text(ans)


def learn_week(update):
    answer = dn.week(info='themes', weeks=0)
    print(answer)
    ans = 'Изучаемые темы: \n'
    for i in range(len(answer['themes'])):
        ans = ans + '\n' + str(i + 1) + '.' + str(answer['themes'][i]) + '\n'
    update.message.reply_text(ans)


def timetable_week(update):
    answer = dn.week(info='schedule', weeks=0)
    print(answer)
    ans = 'Расписание: \n'
    for i in answer['schedule']:
        ans = ans + '   ' + str(i) + ':\n'
        for j in range(len(answer['schedule'][i])):
            ans = ans + '\n       ' + str(j + 1) + '.' + str(answer['schedule'][i][j])
        ans = ans + '\n\n'
    update.message.reply_text(ans)


def marks(update, context):
    answer = dn.marks()
    print(answer)
    x = ''
    ans = 'Оценки за четверть/семестр: \n-----------------------'
    for i in answer:
        y = Counter(list(i[2]))
        for j in y:
            if j.isnumeric():
                if y[j] > 1:
                    x = x + str(y[j]) + '(' + str(j) + ')' + ' | '
                else:
                    x = x + str(j) + ' | '
        ans = ans + '\n' + str(i[0]) + '.' + str(i[1]) + ' | ' + x
        x = ''
        y.clear()
    update.message.reply_text(ans)


def account(update, context):
    update.message.reply_text(
        "Введите логин аккаунта\n"
        "Вы можете прервать опрос, послав команду /stop.\n")
    Updater(TOKEN).dispatcher.remove_handler(echo_handler, group=0)
    return 1


def main():
    updater = Updater(TOKEN)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("homework", homework,
                                  pass_args=True,
                                  pass_job_queue=True,
                                  pass_chat_data=True))
    echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)
    dp.add_handler(echo_handler)
    conv_handler = ConversationHandler(
        # Точка входа в диалог.
        # В данном случае — команда /start. Она задаёт первый вопрос.
        entry_points=[CommandHandler('account', account)],

        # Состояние внутри диалога.
        # Вариант с двумя обработчиками, фильтрующими текстовые сообщения.
        states={
            # Добавили user_data для сохранения ответа.
            1: [MessageHandler(Filters.text & ~Filters.command, first_response, pass_user_data=True)],
            # ...и для его использования.
            2: [MessageHandler(Filters.text & ~Filters.command, second_response, pass_user_data=True)]
        },
        fallbacks=[CommandHandler('stop', stop)]
    )
    dp.add_handler(conv_handler)
    dp.add_handler(CommandHandler("help", help))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
