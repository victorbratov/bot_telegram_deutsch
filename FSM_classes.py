from aiogram.dispatcher.filters.state import State, StatesGroup


class FSMtexts(StatesGroup):
    header = State()
    body = State()
    vocabulary = State()
    order = State()
    level = State()
    are_there_q = State()
    how_many_q = State()
    type_q = State()
    right_a = State()


class FSMuser_data(StatesGroup):
    level_user = State()
    how_often = State()
    upd_freq = State()


class FSMtake_test(StatesGroup):
    will_take = State()
    answer_question = State()
    redo = State()


class FSMsend_all(StatesGroup):
    send_all = State()


class FSMchange_text(StatesGroup):
    what_text = State()
    new_text = State()
