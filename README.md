# Социальная сеть
Реализация Backend части социальной сети на фреймворке fastapi
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
`python3 -m uvicorn main:app --reload`
## Настройка
- database/db.py - Конфиги подключения к базе данных PostgreSQL
- auth/login.py - Конфиги авторизации пользователей
