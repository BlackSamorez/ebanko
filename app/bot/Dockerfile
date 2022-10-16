FROM python:3.7

COPY requirements.txt .
RUN pip3 install -r requirements.txt

RUN mkdir /bot
WORKDIR /bot

COPY bot.py database.py /bot/

ENTRYPOINT ["python3", "bot.py"]
