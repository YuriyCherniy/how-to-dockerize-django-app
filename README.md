# Руководство по первоначальной настройке VDS/VPS сервера и запуску Django приложения в Docker контейнере #
##### Пройдя шаги описанные ниже вы получите контейнеризированное Django приложение подключённое к базе данных Postgresql, Настроенный Nginx, работающий в качестве прокси сервера, а также получим SSL сертификат для домена от Let's Encrypt и настроим его автоматическое обновление. #####

> Данное руководство не является ультимативным гайдом по деплою Django приложений. Это всего лишь небольшая памятка для автора этих строк, которая может быть полезна ещё кому-то. Какие-то решения могут быть неэффективными, какие-то небезопасными. Но к концу этих строк мы получим настроенный VDS/VPS сервер с работающим сайтом, настоящей базой данных и SSL сертификатом. Критика и помощь в совершенствовании приветствуется. Pull request в помощь.

## После установки системы выполнить следующие команды ##
* sudo apt update
* sudo apt upgrade
> Первая команда обновит список доступных пакетов. Вторая обновит пакеты в системе. 

## Настройка подключения к серверу по ssh ключу ##
* на локальной машине сгенерировать ssh ключ: ```ssh-keygen```
* cопировать публичный ключ на сервер: ```ssh-copy-id root@<server_ip>```
> ```<server_ip>``` - это IP адресс VDS/VPS сервера, выдается провайдером.
> После ввода команды необходимо авторизироваться на сервере по логину и паролю, полученным от провайдера после создания VDS/VPS сервера.
* подключится по ssh: ```ssh root@server_ip```
* создать нового пользователя: ```adduser <username>```
* добавить пользователя в группу sudo: ```usermod -aG sudo <username>```
* добавить копию локального открытого ключа новому пользователю: ```rsync --archive --chown=<username>:<username> ~/.ssh /home/<username>```
* переключится на нового пользователя: ```su <username>```
* протестировать права нового пользователя: ```sudo ls -a /root```
> Терминал должен отобразить папки и файла содержащиеся в /root.

## Установка Nginx и Postgresql
* sudo apt install nginx
* sudo apt install postgresql-12

## Установка Docker и Compose займёт немного больше времени
* Для установки Docker выполнить шаги из официальной документации: [Install Docker using the repository](https://docs.docker.com/engine/install/ubuntu/#install-using-the-repository)
* Для установки Compose выполнить шаги из официальной документации: [Install Compose](https://docs.docker.com/compose/install/#install-compose)

## Создание и настройка базы данных
* запустить консоль psql: ```sudo -u postgres psql```
* создать базу данных: ```CREATE DATABASE <db_name>;```
* создать пользователя: ```CREATE USER <username> WITH PASSWORD '<password>';```
* предоставеть пользователю административный доступ к базе данных: ```GRANT ALL PRIVILEGES ON DATABASE <db_name> TO <username>;```
#### Выполнить рекомендации по оптимизации Postgresql из [официальной докуметации Django](https://docs.djangoproject.com/en/3.2/ref/databases/#postgresql-notes): ####
* ```ALTER ROLE <username> SET client_encoding TO 'utf8';```
* ```ALTER ROLE <username> SET default_transaction_isolation TO 'read committed';```
* ```ALTER ROLE <username> SET timezone TO 'UTC';```
* покинуть консоль psql: ```ctr+Z```

## Создание и запуск Docker контейнера ##
Файл Dockerfile содержит инструкции по созданию Docker образа на основе которого будет создаваться и запускаться контейнер с Django приложением. Вот так выглядит наш:
```
FROM python:3.9.5-slim
ENV PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY . .
RUN ["chmod", "+x", "docker-entrypoint.sh"]
ENTRYPOINT [ "./docker-entrypoint.sh" ]
```
Образ будет создан на основе официального образа python:3.9.5-slim, туда будет скопирован файл requirements.txt, затем установятся все зависимости. Далее будут скопированны файлы нашего приложения и выполнены инструкции из файла docker-entrypoint.sh. Вот его содержимое:
```
#!/bin/bash

# Collect static files
echo "Collect static files"
python manage.py collectstatic --noinput

# Apply database migrations
echo "Apply database migrations"
python3 manage.py migrate

# Start server
echo "Starting server"
gunicorn app_to_dockerize.wsgi:application --bind 0.0.0.0:8000 --workers 3
```
Последняя строка запустит сервер приложений gunicorn для обслуживания нашего Django проекта.
Упаравлять Docker будем с помощью docker-compose. Compose обычно используется для работы с многоконтейнерными проектами, но и в данном случае docker-compose немного облегчает работу, а при развитии проекта может оказаться необходимым. Например, Compose предоставляет очень удобный интерфейс для работы с именованными томами, а они однозначно понадобятся если приложение будет немного сложнее, чем пример из этого руководства. Инструкции для docker-compose описываются в файле docker-compose.yml. Вот содержимое нашего:
```
version: "3.9"
   
services:
  web:
    build: .
    volumes:
      - ./static:/app/static
    network_mode: "host"
    restart: unless-stopped
```
Compose смотрит в Dockerfile, строит на его основе образ, а также определяет папку на хосте, куда будут собраны статические файлы. **network_mode: "host"** говорит о том, что сеть Docker контейнера будет открыта локальному хосту, без этого Nginx не увидит сеть кконтейнера. **restart: unless-stopped** говорит о том, что при перезагрузке сервера Docker контейнер будет стартовать автоматически, пока не будет остановлен намеренно.
## Всё готово, можно запускать создание и старт контейнера ##
* скачать приложение на сервер: ```git clone https://github.com/YuriyCherniy/how-to-dockerize-django-app.git```
* перейти в папку содержащую docker-compose.yml файл: ```cd how-to-dockerize-django-app/app_to_dockerize/```
* запустить создание и запуск контейнера: ```docker-compose up -d```
> ключь ```-d``` говорит о том, что контейнер будет запущен в **detached mode**. Это значит, что после создания образа и запуска контейнера, консоль будет освобождена. Если хотите видеть подробности работы приложения опустите ключ.
Для полноценной работы Django приложения необходимо создать супер юзера. Для этого необходимо запустить следующую команду ```docker exec -it <container_name> bash```
> Контейнер должен быть в запущенном состоянии. Имя контейнера можно узнать с помощью команды ```sudo docker ps```