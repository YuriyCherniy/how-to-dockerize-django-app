# Руководство по первоначальной настройке VDS/VPS сервера и деплою Django приложения в Docker контейнере на Ubuntu Server 20.04 LTS #
Пройдя шаги описанные ниже вы получите контейнеризированное Django приложение подключённое к базе данных Postgresql, настроенный Nginx, работающий в качестве прокси сервера и обслуживающий статические файлы приложения, а также получим SSL сертификат для домена от Let's Encrypt и настроим его автоматическое обновление. **Для успешного запуска тестового приложения понадобится доменное имя и оплаченный VDS/VPS.** Руководство актуально для серверов VDS провайдера Timeweb. В других случаях могут потребоваться дополнительные настройки и установка ПО. Например для нормальной работы этого руководства на серверах Firstvds необходимо установить самостоятельно пакет ```snapd``` и убедится, что базы данных создаются с кодировкой ```UTF-8```. По умолчанию будет установлена кодировка ```LATIN1```, что может вызывать сбои в работе приложения.

> Данное руководство не является ультимативным гайдом по деплою Django приложений. Это всего лишь небольшая памятка для автора этих строк, которая может быть полезна ещё кому-то. Какие-то решения могут быть неэффективными, какие-то небезопасными. Но к концу этих строк мы получим настроенный VDS/VPS сервер с работающим сайтом, взрослой базой данных и SSL сертификатом. Критика и помощь в совершенствовании приветствуется. Pull request в помощь. 

## Подключения к серверу и первоначальная настройка ##
* подключится по ssh: ```ssh root@<server_ip>```
> ```<server_ip>``` - это IP адресс VDS/VPS сервера, выдается провайдером.
> После ввода команды необходимо авторизироваться на сервере по логину и паролю, полученным от провайдера после создания VDS/VPS сервера.
* создать нового пользователя: ```adduser <username>```
* добавить пользователя в группу sudo: ```usermod -aG sudo <username>```
* переключится на нового пользователя: ```su <username>```
* протестировать права нового пользователя: ```sudo ls -a /root```
> Терминал должен отобразить папки и файла содержащиеся в /root.

## Обновление репозиториев и установленных пакетов в системе ##

```
sudo apt update
```

```
sudo apt upgrade
```

## Установка Nginx и Postgresql

```
sudo apt install nginx
```

>```
>sudo apt install postgresql-12
>```

## Установка Docker и Compose
**Для установки Docker выполнить следующие команды:**

```
sudo apt-get install \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release
```

```
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
```

```
echo \
  "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
```

```
sudo apt-get update
```

```
sudo apt-get install docker-ce docker-ce-cli containerd.io
```

* проверить установку Docker: ```docker --version```
* За подробностями обращайтесь к официальной документации: [Install Docker using the repository](https://docs.docker.com/engine/install/ubuntu/#install-using-the-repository)

**Для установки Compose выполнить следующие команды:**

```
sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
```

```
sudo chmod +x /usr/local/bin/docker-compose
```

* проверить установку Compose: ```docker-compose --version```
* За подробностями обращайтесь к официальной документации: [Install Compose](https://docs.docker.com/compose/install/#install-compose)

## Создание и настройка базы данных
* запустить консоль psql: ```sudo -u postgres psql```
* создать базу данных: ```CREATE DATABASE <db_name>;```
* создать пользователя: ```CREATE USER <username> WITH PASSWORD '<password>';```
* предоставить пользователю административный доступ к базе данных: ```GRANT ALL PRIVILEGES ON DATABASE <db_name> TO <username>;```
> В контексте данного руководства замените ```<db_name>``` на ```test_db```, ```<username>``` на ```user_postgres```, ```<password>``` на ```0000```. В случае использования собственных значений не забудьте внести изменения в переменную [DATABASES](https://github.com/YuriyCherniy/how-to-dockerize-django-app/blob/40c67213367c43cb7d786fefcf8f557d797bc67b/app_to_dockerize/app_to_dockerize/settings.py#L78-L87). **Внимание! Не храните чувствительные данные в файлах приложения, используйте для этого переменные окружения. В данном руководстве пароли и имена пользователей хранятся в файлах приложения для просты восприятия.**
#### Выполнить рекомендации по оптимизации Postgresql из [официальной докуметации Django](https://docs.djangoproject.com/en/3.2/ref/databases/#postgresql-notes): ####
```
ALTER ROLE <username> SET client_encoding TO 'utf8';
```
```
ALTER ROLE <username> SET default_transaction_isolation TO 'read committed';
```
```
ALTER ROLE <username> SET timezone TO 'UTC';
```
* покинуть консоль psql: ```ctr+Z```

## Создание и запуск Docker контейнера ##
Файл [Dockerfile](https://github.com/YuriyCherniy/how-to-dockerize-django-app/blob/main/app_to_dockerize/Dockerfile) содержит инструкции по созданию Docker образа на основе которого будет создаваться и запускаться контейнер с Django приложением. Вот так выглядит наш:

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

Образ будет создан на основе официального образа python:3.9.5-slim, туда будет скопирован файл [requirements.txt](https://github.com/YuriyCherniy/how-to-dockerize-django-app/blob/main/app_to_dockerize/requirements.txt), затем установятся все зависимости. Далее будут скопированны файлы нашего приложения и выполнены инструкции из файла [docker-entrypoint.sh](https://github.com/YuriyCherniy/how-to-dockerize-django-app/blob/main/app_to_dockerize/docker-entrypoint.sh). Вот его содержимое:

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
Упаравлять Docker будем с помощью docker-compose. Compose обычно используется для работы с многоконтейнерными проектами, но и в данном случае docker-compose немного облегчает работу, а при развитии проекта может оказаться необходимым. Например, Compose предоставляет очень удобный интерфейс для работы с именованными томами, а они однозначно понадобятся если приложение будет немного сложнее, чем пример из этого руководства. Инструкции для docker-compose описываются в файле [docker-compose.yml](https://github.com/YuriyCherniy/how-to-dockerize-django-app/blob/main/app_to_dockerize/docker-compose.yml). Вот содержимое нашего:

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

Compose смотрит в Dockerfile, строит на его основе образ, а также определяет папку на хосте, куда будут собраны статические файлы. **network_mode: "host"** говорит о том, что сеть Docker контейнера будет открыта локальному хосту, без этого Nginx не увидит сеть контейнера. **restart: unless-stopped** говорит о том, что при перезагрузке сервера Docker контейнер будет стартовать автоматически, пока не будет остановлен намеренно.

## Всё готово, можно запускать создание и старт контейнера ##
* перейти в домашнюю директорию: ```cd ~```
* скачать Django приложение на сервер: ```git clone https://github.com/YuriyCherniy/how-to-dockerize-django-app.git```
* перейти в папку содержащую docker-compose.yml файл: ```cd how-to-dockerize-django-app/app_to_dockerize/```
* запустить создание и запуск контейнера: ```sudo docker-compose up -d```
> Ключь ```-d``` говорит о том, что контейнер будет запущен в **detached mode**. Это значит, что после создания образа и запуска контейнера, консоль будет освобождена. Если хотите видеть подробности работы приложения опустите ключ.

Для полноценной работы Django приложения необходимо создать супер пользователя. Для этого необходимо запустить следующую команду: ```sudo docker exec -it <container_name> bash```
> ```<container_name>``` необходимо заменить на имя контейнера. Контейнер должен быть в запущенном состоянии. Имя контейнера можно узнать с помощью команды ```sudo docker ps```.
Теперь можно выполнять стандартные административные команды Django находясь на одном уровне с файлом manage.py.
* создать супер пользователя: ```./manage.py createsuperuser```
* вернуться в консоль сервера: ```exit```

## Настройка Nginx в качестве прокси сервере ##
* открыть файл: ```sudo nano /etc/nginx/nginx.conf```
* удалить всё и поместить следующее содержимое:

```
events {}

http {
  include conf.d/app_to_dockerize;
}
```

* открыть файл: ```sudo nano /etc/nginx/conf.d/app_to_dockerize```
* поместить следующее содержимое:

```
include /etc/nginx/mime.types;

upstream web_app {
    server localhost:8000;
}

server {
    listen 80;
    server_name <your_domain.ru> <www.your_domain.ru>;
    location / {
        proxy_pass http://web_app;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }

    location /static/ {
        root /home/<username>/how-to-dockerize-django-app/app_to_dockerize/;
    }

}
```

> ```<your_domain.ru>``` и ```<www.your_domain.ru>``` замените на ваши доменные имена.
> ```<username>``` замените на имя пользователя операционной системы.
* проверить конфигурационные файлы Nginx на синтаксические ошибки: ```sudo nginx -t```
* перезагрузить конфигурационные файлы Nginx: ```sudo nginx -s reload```
Если всё было сделанно правильно сайт должен открываться на вашем домене по http соединению.

## Получение SSL сертификата от Let's Encrypt и настройка автоматического обновления ##
Получение и обновление сертификата будет происходить в автоматическом режиме с помощью ACME-клиента certbot, для этого выполните следующие команды:

```
sudo snap install core; sudo snap refresh core
```

```
sudo snap install --classic certbot
```

```
sudo ln -s /snap/bin/certbot /usr/bin/certbot
```

```
sudo certbot --nginx
```

* проверить возможность автоматического обнавления сертификата: ```sudo certbot renew --dry-run```

> Больше подробностей, в официальной инструкции: [certbot.eff.org](https://certbot.eff.org/lets-encrypt/ubuntufocal-nginx)

Если всё сделанно верно, сайт будет доступен по защищённому протоколу https на двух зеркалах **your_domain.ru** и **www.your_domain.ru**. Если такое поведение нежелательно необходимо настроить редирект самостоятельно.
