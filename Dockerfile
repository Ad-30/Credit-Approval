FROM python:3.9.12

ENV PYTHONBUFFERED=1

RUN python -m pip install --upgrade pip

WORKDIR /django

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

COPY . .

CMD python manage.py runserver 0.0.0.0:8000
