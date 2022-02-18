from aiogram import Bot
from config import cur, conn
from keyboards import text_kb


async def notification(bot: Bot):
    cur.execute("SELECT user_id, next_notif FROM users")
    users_list = cur.fetchall()
    print(users_list)
    print('list made')
    for i in range(len(users_list)):
        print('next user')
        print(i)
        if users_list[i][1] == 1:
            await bot.send_message(users_list[i][0], "давайте позанимаемся", reply_markup=text_kb)
            cur.execute("SELECT how_often FROM users WHERE user_id = '%s'" % users_list[i][0])
            ho = int(''.join(map(str, cur.fetchone())))
            cur.execute("UPDATE users SET next_notif = ? WHERE user_id = ?", (ho, users_list[i][0]))
            conn.commit()
            print('msg sent')
        else:
            cur.execute("SELECT next_notif FROM users WHERE user_id = '%s'" % users_list[i][0])
            nf = int(''.join(map(str, cur.fetchone())))
            cur.execute("UPDATE users SET next_notif = ? WHERE user_id = ?", (nf - 1, users_list[i][0]))
            conn.commit()
            print('next_notif updated')
