import asyncio
import sys
import os
import logging
import httpx

BOT_TOKEN = os.getenv("BOT_TOKEN",
                      "f9LHodD0c0IXvDof1IyrdJf509Zprvj65zpHZTTAKX28MZg7Syt46umwV3dQx80cePj645cceq0klaAjfDm7")

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

BASE_URL = f"https://api.maxim.ru/bot{BOT_TOKEN}"

user_states = {}
user_data = {}

logging.basicConfig(level=logging.INFO)

def get_role_keyboard():
    return {
        "keyboard": [
            [{"text": "Я студент-исследователь"}],
            [{"text": "Я научный руководитель/преподаватель"}],
            [{"text": "Я представитель руководства/организации"}]
        ],
        "resize_keyboard": True,
        "one_time_keyboard": True
    }


def get_experience_inline_keyboard():
    return {
        "inline_keyboard": [
            [{"text": "❌ Не было опыта", "callback_data": "exp_0"}],
            [{"text": "1–2 года", "callback_data": "exp_1"}],
            [{"text": "3–5 лет", "callback_data": "exp_3"}],
            [{"text": "Более 5 лет", "callback_data": "exp_5"}]
        ]
    }


def get_direction_inline_keyboard():
    return {
        "inline_keyboard": [
            [{"text": "1. Технические", "callback_data": "dir_1"}, {"text": "2. IT", "callback_data": "dir_2"}],
            [{"text": "3. Экономика", "callback_data": "dir_3"}, {"text": "4. Гуманитарные", "callback_data": "dir_4"}],
            [{"text": "5. Медицина", "callback_data": "dir_5"}, {"text": "6. Право", "callback_data": "dir_6"}],
            [{"text": "7. Педагогика", "callback_data": "dir_7"}]
        ]
    }


def get_notifications_keyboard():
    return {
        "inline_keyboard": [
            [{"text": "✅ Да", "callback_data": "notify_yes"}, {"text": "❌ Нет", "callback_data": "notify_no"}]
        ]
    }


def get_main_menu_student():
    return {
        "inline_keyboard": [
            [{"text": "📚 Полезные курсы", "callback_data": "func_courses"}],
            [{"text": "📑 Структура работы", "callback_data": "func_structure"}],
            [{"text": "📖 Литература", "callback_data": "func_literature"}],
            [{"text": "🔔 Уведомления", "callback_data": "func_toggle_notify"}],
            [{"text": "💡 Идеи для НИР", "callback_data": "func_ideas"}],
            [{"text": "✏️ Оформление", "callback_data": "func_format"}],
            [{"text": "🎤 Конференции", "callback_data": "func_events"}],
            [{"text": "👥 Поиск команды", "callback_data": "func_team"}]
        ]
    }


def get_main_menu_teacher():
    return {
        "inline_keyboard": [
            [{"text": "🧑‍🏫 Автоматизированное сопровождение", "callback_data": "t_func_mentor"}],
            [{"text": "🎓 Организация мастерклассов", "callback_data": "t_func_master"}],
            [{"text": "📚 Методические рекомендации", "callback_data": "t_func_guidelines"}],
            [{"text": "📝 Тесты и оценивание", "callback_data": "t_func_tests"}],
            [{"text": "🔬 База исследований", "callback_data": "t_func_research_db"}]
        ]
    }


def get_main_menu_admin():
    return {
        "inline_keyboard": [
            [{"text": "🧩 Планирование НИР", "callback_data": "a_func_planning"}],
            [{"text": "🔍 Экспертиза и консалтинг", "callback_data": "a_func_expertise"}],
            [{"text": "📣 Научная коммуникация", "callback_data": "a_func_communication"}],
            [{"text": "🤝 Развитие партнерства", "callback_data": "a_func_partnership"}]
        ]
    }


def get_back_button():
    return {
        "inline_keyboard": [
            [{"text": "↩️ В меню", "callback_data": "back_to_menu"}]
        ]
    }

def _sync_get(url, params=None):
    try:
        with httpx.Client(timeout=35.0) as client:
            return client.get(url, params=params).json()
    except Exception as e:
        print(f"❌ GET error: {e}")
        return {"ok": False}


def _sync_post(url, json_data):
    try:
        with httpx.Client(timeout=30.0) as client:
            return client.post(url, json=json_data).json()
    except Exception as e:
        print(f"❌ POST error: {e}")
        return {"ok": False}


async def send_message(chat_id, text, reply_markup=None):
    url = f"{BASE_URL}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    if reply_markup:
        payload["reply_markup"] = reply_markup
    await asyncio.to_thread(_sync_post, url, payload)


async def edit_message(chat_id, message_id, text, reply_markup=None):
    url = f"{BASE_URL}/editMessageText"
    payload = {
        "chat_id": chat_id,
        "message_id": message_id,
        "text": text,
        "parse_mode": "HTML"
    }
    if reply_markup:
        payload["reply_markup"] = reply_markup
    await asyncio.to_thread(_sync_post, url, payload)


async def get_updates(offset=None):
    url = f"{BASE_URL}/getUpdates"
    params = {"timeout": 20}
    if offset is not None:
        params["offset"] = offset
    return await asyncio.to_thread(_sync_get, url, params)

async def handle_message(message):
    user_id = message["from"]["id"]
    chat_id = message["chat"]["id"]
    text = message.get("text", "")

    if text == "/start":
        user_states[user_id] = "waiting_for_role"
        user_data[user_id] = {}
        await send_message(
            chat_id,
            f"Привет, {message['from'].get('first_name', 'друг')}! 👋\n"
            "На связи твой бот-помощник *«Наука в MAX»*.\n\n"
            "Расскажи о себе — чем ты занимаешься?",
            reply_markup=get_role_keyboard()
        )
        return

    state = user_states.get(user_id)

    if state == "waiting_for_role" and text == "Я студент-исследователь":
        user_states[user_id] = "waiting_for_university"
        user_data[user_id]["role"] = "student"
        await send_message(chat_id, "Отлично! 🎓 Введите название университета, где вы обучаетесь:")
        return

    if state == "waiting_for_role" and text == "Я научный руководитель/преподаватель":
        user_states[user_id] = "teacher_waiting_for_university"
        user_data[user_id]["role"] = "teacher"
        await send_message(chat_id, "Введите название университета, в котором вы преподаете:")
        return

    if state == "waiting_for_role" and text == "Я представитель руководства/организации":
        user_states[user_id] = "admin_waiting_for_university"
        user_data[user_id]["role"] = "admin"
        await send_message(chat_id, "Представителем руководства какого университета вы являетесь?")
        return

    if state == "waiting_for_university":
        user_data[user_id]["university"] = text
        user_states[user_id] = "waiting_for_experience"
        await send_message(
            chat_id,
            "Ты только начинаешь свой исследовательский путь или уже был опыт НИР?",
            reply_markup=get_experience_inline_keyboard()
        )
        return

    if state == "teacher_waiting_for_university":
        user_data[user_id]["university"] = text
        user_states[user_id] = "teacher_waiting_for_direction"
        await send_message(
            chat_id,
            "Отлично! Какое из следующих направлений является вашей профессиональной сферой?\n\n"
            "*1. Технические науки*\n"
            "*2. Информационные технологии*\n"
            "*3. Экономика и бизнес*\n"
            "*4. Гуманитарные науки*\n"
            "*5. Медицина и биология*\n"
            "*6. Право и юриспруденция*\n"
            "*7. Педагогика и психология*",
            reply_markup=get_direction_inline_keyboard()
        )
        return

    if state == "admin_waiting_for_university":
        user_data[user_id]["university"] = text
        user_states[user_id] = "admin_ready"
        await send_message(
            chat_id,
            "Предлагаем познакомиться Вам с доступными функциями данного бота:\n\n"
            "*🧩 Планирование и координация НИР* — помощь в разработке стратегических планов\n"
            "*🔍 Экспертиза и консалтинг* — оценка проектов и рекомендации\n"
            "*📣 Научная коммуникация и продвижение* — конференции, форумы, PR\n"
            "*🤝 Развитие партнерства* — кооперация между вузами",
            reply_markup=get_main_menu_admin()
        )
        return

    if state == "waiting_for_experience_desc":
        user_data[user_id]["experience_desc"] = text
        user_states[user_id] = "waiting_for_direction"
        await send_message(
            chat_id,
            "Здорово, что ты интересуешься этой темой!",
            reply_markup=get_direction_inline_keyboard()
        )
        return


async def handle_callback(callback):
    user_id = callback["from"]["id"]
    msg = callback["message"]
    chat_id = msg["chat"]["id"]
    msg_id = msg["message_id"]
    data = callback["data"]
    role = user_data.get(user_id, {}).get("role")

    if data.startswith("exp_") and role == "student":
        exp_map = {"exp_0": "Не было опыта", "exp_1": "1-2 года", "exp_3": "3-5 лет", "exp_5": "Более 5 лет"}
        experience = exp_map[data]
        user_data[user_id]["experience"] = experience

        if experience == "Не было опыта":
            user_states[user_id] = "waiting_for_direction"
            await send_message(
                chat_id,
                "Здорово, что ты интересуешься этой темой!",
                reply_markup=get_direction_inline_keyboard()
            )
        else:
            user_states[user_id] = "waiting_for_experience_desc"
            await edit_message(chat_id, msg_id, "Опишите свой прошлой опыт (можно коротко):")
        return

    if data.startswith("dir_"):
        dir_map = {
            "dir_1": "1. Технические науки", "dir_2": "2. Информационные технологии",
            "dir_3": "3. Экономика и бизнес", "dir_4": "4. Гуманитарные науки",
            "dir_5": "5. Медицина и биология", "dir_6": "6. Право и юриспруденция",
            "dir_7": "7. Педагогика и психология"
        }
        direction = dir_map[data]
        user_data[user_id]["direction"] = direction

        if role == "student":
            user_states[user_id] = "waiting_for_notifications"
            await edit_message(
                chat_id,
                msg_id,
                "Отлично! 🎯 У нас часто появляются материалы по этим темам.\n\n"
                "Хочешь получать уведомления о новых публикациях?",
                reply_markup=get_notifications_keyboard()
            )
        elif role == "teacher":
            user_states[user_id] = "teacher_ready"
            await edit_message(
                chat_id,
                msg_id,
                "Отлично! А теперь давайте познакомимся с функциями этого бота:",
                reply_markup=get_main_menu_teacher()
            )
        return

    if data == "notify_yes" and role == "student":
        user_data[user_id]["notifications_enabled"] = True
        await edit_message(
            chat_id,
            msg_id,
            "Супер! 📩 Теперь я буду присылать тебе новые материалы сразу после публикации!\n\n"
            "А теперь — к функциям!",
            reply_markup=get_main_menu_student()
        )
        return

    if data == "notify_no" and role == "student":
        user_data[user_id]["notifications_enabled"] = False
        await edit_message(
            chat_id,
            msg_id,
            "Ничего страшного! 😊 В любой момент можешь включить уведомления через меню.\n\n"
            "А теперь — к функциям!",
            reply_markup=get_main_menu_student()
        )
        return

    if data.startswith("func_") and role == "student":
        texts = {
            "func_courses": "📚 *Полезные курсы*\n\n• [Основы научного письма](https://example.com)",
            "func_structure": "📑 *Структура научной работы*\n\n1. Введение\n2. Обзор литературы...",
            "func_literature": "📖 *Полезная литература*\n\n• elibrary.ru\n• cyberleninka.ru",
            "func_ideas": "💡 *Идеи для исследований*\n\n• Проекты от преподавателей\n• Актуальные темы",
            "func_format": "✏️ *Оформление*\n\n• ГОСТ 7.32–2017\n• Требования ВАК",
            "func_events": "🎤 *Конференции*\n\n• Всероссийская — 15 марта\n• Международная — 12 апреля",
            "func_team": "👥 *Поиск команды*\n\nНапиши, в каком направлении хочешь работать"
        }
        text = texts.get(data, "Функция в разработке.")
        await edit_message(chat_id, msg_id, text, reply_markup=get_back_button())
        return

    if data.startswith("t_func_") and role == "teacher":
        texts = {
            "t_func_mentor": "🧑‍🏫 *Автоматизированное сопровождение студентов*\n\n• Отслеживание прогресса\n• Напоминания о сроках",
            "t_func_master": "🎓 *Организация мастерклассов*\n\n• Подача заявок на конференции\n• Онлайн-уроки",
            "t_func_guidelines": "📚 *Методические рекомендации*\n\n• По научному руководству\n• По написанию ВКР",
            "t_func_tests": "📝 *Тесты и оценивание*\n\n• Создание опросов\n• Сбор статистики",
            "t_func_research_db": "🔬 *База исследований*\n\n• Актуальные темы\n• Подводящие темы для студентов"
        }
        text = texts.get(data, "Функция в разработке.")
        await edit_message(chat_id, msg_id, text, reply_markup=get_back_button())
        return

    if data.startswith("a_func_") and role == "admin":
        texts = {
            "a_func_planning": "🧩 *Планирование и координация НИР*\n\n• Стратегические планы\n• Междисциплинарные проекты",
            "a_func_expertise": "🔍 *Экспертиза и консалтинг*\n\n• Оценка проектов\n• Рекомендации по НИР",
            "a_func_communication": "📣 *Научная коммуникация*\n\n• Продвижение достижений\n• Организация конференций",
            "a_func_partnership": "🤝 *Развитие партнерства*\n\n• Кооперация с вузами\n• Научные сообщества"
        }
        text = texts.get(data, "Функция в разработке.")
        await edit_message(chat_id, msg_id, text, reply_markup=get_back_button())
        return

    if data == "back_to_menu":
        role = user_data.get(user_id, {}).get("role")
        if role == "student":
            kb = get_main_menu_student()
        elif role == "teacher":
            kb = get_main_menu_teacher()
        elif role == "admin":
            kb = get_main_menu_admin()
        else:
            kb = get_role_keyboard()
        await edit_message(chat_id, msg_id, "Выберите функцию:", reply_markup=kb)
        return

async def main():
    print("✅ Бот запускается...")

    # Проверка токена (опционально)
    try:
        info = await asyncio.to_thread(_sync_get, f"{BASE_URL}/getMe")
        if info.get("ok"):
            bot_info = info["result"]
            print(f"🤖 Бот: {bot_info['first_name']} (@{bot_info['username']})")
        else:
            print("⚠️ Не удалось проверить токен — продолжаем в оффлайн-режиме")
    except:
        print("⚠️ Сетевая ошибка — бот работает в локальном режиме")

    offset = None
    print("📡 Ожидаю сообщения...")
    while True:
        try:
            updates = await get_updates(offset)
            if not updates.get("ok"):
                await asyncio.sleep(1)
                continue

            for update in updates.get("result", []):
                offset = update["update_id"] + 1

                if "message" in update:
                    asyncio.create_task(handle_message(update["message"]))
                elif "callback_query" in update:
                    asyncio.create_task(handle_callback(update["callback_query"]))

        except KeyboardInterrupt:
            print("\n🛑 Бот остановлен.")
            break
        except Exception as e:
            print(f"⚠️ Ошибка: {e}")
            await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())