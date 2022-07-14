from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from secret_token import TOKEN_ST
from pars_file import parser_main, create_connection, DATABASE_PATH


def start(update, context):
    update.message.reply_text('')


def help(update, context):
    update.message.reply_text('Для старта введите /start\n'
                              'Для обновления информации /parse\n'
                              'Для получения информации о городе введите его название')


def error(update, context):
    print(context.error)
    update.message.reply_text('Ошибка, повторите ввод')


def text(update, context):
    text_received = update.message.text
    connection = create_connection(DATABASE_PATH)
    cursor = connection.cursor()
    res = cursor.execute("SELECT * FROM City WHERE name=?", (text_received,)).fetchone()
    if res:
        update.message.reply_text(f"Город: {res[1]}\n"
                                  f"Население: {res[2]}\n"
                                  f"{res[3]}"
                                  )
    else:
        res1 = cursor.execute("SELECT * FROM City WHERE name LIKE ?", ('%' + text_received + '%',)).fetchall()
        res2 = cursor.execute("SELECT * FROM City WHERE name LIKE ?", ('%' + text_received.capitalize() + '%',)).fetchall()
        is_printed = []
        answer = 'Возможно Вы имели ввиду один из этих городов:\n'
        for el in res1 + res2:
            if el[1] not in is_printed:
                is_printed.append(el[1])
        answer += '\n'.join(is_printed)
        update.message.reply_text(answer)


def parsing(update, context):
    parser_main()
    update.message.reply_text("Информация успешно загружена в базу данных")


def main():
    TOKEN = TOKEN_ST
    updater = Updater(TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help))
    dispatcher.add_handler(CommandHandler("parse", parsing))
    dispatcher.add_handler(MessageHandler(Filters.text, text))
    dispatcher.add_error_handler(error)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
