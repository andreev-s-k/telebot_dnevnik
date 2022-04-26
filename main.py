import logging
from datetime import datetime
from telegram.ext import *
from telegram import *
from dnevnikru import Dnevnik
from collections import Counter
from pprint import pprint

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

logger = logging.getLogger(__name__)

TOKEN = '5225353944:AAGfXO0TWaKkrBJFakBbJ6LyHwFFOGyQeiY'

dn = 0  # Dnevnik(login=login, password=password)

reply_keyboard = [['Домашние задания на завтра'],
                  ['Расписание на неделю'],
                  ['Итоги недели'],
                  ['Оценки за четверть/семестр'],
                  ['Аккаунт']]

reply_keyboard2 = [['Оценки за неделю'], ['Изучаемые на недели темы'], ['Главное меню']]

def start(update, context):
    markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True)
    update.message.reply_text(
        "Приветствую! Я бот, позволяющий смотреть информацию с Вашего дневника.ру. "
        "Выберите интересующую вас в данный момент информацию",
        reply_markup=markup
    )

def homework(update, context):
    if not context.args:
        day = str(int(datetime.today().strftime('%d')) + 1) + datetime.today().strftime('.%m.%Y')
        homeworks = dn.homework(datefrom=day, days=0)
    elif int(context.args[0]) > 0:
        homeworks = dn.homework(days=int(context.args[0]))
    answer = 'Всего заданий: ' + str(homeworks['homeworkCount']) + '\n'
    for i in range(len(homeworks['homework'])):
        answer = answer + str(i + 1) + '.' + homeworks['homework'][i][0] + ' | ' + homeworks['homework'][i][1] + '\n'
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
    if dn != 0 or update.message.text == 'Аккаунт' or update.message.text == 'Главное меню' or update.message.text == 'Итоги недели':
        if update.message.text == 'Оценки за неделю':
            marks_week(update)
        if update.message.text == 'Изучаемые на недели темы':
            learn_week(update)
        if update.message.text == 'Расписание на неделю':
            timetable_week(update)
        if update.message.text == 'Оценки за четверть/семестр':
            marks(update, context)
        if update.message.text == 'Домашние задания на завтра':
            homework(update, context)
    else:
        update.message.reply_text('Данные аккаунта не указаны\n'
                                  'Указать их можно в пункте "Аккаунт" главного меню.')
    if 'Аккаунт' in update.message.text:
        account(update, context)
    if update.message.text == 'Главное меню':
        start(update, context)


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
    pprint(answer)
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
    ans = 'Средний балл: \n-----------------------'
    for i in answer:
        ans = ans + '\n' + i[1] + ' | ' + i[6]
    update.message.reply_text(ans)


def account(update, context):
    global dn
    print(context, context.args)
    if context.args == None:
        update.message.reply_text(
            "Введите данные аккаунта\n"
            "для этого введите команду:\n /account [логин] [пароль].\n")
    else:
        dn = Dnevnik(login=context.args[0], password=context.args[1])
        update.message.reply_text(
            "Данные аккаунта получены")


def main():
    updater = Updater(TOKEN)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("homework", homework,
                                  pass_args=True))
    dp.add_handler(CommandHandler("account", account,
                                  pass_args=True))
    echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)
    dp.add_handler(echo_handler)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
