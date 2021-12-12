# Социальная сеть
Реализация REST-API социальной сети на фреймворке fastapi
## Установка
Требуется наличие базы данных PostgreSQL или наличие доступа к ней
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
Посмотреть, как будет функционировать сервис, можно [тут](https://fastapit-social-network.herokuapp.com/docs)
### P.S.
Если сервис выдает Internal error, то советую попробовать релиз версии v1.0.0