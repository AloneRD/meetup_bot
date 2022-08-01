# Meetup BOT

Телеграм бот для помощи в организации и проведении митапов. 
### Основные функциональные возможности:
![image](https://user-images.githubusercontent.com/22379662/182206278-5807a3bd-69f8-47c5-a70c-0114c4d9673e.png)

___Просмотр программы мероприятия:___  
Позволяет просмотреть всю структуру мероприятия: какие есть потоки, блоки, доклады, где и в какое время будут происходить события.

___Задать вопрос докладчику:___  
Позволяет выбрать спикера из тех что участвуют в мероприятии и задать ему вопрос. Ответ на вопрос участник получит так же в чате с ботом. Так же есть возможность просмотреть вопросы других участников и ответы на них.

___Познакомиться с интересными людьми:___  
Участник мероприятия может заполнить свою  анкету (фамилия, имя компания, должность) и получить доступ к анкетам других участников. Бот будет предлагать контакты случайным образом.

___Поддержать организаторов мероприятия:___  
С помощью бота можно отправить донат организаторам на развитие и проведение новых митапов.

___Ответить на вопрос слушателя (для спикеров мероприятия):___  
Если пользователь является спикером митапа, то у него доступна дополнительная ветка - Ответа на вопросы. Он сможет просматривать вопросы слушателей и отвечать на них в чате с ботом, ответ будет незамедлительно отправлен спрашивающему.

## Техническая информация
Проект реализован на основе фреймворка Django, он используется для администрирования данных.
### Установка
1. Установить зависимости
    ```
    pip install -r requirements.txt
    ```
1. Создать файл `.env`, в него положить токен бота и токен для приема оплат
    ```
    TG_TOKEN=<ваш токен>
    TG_PAY_TOKEN=<другой ваш токен>
    ```
    Как создать и получить токен бота: https://core.telegram.org/bots#3-how-do-i-create-a-bot  
    Как получить токен оплат: https://core.telegram.org/bots/payments#getting-a-token
1. Создать БД 
    ```
    python manage.py migrate
    ```
1. Создать администратора
    ```
    python manage.py createsuperuser
    ```
1. Бота запускать командой
    ```
    python bot_backend.py
    ```
1. Админку запускать командой
    ```
    python manage.py runserver
    ```
    Доступ по адресу http://127.0.0.1:8000/admin
