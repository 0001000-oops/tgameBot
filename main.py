import random
import logging
from telegram import Update, ForceReply, replykeyboardmarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler

# Включаем логирование
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Состояния для ConversationHandler
REGISTER, MAIN_MENU, QUIZ_MENU, QUIZ_TOPIC, QUIZ_LEVEL, ANSWER_QUESTION, PUZZLE, GUESS_NUMBER, DAILY_TIP, PROFILE = range(10)

# Хранение данных пользователей
users_data = {}

# Вопросы для викторины по темам и уровням
quiz_questions = {
    "history": {
        "easy": [
            {"question": "Кто был первым президентом США?", "options": ["Авраам Линкольн", "Джордж Вашингтон", "Томас Джефферсон"], "answer": "Джордж Вашингтон"},
            {"question": "Какой год считается началом Второй мировой войны?", "options": ["1939", "1941", "1938"], "answer": "1939"}
        ],
        "medium": [
            {"question": "Когда была подписана Декларация независимости США?", "options": ["1776", "1787", "1791"], "answer": "1776"},
            {"question": "Кто был королем Англии во время американской революции?", "options": ["Георг III", "Георг II", "Георг IV"], "answer": "Георг III"}
        ],
        "hard": [
            {"question": "Кто был последним императором России?", "options": ["Николай I", "Николай II", "Александр III"], "answer": "Николай II"},
            {"question": "Какой город был столицей СССР?", "options": ["Москва", "Санкт-Петербург", "Киев"], "answer": "Москва"}
        ]
    },
    # Добавьте аналогичные структуры для других тем...
}

# Советы на день
daily_tips = [
    "Пейте достаточно воды каждый день!",
    "Регулярно гуляйте на свежем воздухе.",
    "Не забывайте делать перерывы в работе.",
    "Чтение книг развивает мышление и воображение.",
    "Старайтесь улыбаться чаще — это улучшает настроение!"
]

def start(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("Добро пожаловать! Как вас зовут?")
    return REGISTER

def register_name(update: Update, context: CallbackContext) -> int:
    user_id = update.message.from_user.id
    users_data[user_id] = {'name': update.message.text, 'points': 0}
    update.message.reply_text(f"Приятно познакомиться, {users_data[user_id]['name']}! Выберите действие:", reply_markup=main_menu_keyboard())
    return MAIN_MENU

def main_menu(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("Выберите действие:", reply_markup=main_menu_keyboard())
    return MAIN_MENU

def main_menu_keyboard():
    keyboard = [
        ["Викторина", "Головоломка"],
        ["Угадай число", "Совет на день"],
        ["Профиль"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def quiz_menu(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("Выберите тему викторины:", reply_markup=quiz_menu_keyboard())
    return QUIZ_TOPIC

def quiz_menu_keyboard():
    keyboard = [
        ["Историческая", "Научная"],
        ["Киберспортивная", "Детская"],
        ["Назад в меню"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def select_quiz_topic(update: Update, context: CallbackContext) -> int:
    topic = update.message.text.lower()
    if topic in quiz_questions:
        context.user_data['quiz_topic'] = topic
        update.message.reply_text("Выберите уровень сложности:", reply_markup=quiz_level_keyboard())
        return QUIZ_LEVEL
    else:
        return main_menu(update, context)

def quiz_level_keyboard():
    keyboard = [
        ["Легкий", "Средний"],
        ["Сложный", "Назад в меню"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def select_quiz_level(update: Update, context: CallbackContext) -> int:
    level = update.message.text.lower()
    if level in ['легкий', 'средний', 'сложный']:
        context.user_data['quiz_level'] = level
        context.user_data['current_question'] = 0
        context.user_data['correct_answers'] = 0
        ask_question(update, context)
        return ANSWER_QUESTION
    else:
        return main_menu(update, context)

def ask_question(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    topic = context.user_data['quiz_topic']
    level = context.user_data['quiz_level']
    
    questions = quiz_questions[topic][level]
    
    if context.user_data['current_question'] < len(questions):
        question_data = questions[context.user_data['current_question']]
        options = "\n".join([f"{i + 1}. {opt}" for i, opt in enumerate(question_data["options"])])
        
        update.message.reply_text(f"Вопрос {context.user_data['current_question'] + 1}: {question_data['question']}\n{options}")
    else:
        show_results(update, context)

def handle_answer(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    answer_index = int(update.message.text) - 1
    
    topic = context.user_data['quiz_topic']
    level = context.user_data['quiz_level']
    
    question_data = quiz_questions[topic][level][context.user_data['current_question']]
    
    if question_data["options"][answer_index] == question_data["answer"]:
        users_data[user_id]['points'] += 10  # Заработать 10 очков за правильный ответ
        context.user_data['correct_answers'] += 1
        update.message.reply_text(f"Правильно! Верный ответ: {question_data['answer']}")
    else:
        update.message.reply_text(f"Неправильно. Верный ответ: {question_data['answer']}")

    context.user_data['current_question'] += 1
    ask_question(update, context)

def show_results(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    correct_answers = context.user_data['correct_answers']
    
    update.message.reply_text(f"Вы ответили правильно на {correct_answers} вопросов!")
    
def puzzle(update: Update, context: CallbackContext) -> None:
    # Логика головоломки может быть добавлена здесь
    update.message.reply_text("Это головоломка! Какую загадку вы хотите решить?")

def guess_number(update: Update, context: CallbackContext) -> None:
    number_to_guess = random.randint(1, 100)
    
    users_data[update.message.from_user.id]['number_to_guess'] = number_to_guess
    
    update.message.reply_text("Я загадал число от 1 до 100. Попробуйте угадать!")
    
def handle_guess(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    guess = int(update.message.text)
    
    number_to_guess = users_data[user_id].get('number_to_guess')
    
    if guess < number_to_guess:
        update.message.reply_text("Слишком мало! Попробуйте снова.")
        
    elif guess > number_to_guess:
        update.message.reply_text("Слишком много! Попробуйте снова.")
        
    else:
        users_data[user_id]['points'] += 20  # Заработать 20 очков за правильный ответ
        update.message.reply_text(f"Поздравляю! Вы угадали число {guess}.")
    
def daily_tip(update: Update, context: CallbackContext) -> None:
    tip = random.choice(daily_tips)
    update.message.reply_text(f"Совет на день: {tip}")

def profile(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    user_info = users_data.get(user_id)
    
    if user_info:
        profile_info = f"Имя: {user_info['name']}\nОчки: {user_info['points']}"
        update.message.reply_text(profile_info)
    else:
        update.message.reply_text("Вы не зарегистрированы. Пожалуйста, начните с /start.")

def main() -> None:
    """Запуск бота."""
    updater = Updater("YO7183657865:AAFhE7dmL_p0xoQ7snJ_-0I7PyWNFmMKBhI")
    
    dispatcher = updater.dispatcher

    # Определяем обработчики команд и сообщений
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        
        states={
            REGISTER: [MessageHandler(Filters.text & ~Filters.command, register_name)],
            MAIN_MENU: [MessageHandler(Filters.regex('^(Викторина|Головоломка|Угадай число|Совет на день|Профиль)$'), main_menu)],
            QUIZ_MENU: [MessageHandler(Filters.regex('^(Историческая|Научная|Киберспортивная|Детская)$'), select_quiz_topic)],
            QUIZ_LEVEL: [MessageHandler(Filters.regex('^(Легкий|Средний|Сложный)$'), select_quiz_level)],
            ANSWER_QUESTION: [MessageHandler(Filters.text & ~Filters.command, handle_answer)],
            PUZZLE: [MessageHandler(Filters.text & ~Filters.command, puzzle)],
            GUESS_NUMBER: [MessageHandler(Filters.text & ~Filters.command, handle_guess)],
            DAILY_TIP: [MessageHandler(Filters.text & ~Filters.command, daily_tip)],
            PROFILE: [MessageHandler(Filters.text & ~Filters.command, profile)],
        },
        
        fallbacks=[CommandHandler('start', start)]
    )

    dispatcher.add_handler(conv_handler)

    # Запускаем бота
    updater.start_polling()
    
    updater.idle()

if __name__ == '__main__':
    main()