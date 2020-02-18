FROM python

RUN mkdir /nostalgia

WORKDIR /nostalgia

COPY . /nostalgia

RUN pip install -e .

CMD tail -f /dev/null
