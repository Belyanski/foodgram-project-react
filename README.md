# Foodgram
![Python](https://img.shields.io/badge/-Python-3776AB?style=flat&logo=python&logoColor=white)
![Django](https://img.shields.io/badge/-Django-092E20?style=flat&logo=django&logoColor=white)
![Django REST framework](https://img.shields.io/badge/-Django%20REST%20framework-ff9900?style=flat&logo=django&logoColor=white)
![Postman](https://img.shields.io/badge/-Postman-FF6C37?style=flat&logo=postman&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/-PostgreSQL-336791?style=flat&logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/-Docker-2496ED?style=flat&logo=docker&logoColor=white)

## Описание проекта
Foodgram – это сайт, на котором пользователи могут публиковать рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Сервис «Список покупок» позволяет пользователям создавать список продуктов, которые нужно купить для приготовления выбранных блюд. 
## Запуск проекта на локальной машине
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

## Запуск проекта на боевом сервере
```Примечание: дальнейшии инструкции составлены на основе работы с сервером на OS Ubuntu 20.04.```

- Форкните репозиторий
- Клонируйте репозиторий на локальную машину git clone git@github.com:<ваш_аккаунт>/foodgram-project-react.git
- В файле ```nginx.conf``` замените **ip сервера** и **домен** на свои
- Предварительно авторизовавших в терминале на **DockerHub** (```docker login```) сбилдить и пушнуть образы  в директориях **backend** и **frontend**
```
docker build -t <ваше_имя_пользователя>/foodgram_backend . # в папке **backend**
docker push <ваше_имя_пользователя>/foodgram_backend
docker build -t <ваше_имя_пользователя>/foodgram_frontend .# в папке **frontend**
docker push <ваше_имя_пользователя>/foodgram_frontend
```
В файлах **docker-compose.yml** и **docker-compose.production.yml** репозитория замените во всех ```image``` имеющиеся данные на свои ```<ваше_имя_пользователя>/<имя_образа>:latest```

Подготовка сервера:
- В домашней директории сервера создать папку **foodgram** ``` mkdir foodgram``` и перейти в нее ``` cd foodgram``` 
- В директории **foodgram** создать папки **infra** и **docs**, также через ```mkdir```
- В папке **docs** разместить файлы ```openapi-schema.yml``` и ```redoc.html``` из репозитерия 
- В папке infra аналогичным способом разместить ```docker-compose.production.yml``` и ```nginx.conf```

В корневой директории проекта создайте файл с секретами ```nano .env``` и  заполните его: 

Для Django-проекта
```
SECRET_KEY                              # Секретный ключ Django-проекта
DEBUG                                   # True или False
ALLOWED_HOSTS                           # можно указать звездочку *
```
Примерные значения для БД PostgreSQL
```
POSTGRES_DB                             # foodgram 
POSTGRES_USER                           # foodgram_user
POSTGRES_PASSWORD                       # foodgram_password
DB_NAME                                 # foodgram
DB_HOST                                 # db
DB_PORT                                 # 5432
```

Замените настройки **Nginx** серверва на следующие:
``` sudo nano /etc/nginx/sites-enabled/default```
```
server {

	server_name <ваш_домен>;
	
	location / {
	   proxy_set_header Host $http_host;
	   proxy_pass http://127.0.0.1:8000;
	}

	location /admin/ {
	   proxy_set_header Host $http_host;
	   proxy_pass http://127.0.0.1:8000/admin/;
	}
}
```
Сохранитие изменение и презагрузите **Nginx** ```sudo systemctl reload nginx```.  Работу конфига можно проверить командой ```sudo nginx -t```.

В папке проекта **infra** последовательно выполните следующие команды:

```
sudo docker compose -f docker-compose.production.yml up -d
docker compose -f docker-compose.production.yml exec backend python manage.py migrate --noinput
docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic --noinput
docker compose -f docker-compose.production.yml exec backend python manage.py ingrs_loader 
docker compose -f docker-compose.production.yml exec backend python manage.py tags_loader
```
После выполнения описаннх действий проект должен стать доступным по домену. Поздравляю! 

## Автоматизация деплоя
Скорректируйте параметр ```tags``` в файле ```.github/workflows/main.yml``` под свои данные с  **Docker Hub**. Также удостоверьтесь, что на шаге ```Executing remote ssh commands to deploy``` прописан правильный путь к проекту. 

В **Settings** репозитория на **GitHub** в разделе **Secrets and variables**  создать следующие секреты:
Для Django-проекта
```
SECRET_KEY                              # Секретный ключ Django-проекта
DEBUG                                   # True или False
ALLOWED_HOSTS                           # можно указать звездочку *
```
Примерные значения для БД PostgreSQL
```
POSTGRES_DB                             # foodgram 
POSTGRES_USER                           # foodgram_user
POSTGRES_PASSWORD                       # foodgram_password
DB_NAME                                 # foodgram
DB_HOST                                 # db
DB_PORT                                 # 5432
```
Данные для авторизации на DockerHub
```
DOCKER_PASSWORD                        # Пароль
DOCKER_USERNAME                        # Логин
```
Для сервера
```
HOST                                   # Ip-адрес сервера
SSH_KEY                                # SSH-ключ
USER                                   # Имя пользователя
PASSPHRASE                             # Секретная фраза от ssh-ключа
```
Для уведомления в мессенджере Telegram
```
TELEGRAM_TOKEN                         # Токен вашего telgram-бота
TELEGRAM_TO                            # Ваш id в Telegram
```
Отправьте изменения на **GitHub** следующими командами:
```
git add .
git commit -m '<имя_коммита>'
git pushh
```
В разделе **Actions** на **GitHub** вы можете отследить ход деплоя проекта на сервере. Или можно дождаться уведомления от вашего бота в **Telegram**.

<br>[Foodgram](https://foodkilogram.ddns.net/)</br>
<br>[API Foodgram](https://foodkilogram.ddns.net/api/)</br>
<br>[Документация Foodgram](https://foodkilogram.ddns.net/api/docs/)</br>
<br>[Панель администратора](https://foodkilogram.ddns.net/admin/)</br>

#### Автор работы
[Ярослав Белянский](https://github.com/Belyanski)