from aiogram import types
from dispatcher import dp, bot
from config import cur, conn
from FSM_classes import FSMuser_data, FSMtake_test
from keyboards import *
from aiogram.dispatcher import FSMContext
from handlers.methods import compile_text_message, sending_question, update_average_score, put_val_users, \
    check_if_convertable_to_int


@dp.message_handler(commands=['start'])
async def command_start(message: types.Message):
    us_id = message.from_user.id
    us_name = message.from_user.username
    us_activity = 0
    put_val_users(user_id=us_id, user_name=us_name, user_activity=us_activity)
    u_id = message.from_user.id
    cur.execute("SELECT user_name FROM users WHERE user_id = '%s' " % u_id)
    u_name = cur.fetchone()
    mess = "Привет, " + ''.join(u_name)
    await bot.send_message(message.from_user.id, mess)
    await bot.send_message(message.from_user.id, "deutsch_bot - это telegram bot созданный для того, чтобы помочь его "
                                                 "пользователям заниматься немецким языком регулярно и "
                                                 "прогрессировать в его изучении. не могли бы вы ответить на несколько вопросов?")
    await FSMuser_data.level_user.set()
    await message.answer("как вы оцените свой уровень немецкого?", reply_markup=level_kb)


@dp.message_handler(state=FSMuser_data.level_user)
async def put_user_level(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['user_level'] = message.text
    await FSMuser_data.next()
    await message.answer("раз в сколько дней вы хотите получать напоминание о занятии (введите чило от 1 до 7)?",
                         reply_markup=types.ReplyKeyboardRemove())


@dp.message_handler(state=FSMuser_data.how_often)
async def put_how_often(message: types.Message, state: FSMContext):
    if not check_if_convertable_to_int(message):
        await message.answer("это должно быть число, попробуйте ещё раз")
        return
    if int(message.text) <= 0:
        await message.answer("число должно быть больше 0, попробуйте ещё раз")
        return
    async with state.proxy() as data:
        data['how_often'] = int(message.text)
        data["text_num"] = 1
        cur.execute('UPDATE users SET (user_level, how_often) = (?, ?) WHERE user_id = ?',
                    (data['user_level'], data['how_often'], message.from_user.id))
        conn.commit()
        cur.execute("UPDATE users SET text_num = ? WHERE (user_id, text_num) = (?,?)",
                    (data["text_num"], message.from_user.id, None))
        conn.commit()
        cur.execute("SELECT text_num FROM users WHERE user_id = '%s'" % message.from_user.id)
        print(cur.fetchone())
    await state.finish()
    await message.answer("ваши данные сохранены", reply_markup=standart_kb)


@dp.message_handler(commands=["настройки⚙️"])
async def settings(message: types.Message):
    await message.answer("settings", reply_markup=settings_kb)


@dp.message_handler(commands=['настроить_уведомления'])
async def upd_freq(message: types.Message):
    await message.answer("раз в сколько дней вы хотите получать напоминание о занятии (введите чило от 1 до 7)")
    await FSMuser_data.upd_freq.set()


@dp.message_handler(state=FSMuser_data.upd_freq)
async def update_frequency(message: types.Message, state: FSMContext):
    if not check_if_convertable_to_int(message):
        await message.answer("это должно быть число, попробуйте ещё раз")
        return
    if int(message.text) <= 0:
        await message.answer("число должно быть больше 0, попробуйте ещё раз")
        return
    async with state.proxy() as data:
        data['how_often'] = message.text
        cur.execute('UPDATE users SET how_often = ? WHERE user_id = ?',
                    (data['how_often'], message.from_user.id))
        conn.commit()
    await state.finish()
    await message.answer("ваши данные сохранены", reply_markup=standart_kb)


@dp.message_handler(commands=['поддержка'])
async def command_help(message: types.Message):
    await message.answer(
        "список всех команд:\n\n/start - начальная команда, позволит заново ввести данные пользователя(уровень "
        "немецкого, частоту уведомлений)\n\n/настроить_уведомления - обновить данные о частоте "
        "уведомлений\n\n/нoвый_текст - "
        "пришлет новый текст\n\nотмена - если написать слово отмена, пока вы проходите тест или настраиваете профиль, "
        "изменения не будут сохранены\n\nпо вопросам писать @victorbratov", reply_markup=standart_kb)


@dp.message_handler(commands=['моя_статистика'])
async def see_stats(message: types.Message):
    cur.execute('SELECT text_num FROM users WHERE user_id = "%s"' % message.from_user.id)
    tr = int(''.join(map(str, cur.fetchone()))) - 1
    cur.execute("SELECT average_score FROM users WHERE user_id = '%s'" % message.from_user.id)
    asc = float(''.join(map(str, cur.fetchone())))
    msg = "прочитано текстов: " + str(tr) + "\n" + "ваш средний балл за тест: " + str(round(asc)) + "%"
    await message.answer(msg, reply_markup=standart_kb)


@dp.message_handler(commands=['новый_текст📖'])
async def send_text(message: types.Message):
    cur.execute("SELECT text_num FROM users WHERE user_id = '%s'" % message.from_user.id)
    tn = int(''.join(map(str, cur.fetchone())))
    await compile_text_message(tn, message)
    cur.execute("SELECT question_number FROM texts WHERE order_text = '%s'" % tn)
    qn = int(''.join(map(str, cur.fetchone())))
    if qn > 0:
        await message.answer("давайте пройдем тест на понимание текста?", reply_markup=yesno_kb)
        await FSMtake_test.will_take.set()
    else:
        cur.execute("UPDATE users SET text_num = ? WHERE user_id = ?", (tn + 1, message.from_user.id))
        conn.commit()
        await message.answer("досвидания, увидимся в следующий раз", reply_markup=standart_kb)


@dp.message_handler(state=FSMtake_test.will_take)
async def will_take(message: types.Message, state: FSMContext):
    if message.text == "да":
        await message.answer("удачи", reply_markup=types.ReplyKeyboardRemove())
        async with state.proxy() as data:
            (data['test_num'], data['q_order']) = await sending_question(message)
            data["rn_count"] = 0
            await FSMtake_test.next()
    else:
        cur.execute("SELECT text_num FROM users WHERE user_id = '%s'" % message.from_user.id)
        tn = int(''.join(map(str, cur.fetchone())))
        cur.execute("UPDATE users SET text_num = ? WHERE user_id = ?", (tn + 1, message.from_user.id))
        conn.commit()
        await state.finish()
        await message.answer("досвидания, увидимся в следующий раз", reply_markup=standart_kb)


@dp.message_handler(state=FSMtake_test.answer_question)
async def answer_q(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        user_a = message.text
        data["q_order"] = int(data["q_order"]) + 1
        cur.execute("SELECT right_a FROM questions WHERE (test_number, q_order) = (?,?)",
                    (data["test_num"], data["q_order"]))
        rn = ''.join(cur.fetchone())
        data["q_order"] = int(data["q_order"]) - 1
        if user_a == rn:
            data["rn_count"] = int(data["rn_count"]) + 1
            await message.answer("✅")
        else:
            await message.answer("❌")
        if int(data["q_order"]) > 0:
            cur.execute("SELECT question_text FROM questions WHERE (test_number, q_order) = (?,?)",
                        (data["test_num"], data["q_order"]))
            msg = ''.join(cur.fetchone())
            await message.answer(msg, reply_markup=kb_abcd)
            await message.answer("выберите ответ")
            data["q_order"] = int(data["q_order"]) - 1
        else:
            await FSMtake_test.next()
            await message.answer("хотите пройти тест ещё раз?", reply_markup=yesno_kb)


@dp.message_handler(state=FSMtake_test.redo)
async def redo(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if message.text == "да":
            cur.execute("SELECT question_number FROM texts WHERE order_text = '%s'" % data["test_num"])
            data["q_q"] = int(''.join(map(str, cur.fetchone())))
            (data['test_num'], data['q_order']) = await sending_question(message)
            score = data["rn_count"] / data["q_q"] * 100
            cur.execute(
                "SELECT tests_taken, average_score FROM users WHERE user_id = '%s'" % message.from_user.id)
            data_obj = cur.fetchall()[0]
            (tt, asc) = (int(data_obj[0]), int(data_obj[1]))
            update_average_score(tt, asc, score, message)
            data['rn_count'] = 0
            await FSMtake_test.answer_question.set()
        else:
            cur.execute("SELECT question_number FROM texts WHERE order_text = '%s'" % data["test_num"])
            data["q_q"] = int(''.join(map(str, cur.fetchone())))
            score = data["rn_count"] / data["q_q"] * 100
            msg = "ваш результат " + str(int(score)) + "%"
            await message.answer(msg)
            cur.execute(
                "SELECT text_num, tests_taken, average_score FROM users WHERE user_id = '%s'" % message.from_user.id)
            data_obj = cur.fetchall()[0]
            (tn, tt, asc) = (int(data_obj[0]), int(data_obj[1]), float(data_obj[2]))
            cur.execute("UPDATE users SET text_num = ? WHERE user_id = ?", (tn + 1, message.from_user.id))
            update_average_score(tt, asc, score, message)
            await state.finish()
            await message.answer("досвидания, увидимся в следующий раз", reply_markup=standart_kb)


@dp.message_handler()
async def no_fn(message: types.Message):
    await message.reply("такой команды нет", reply_markup=standart_kb)
