from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

button_A1 = KeyboardButton("A1")
button_A2 = KeyboardButton("A2")
button_B1 = KeyboardButton("B1")
button_B2 = KeyboardButton("B2")

level_kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
level_kb.row(button_A1, button_A2).row(button_B1, button_B2)

button_text = KeyboardButton("/новый_текст📖")

text_kb = ReplyKeyboardMarkup()
text_kb.add(button_text)

button_yes = KeyboardButton("да")
button_no = KeyboardButton("нет")

yesno_kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
yesno_kb.add(button_yes).add(button_no)

button_1 = KeyboardButton("a")
button_2 = KeyboardButton("b")
button_3 = KeyboardButton("c")
button_4 = KeyboardButton("d")

kb_abcd = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
kb_abcd.row(button_1, button_2).row(button_3, button_4)

button_settings = KeyboardButton("/настройки⚙️")
button_acsess_to_admin_kb = KeyboardButton("/admin")

standart_kb = ReplyKeyboardMarkup(resize_keyboard=True)
standart_kb.add(button_text).row(button_settings, button_acsess_to_admin_kb)

button_see_stats = KeyboardButton("/моя_статистика")
button_help = KeyboardButton("/поддержка")
button_update_freq = KeyboardButton("/настроить_уведомления")

settings_kb = ReplyKeyboardMarkup(resize_keyboard=True)
settings_kb.row(button_see_stats, button_update_freq).add(button_help)

button_send_all = KeyboardButton("/send_all")
button_new_text = KeyboardButton("/new_text")
button_see_all_stats = KeyboardButton("/see_all_stats")
button_change_text = KeyboardButton("/change_text")


admin_kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
admin_kb.row(button_new_text, button_change_text).row(button_see_all_stats, button_send_all)
