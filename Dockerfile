FROM ubuntu:20.04

RUN apt update

RUN DEBIAN_FRONTEND=noninteractive TZ=Etc/UTC apt-get -y install git  python3-pip python3-cffi python3-brotli libpango-1.0-0 libpangoft2-1.0-0
RUN pip install pillow

RUN ln -s /usr/bin/python3 /usr/bin/python

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

EXPOSE 8000

COPY . /app

CMD  (python manage.py migrate || true) && (python manage.py collectstatic --noinput || true) && gunicorn somapi.wsgi:application --workers=2 --timeout=120  -b 0.0.0.0:8000

