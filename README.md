# REST API для SMIT.Studio

[Тестовое задание](https://docs.google.com/document/d/1-nWZ0dbC86Z-Z5PClyltXUWfW7TM9wGg2vyL-YFtlAQ/edit?usp=sharing)

**_Данный сервис развернут на сервере по адресу: [Документация SMITProject](http://5.104.108.168:8010/docs/)_**

## Установка

Перед началом установки убедитесь, что у вас установлен Python 3.11 и Poetry (пакетный менеджер для Python).

1. Склонируйте репозиторий:

`git clone https://github.com/192117/SMITProject.git`

2. Перейдите в директорию:

`cd SMITProject`

## Запуск приложения без Docker Compose (после пункта "Установка")

1. Установите зависимости с помощью Poetry:

`poetry install`

2. Создайте переменные окружения:

_Создайте файл .env на основе .env_example для запуска без Docker и файл .env.docker на основе .env_example для 
запуска с Docker. Оба файла содержат переменные окружения, которые требуются для настройки приложения._

3. Запустите приложеие с помощью Poetry:

`poetry run uvicorn app:app --host 0.0.0.0 --port 8000`

4. Доступ к приложению: 

- [Документация swagger](http://127.0.0.1:8000/docs/)
- [Документация redoc](http://127.0.0.1:8000/redoc/)


## Запуск приложения c использованием Docker Compose (после пункта "Установка")

1. Создайте переменные окружения:

_Создайте файл .env на основе .env_example для запуска без Docker и файл .env.docker на основе .env_example для 
запуска с Docker. Оба файла содержат переменные окружения, которые требуются для настройки приложения._

2. Запустите сборку docker-compose:

`docker compose up -d --build`

3. Доступ к приложению: 

- [Документация swagger](http://127.0.0.1:8002/docs/)
- [Документация redoc](http://127.0.0.1:8002/redoc/)
