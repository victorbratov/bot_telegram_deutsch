from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from dispatcher import dp
from config import cur, conn
from FSM_classes import FSMtexts, FSMchange_text, FSMsend_all
import logging
from keyboards import *
from dispatcher import bot
from handlers.methods import compile_text_message, commit_new_text_to_bd, commit_new_question_to_db, \
    check_if_convertable_to_int


@dp.message_handler(is_owner=True, commands='new_text', state=None)
async def new_text(message: types.Message):
    await FSMtexts.header.set()
    await message.reply("type header")


@dp.message_handler(commands=['отмена'], state='*')
@dp.message_handler(Text(equals='отмена', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    logging.info('Cancelling state %r', current_state)
    await state.finish()
    await message.reply('действие отменено', reply_markup=standart_kb)


@dp.message_handler(state=FSMtexts.header)
async def put_in_header(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['header'] = message.text
    await FSMtexts.next()
    await message.reply("type text")


@dp.message_handler(state=FSMtexts.body)
async def put_in_body(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['text'] = message.text
    await FSMtexts.next()
    await message.reply("type vocabulary")


@dp.message_handler(state=FSMtexts.vocabulary)
async def put_in_vocabulary(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['vocab'] = message.text
    await FSMtexts.next()
    await message.reply("what's the order number?")


@dp.message_handler(state=FSMtexts.order)
async def put_in_order(message: types.Message, state: FSMContext):
    if not check_if_convertable_to_int(message):
        await message.answer("это должно быть число, попробуйте ещё раз")
        return
    if int(message.text) <= 0:
        await message.answer("число должно быть больше 0, попробуйте ещё раз")
        return
    async with state.proxy() as data:
        data['order_text'] = int(message.text)
    await FSMtexts.next()
    await message.reply("what's the level?", reply_markup=level_kb)


@dp.message_handler(state=FSMtexts.level)
async def put_in_level(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['level'] = message.text
    async with state.proxy() as data:
        commit_new_text_to_bd(data['header'], data['text'], data['vocab'], data['order_text'], data['level'])
    await message.reply("are there any questions for this text?", reply_markup=yesno_kb)
    await FSMtexts.next()


@dp.message_handler(state=FSMtexts.are_there_q)
async def are_there_q(message: types.Message, state: FSMContext):
    if message.text == "да":
        await message.answer("how many?", reply_markup=types.ReplyKeyboardRemove())
        await FSMtexts.next()
    else:
        await message.answer("data is stored", reply_markup=standart_kb)
        await state.finish()


@dp.message_handler(state=FSMtexts.how_many_q)
async def how_many_q(message: types.Message, state: FSMContext):
    if not check_if_convertable_to_int(message):
        await message.answer("это должно быть число, попробуйте ещё раз")
        return
    if int(message.text) <= 0:
        await message.answer("число должно быть больше 0, попробуйте ещё раз")
        return
    async with state.proxy() as data:
        data["question_number"] = message.text
        cur.execute("UPDATE texts SET question_number = ? WHERE order_text = ?",
                    (data["question_number"], data["order_text"]))
        conn.commit()
    await message.answer("type the question")
    await FSMtexts.next()


@dp.message_handler(state=FSMtexts.type_q)
async def type_q(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["q_text"] = message.text
    await message.answer("type the right answer", reply_markup=kb_abcd)
    await FSMtexts.next()


@dp.message_handler(state=FSMtexts.right_a)
async def right_a(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["right_a"] = message.text
        question_number = data["question_number"]
        commit_new_question_to_db(data['q_text'], data['order_text'], data['question_number'], data['right_a'])
        if int(question_number) > 1:
            data["question_number"] = int(question_number) - 1
            await message.answer("type the next question")
            await FSMtexts.type_q.set()
        else:
            await message.answer("data is stored", reply_markup=standart_kb)
            await state.finish()


@dp.message_handler(commands=["change_text"], is_owner=True)
async def change_text(message: types.Message):
    await message.answer("what text you want to change?")
    await FSMchange_text.what_text.set()


@dp.message_handler(state=FSMchange_text.what_text)
async def which_text(message: types.Message, state: FSMContext):
    if not check_if_convertable_to_int(message):
        await message.answer("это должно быть число, попробуйте ещё раз")
        return
    if int(message.text) <= 0:
        await message.answer("число должно быть больше 0, попробуйте ещё раз")
        return
    async with state.proxy() as data:
        data["tn"] = int(message.text)
        await compile_text_message(data['tn'], message)
    await FSMchange_text.next()


@dp.message_handler(state=FSMchange_text.new_text)
async def new_change_text(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        cur.execute("UPDATE texts SET text_body = ? WHERE order_text = ?", (message.text, data["tn"]))
        conn.commit()
    await message.answer("changes made", reply_markup=standart_kb)
    await state.finish()


@dp.message_handler(commands=["send_all"], is_owner=True)
async def send_all(message: types.Message):
    await message.reply("type the message")
    await FSMsend_all.send_all.set()


@dp.message_handler(state=FSMsend_all.send_all)
async def send_mess(message: types.Message, state: FSMContext):
    cur.execute("SELECT user_id FROM users")
    users = cur.fetchall()
    for i in range(len(users)):
        users[i] = int(''.join(map(str, users[i])))
    print(users)
    for user in users:
        await bot.send_message(user, message.text)
    await message.answer("сообщение послано всем пользователям бота", reply_markup=standart_kb)
    await state.finish()


@dp.message_handler(commands=["see_all_stats"], is_owner=True)
async def send_all_stats(message: types.Message):
    cur.execute("SELECT user_name FROM users")
    users = cur.fetchall()
    cur.execute("SELECT text_num FROM users")
    user_tn = cur.fetchall()
    cur.execute("SELECT average_score FROM users")
    user_as = cur.fetchall()
    msg = ''
    for i in range(len(users)):
        msg += str(''.join(users[i])) + " texts read 📖: " + str(
            round(float(''.join(map(str, user_tn[i])))) - 1) + " average score: " + str(
            round(float(''.join(map(str, user_as[i]))))) + '%\n'
    await message.answer(msg, reply_markup=standart_kb)


@dp.message_handler(commands=['admin'], is_owner=True)
async def acsess_to_admin_kb(message: types.Message):
    await message.answer("доступ к командам админа открыт", reply_markup=admin_kb)
