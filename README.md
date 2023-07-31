# Foodgram
![Python](https://img.shields.io/badge/-Python-3776AB?style=flat&logo=python&logoColor=white)
![Django](https://img.shields.io/badge/-Django-092E20?style=flat&logo=django&logoColor=white)
![Django REST framework](https://img.shields.io/badge/-Django%20REST%20framework-ff9900?style=flat&logo=django&logoColor=white)
![Postman](https://img.shields.io/badge/-Postman-FF6C37?style=flat&logo=postman&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/-PostgreSQL-336791?style=flat&logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/-Docker-2496ED?style=flat&logo=docker&logoColor=white)

## Описание проекта
Foodgram - это сайт, на котором пользователи могут публиковать рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Сервис «Список покупок» позволяет пользователям создавать список продуктов, которые нужно купить для приготовления выбранных блюд. 
## Запуск проекта
- Клонировать репозиторий и перейти в него в командной строке:
```
git clone git@github.com:Belyanski/foodgram-project-react.git
```
```
cd foodgram-project-react
```
- Cоздать и активировать виртуальное окружение
```
python -m venv venv # Для Windows
python3 -m venv venv # Для Linux и macOS
```
```
source venv/Scripts/activate # Для Windows
source venv/bin/activate # Для Linux и macOS
```
- Установите зависимости из файла requirements.txt
```
pip install -r requirements.txt
``` 
- Перейти в папку со скриптом управления и выполнить миграции
```
cd backend/
```
- Выполните миграции
```
python manage.py migrate
```

- Запустить проект
```
python manage.py runserver
```
## Создание суперпользователя
- В директории с файлом manage.py выполнить команду
```
python manage.py createsuperuser
```
- Заполнить поля в терминале
```
Email: <ваш_email>
Username: <ваше_имя_пользователя>
First_name: <ваше_имя>
Last_name: <ваша_фамилия>
Password: <ваш_пароль>
Password (again): <повторите_ваш_пароль>
```
## Регистрация нового пользователя
- Передать на эндпоинт 127.0.0.1:8000/api/users/ данные для регистрации
```
{
  "email": "<ваш_email>",
  "username": "<ваше_имя_пользователя>",
  "first_name": "<ваше_имя>",
  "last_name": "<ваша_фамилия>",
  "password": "<ваш_пароль>"
}
```

## Получение токена
- Передать на эндпоинт http://127.0.0.1:8000/api/auth/token/login/
```
{
  "password": "<ваш_пароль>",
  "email": "<ваш_email>"
}
```

## Полная документация с доступными запросами и ответами на них
- В директории **infra/** при запущеном Docker выполнить команду **docker-compose up**
- Перейти в браузере по адресу http://localhost/api/docs/

## Автор проекта
[Ярослав Белянский](https://github.com/Belyanski)