FROM python:3.6-alpine

RUN adduser -D cirex

WORKDIR /home/cirex

RUN apk update alpine-sdk \
    && apk --no-cache --update-cache add --virtual build-dependencies \
        build-base \
        gcc \
	g++ \
	gfortran \
	libquadmath \
	cython \
	bash \
 	libc-dev \
	openblas-dev \
        wget \
        git \
    && apk add \
	
	python-dev python3-dev \
	openblas-dev \
	mariadb-dev \
	libxslt-dev \
	libxml2-dev \
	jpeg-dev \
        zlib-dev \
       	freetype-dev \
        lcms2-dev \
       	openjpeg-dev \
        tiff-dev \
        tk-dev \
        tcl-dev \
  	harfbuzz-dev \
        fribidi-dev

COPY requirements.txt requirements.txt
RUN python -m venv cirexenv

RUN cirexenv/bin/pip3 install numpy
RUN cirexenv/bin/pip3 install -r requirements.txt
#RUN ["python", "-m", "import nltk; nltk.download(['punkt', 'stopwords'])"]
RUN cirexenv/bin/python3 -m nltk.downloader -d /usr/share/nltk_data punkt
RUN cirexenv/bin/python3 -m nltk.downloader -d /usr/share/nltk_data stopwords
RUN cirexenv/bin/pip3 install gunicorn pymysql gunicorn[eventlet]

RUN apk del build-dependencies 


COPY cirex cirex
COPY migrations migrations
#COPY utilities utilities
COPY cirex_launch.py config.py boot.sh ./
RUN chmod +x boot.sh

ENV FLASK_APP cirex_launch.py

RUN chown -R cirex:cirex ./
USER cirex

EXPOSE 5000
ENTRYPOINT ["./boot.sh"]

