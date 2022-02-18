from aiogram import types
from keyboards import kb_abcd
from config import cur, conn


async def compile_text_message(tn, message: types.Message):
    cur.execute("SELECT header FROM texts WHERE order_text = '%s'" % tn)
    header = cur.fetchone()
    cur.execute("SELECT text_body FROM texts WHERE order_text = '%s'" % tn)
    text = cur.fetchone()
    # cur.execute("SELECT vocabulary FROM texts WHERE order_text = '%s'" % tn)
    # vocabulary = cur.fetchone()
    mess = ''.join(header) + "\n\n" + ''.join(text)
    await message.answer(mess, reply_markup=types.ReplyKeyboardRemove())
    # await message.answer(''.join(vocabulary))


async def compile_question_message(message: types.Message, tn, qo):
    cur.execute("SELECT question_text FROM questions WHERE (test_number, q_order) = (?,?)",
                (tn, qo))
    mmsg = cur.fetchone()
    msg = ''.join(mmsg)
    await message.answer(msg, reply_markup=kb_abcd)
    await message.answer("выберите ответ")


async def sending_question(message: types.Message):
    cur.execute("SELECT text_num FROM users WHERE user_id = '%s'" % message.from_user.id)
    tn = int(''.join(map(str, cur.fetchone())))
    cur.execute("SELECT question_number FROM texts WHERE order_text = '%s'" % tn)
    qo = int(''.join(map(str, cur.fetchone()))) - 1
    await compile_question_message(message, tn, qo + 1)
    return tn, qo


def commit_new_text_to_bd(th, tb, vb, tn, tl):
    cur.execute(
        'INSERT INTO texts (header, text_body, vocabulary, order_text, level, question_number) VALUES (?, ?, ?, '
        '?, ?, NULL)',
        (th, tb, vb, tn, tl))
    conn.commit()


def commit_new_question_to_db(qt, tn, qn, ra):
    cur.execute("INSERT INTO questions (question_text, test_number, q_order, right_a) VALUES (?,?,?,?)",
                (qt, tn, qn, ra))
    conn.commit()


def update_average_score(tt, asc, score, message):
    cur.execute("UPDATE users SET tests_taken = ? WHERE user_id = ?", (tt + 1, message.from_user.id))
    cur.execute("UPDATE users SET average_score = ? WHERE user_id = ?",
                ((((asc * tt) + int(score)) / (tt + 1)), message.from_user.id))
    conn.commit()


def put_val_users(user_id: int, user_name: str, user_activity: int):
    cur.execute(
        'INSERT INTO users (user_id, user_name, user_activity, how_often, user_level) VALUES (?, ?, ?, NULL, NULL)',
        (user_id, user_name, user_activity))
    conn.commit()


def check_if_convertable_to_int(message: types.Message):
    try:
        int(message.text)
        return True
    except ValueError:
        return False
