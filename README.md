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
#### выполнить рекомендации по оптимизации Postgresql из [официальной докуметации Django](https://docs.djangoproject.com/en/3.2/ref/databases/#postgresql-notes): ####
* ```ALTER ROLE <username> SET client_encoding TO 'utf8';```
* ```ALTER ROLE <username> SET default_transaction_isolation TO 'read committed';```
* ```ALTER ROLE <username> SET timezone TO 'UTC';```