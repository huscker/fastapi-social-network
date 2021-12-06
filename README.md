# Социальная сеть
Реализация REST-API социальной сети на фреймворке fastapi
## Установка
#### Ubuntu
Установка python3:  
`sudo apt update`  
`sudo apt install python3 python3-pip`  
Установка зависимостей:  
`pip3 install -r requirements.txt` 
#### Arch Linux
Установка python3:  
`pacman -Sy python python-pip`  
Установка зависимостей:  
`pip3 install -r requirements.txt`  
## Запуск
`python3 -m uvicorn main:app --port 80 --host 0.0.0.0`
## Настройка
- configs/db.py - Конфиги подключения к базе данных PostgreSQL
- configs/auth.py - Конфиги авторизации пользователей
## Пример работы
Чтобы просмотреть как будет функционировать сервис, можно перейти по [тут](http://167.99.41.97/docs) или [тут](https://fastapit-social-network.herokuapp.com/docs)
