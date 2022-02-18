from aiogram import executor
from dispatcher import dp, scheduler, bot
from notification import notification
import handlers

if __name__ == "__main__":
    scheduler.add_job(notification, "cron", hour='19', minute='00', timezone='Europe/Moscow', args=(bot,))
    scheduler.start()
    executor.start_polling(dp, skip_updates=True)
