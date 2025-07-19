# TumarOne Programs Monitor Bot

https://web.telegram.org/k/#@tumaroneAlert


Telegram‑бот, который следит за появлением новых программ на платформе [Tumar.one](https://tumar.one/) и мгновенно уведомляет вас.  


---

## Алгоритм

- **OAuth2 Authorization Code Flow для получения свежих токенов авторизации**  
- **Циклический опрос API**  
- **Telegram-уведомления при появлении новых программ**  

## Тестовый json-server для отладки
```bash
cd mock-api 
./start-mock-api.sh
```
