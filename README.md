# ebanko

### Who is ebanko?
Ebanko is a conversational [telegram bot](https://t.me/toxic_ebanko_bot) trained on **2ch.hk/b/**

### Infrastructure
Container network is run with [docker-compose](https://docs.docker.com/compose/). Containers include:
* Backend: **NLP** tasks are run inside Flask server. Only accessible from inside the network
* Telegram api: asynchronous [telegram api](https://github.com/python-telegram-bot/python-telegram-bot), sends requests to backend for processing
* Metrics collector: [prometheus](https://prometheus.io/) collects metrics from [telegraf](https://www.influxdata.com/time-series-platform/telegraf/) and Flask
* Metrics board: [grafana](https://grafana.com/) on port ```3000```

### How to run
* Insert your bot's token inside [bot.py](https://github.com/BlackSamorez/ebanko/blob/main/app/bot/bot.py)
* Download the model (see **Availability**) and place it in ```app/app/model```
* From ```app``` run:
```
docker-compose up --build
```
No gpu is needed

### Availability

Finetuned model is availbale at [huggingface](https://huggingface.co/BlackSamorez/rudialogpt3_medium_based_on_gpt2_2ch).
Dataset is also available [there](https://huggingface.co/datasets/BlackSamorez/2ch_b_dialogues).

### Inference speedup
* None (for now)
