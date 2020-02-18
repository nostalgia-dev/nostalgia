FROM python

RUN ls /

WORKDIR /nostalgia

COPY . /nostalgia
RUN ls /nostalgia/nostalgia
RUN pip install -U jupyter

RUN chmod 777 /nostalgia/nostalgia/research

# RUN conda install pyahocorasick
RUN pip install -U nostalgia
ENTRYPOINT ['jupyter notebook']

