# ebanko

### Who is ebanko?
Ebanko is a [telegram bot](https://t.me/toxic_ebanko_bot) whose purpose is to toxify messages

### Infrastructure
Container network is run with [docker-compose](https://docs.docker.com/compose/). Containers include:
* Backend: **NLP** tasks are run inside Flask server. Only accessible from inside the network
* Telegram api: asynchronous [telegram api](https://github.com/python-telegram-bot/python-telegram-bot), sends requests to backend for processing
* Metrics collector: [prometheus](https://prometheus.io/) collects metrics from [telegraf](https://www.influxdata.com/time-series-platform/telegraf/) and Flask
* Metrics board: [grafana](https://grafana.com/) on port ```3000```

### How to run
* Insert your bot's token inside [bot.py](https://github.com/BlackSamorez/ebanko/blob/main/app/bot/bot.py)
* From ```app``` run:
```
docker-compose up --build
```
No gpu is needed

### Inference speedup
* None (for now)
