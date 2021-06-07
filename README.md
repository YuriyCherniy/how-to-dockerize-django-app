## настройка ssh подключения к серверу по ключу ##
* на локальной машине сгенерировать ssh ключ: ```ssh-keygen```


копировать публичный ключ на сервер
ssh-copy-id root@ server ip

подключится по ssh
ssh root@ server ip

```cd micro-shop/```