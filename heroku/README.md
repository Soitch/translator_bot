# translator_bot

### Todo:
* Как выбрать переводчик для конкретного пользователя(сколько памяти будем занимать дикт с увеличением)
* очищать дикт после некоторого времени без действия


### Problems:
* aiogram.utils.exceptions.NetworkError: Aiohttp client throws an error: ClientConnectorError: Cannot connect to host api.telegram.org:443 ssl:default [nodename nor servname provided, or not known]


### Heroku:
```bash
heroku container:push --app khak-rus-translator web
heroku container:release --app khak-rus-translator web
heroku logs --tail --app khak-rus-translator  
```





### Reference:
* [Creating Telegram Bot and deploying it on Heroku](https://medium.com/python4you/creating-telegram-bot-and-deploying-it-on-heroku-471de1d96554)
