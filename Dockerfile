FROM python:3.6.4-slim

RUN apt update && \
    apt install -y build-essential python3-dev git wget && \
    wget -O /usr/local/bin/wait-for-it.sh https://raw.githubusercontent.com/vishnubob/wait-for-it/55c54a5abdfb32637b563b28cc088314b162195e/wait-for-it.sh && \
    chmod +x /usr/local/bin/wait-for-it.sh

ADD . /opt/serious_bot
WORKDIR /opt/serious_bot

RUN git clone https://github.com/PixeLInc/disco.git
WORKDIR disco/

RUN python setup.py install

WORKDIR ../

RUN pip install -r requirements.txt
