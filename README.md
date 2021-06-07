## настройка подключения к серверу по ssh ключу ##
* на локальной машине сгенерировать ssh ключ: ```ssh-keygen```
* cопировать публичный ключ на сервер: ```ssh-copy-id root@<server_ip>```
> ```<server_ip>``` - это IP адресс вашего VDS/VPS сервера, выдается провайдером.
> после ввода коанды неоюходимо авторизироваться на сервере по логину и паролю полученным от провайдера после создания VDS/VPS сервера.
* подключится по ssh: ```ssh root@server_ip```

```cd micro-shop/```