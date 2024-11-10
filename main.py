from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext

TOKEN = '7710943986:AAEUcvPsKfxzwuziTHQMfbg-D8SjZBhJcvw'


def start(update: Update, context: CallbackContext):
    update.message.reply_text('Добро пожаловать в игру Крестики-нолики! Нажмите /play для начала игры.')


def play(update: Update, context: CallbackContext):
    board = [[' ' for _ in range(3)] for _ in range(3)]
    markup = create_board_markup(board)
    context.user_data['board'] = board
    context.user_data['turn'] = 'X'
    update.message.reply_text('Ваш ход:', reply_markup=markup)


def button(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    row, col = map(int, query.data.split(','))  # get row and column from callback data
    board = context.user_data['board']

    if board[row][col] == ' ':  # check if the cell is empty
        board[row][col] = 'X'  # player's move
        if has_won(board, 'X'):
            query.edit_message_text('Вы выиграли!')
            return
        elif is_full(board):
            query.edit_message_text('Ничья!')
            return

        if not is_full(board):
            bot_play(board, context)  # bot makes a move
            if has_won(board, 'O'):
                markup = create_board_markup(board)
                query.edit_message_text('Бот выиграл!', reply_markup=markup)
                return

        markup = create_board_markup(board)
        query.edit_message_text('Ваш ход:', reply_markup=markup)
    else:
        query.edit_message_text('Эта клетка уже занята, выберите другую.')


def has_won(board, player):
    # Проверка строк
    for row in board:
        if all(cell == player for cell in row):
            return True
    # Проверка столбцов
    for col in range(3):
        if all(board[row][col] == player for row in range(3)):
            return True
    # Проверка диагоналей
    if all(board[i][i] == player for i in range(3)):
        return True
    if all(board[i][2 - i] == player for i in range(3)):
        return True

    return False


def bot_play(board, context):
    # Пытаемся найти выигрышный ход
    for i in range(3):
        for j in range(3):
            if board[i][j] == ' ':
                board[i][j] = 'O'
                if has_won(board, 'O'):
                    return
                board[i][j] = ' '

    # Блокировка хода игрока
    for i in range(3):
        for j in range(3):
            if board[i][j] == ' ':
                board[i][j] = 'X'
                if has_won(board, 'X'):
                    board[i][j] = 'O'
                    return
                board[i][j] = ' '

    # Остальные случаи - выбор первого свободного места
    for i in range(3):
        for j in range(3):
            if board[i][j] == ' ':
                board[i][j] = 'O'
                return



def is_full(board):
    return all(board[row][col] != ' ' for row in range(3) for col in range(3))


def create_board_markup(board):
    keyboard = [
        [InlineKeyboardButton(board[row][col] or ' ', callback_data=f'{row},{col}') for col in range(3)]
        for row in range(3)
    ]
    return InlineKeyboardMarkup(keyboard)


def main():
    updater = Updater(TOKEN)

    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CommandHandler('play', play))
    updater.dispatcher.add_handler(CallbackQueryHandler(button))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
