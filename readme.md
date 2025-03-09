# Telegram Support Bot

Этот бот предназначен для автоматизации технической поддержки в Telegram. Он предоставляет ответы на часто задаваемые вопросы (FAQ), позволяет пользователям задавать свои вопросы и перенаправляет их менеджерам поддержки.

## Особенности

*   **Автоматические ответы на FAQ:** Бот предоставляет ответы на часто задаваемые вопросы, хранящиеся в базе данных.
*   **Обработка произвольных вопросов:** Пользователи могут задавать свои вопросы, которые будут перенаправлены доступным менеджерам поддержки.
*   **Управление менеджерами:** Администраторы могут добавлять и удалять менеджеров поддержки.
*   **Удобный интерфейс для менеджеров:** Менеджеры могут просматривать список открытых вопросов и отвечать на них прямо через бота.
*   **История запросов:** Все вопросы и ответы сохраняются в базе данных для каждого пользователя.

## Требования

*   Python 3.6+
*   Библиотеки:
    *   `pyTelegramBotAPI`
    *   `sqlite3` (входит в стандартную библиотеку Python)
    *   `configparser` (или `python-dotenv` для переменных окружения)



4.  **Настройка базы данных:**

    База данных `support_bot.db` будет создана автоматически при первом запуске бота. Таблицы `faq`, `support_requests` и `managers` будут созданы, если их еще нет.
    Для добовления новых FAQ просто добавте их в БД.
5.  **Запуск бота:**

    ```bash
    python app.py
    ```

## Использование

1.  **Начните общение с ботом в Telegram.**
2.  **Пользователь:**

    *   Нажмите `/start`, чтобы начать.
    *   Выберите вопрос из списка FAQ.
    *   Нажмите кнопку "Написать свой вопрос", чтобы задать произвольный вопрос.

3.  **Менеджер поддержки:**

    *   Отправьте команду `/menejinbot`, чтобы стать менеджером поддержки.
    *   Менеджер получит кнопку "Ответить на вопрос".
    *   Нажмите кнопку "Ответить на вопрос", чтобы увидеть список открытых вопросов.
    *   Выберите вопрос, на который хотите ответить.
    *   Введите ответ и отправьте его.  Пользователь получит ответ на свой вопрос.
## Команды бота

*   `/start` - Начать работу с ботом.
*   `/menejinbot` - Зарегистрироваться как менеджер поддержки.
*   

## Структура базы данных

*   **`faq`**

    *   `id` (INTEGER PRIMARY KEY AUTOINCREMENT)
    *   `question` (TEXT UNIQUE NOT NULL)
    *   `answer` (TEXT NOT NULL)

*   **`support_requests`**

    *   `id` (INTEGER PRIMARY KEY AUTOINCREMENT)
    *   `user_id` (INTEGER NOT NULL)
    *   `question` (TEXT)
    *   `answer` (TEXT)
    *   `manager_id` (INTEGER)
    *   `status` (TEXT DEFAULT 'new')
    *   `created_at` (DATETIME DEFAULT CURRENT_TIMESTAMP)


.

## Благодарности

Спасибо библиотеке `pyTelegramBotAPI` за простоту и удобство использования!

