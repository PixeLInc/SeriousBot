FROM python:3.6.4-slim

RUN apt update && \
    apt install -y build-essential python3-dev git

ADD . /opt/serious_bot
WORKDIR /opt/serious_bot

RUN git clone https://github.com/PixeLInc/disco.git
WORKDIR disco/

RUN python setup.py install

WORKDIR ../

RUN pip install -r requirements.txt

CMD ["bash", "start.sh"]
