FROM python:3.8

ENV HOME /root

WORKDIR /root

COPY . .

RUN pip3 install -r requirements.txt

EXPOSE 8080

CMD python3 manage.py makemigrations && python3 manage.py migrate && python3 manage.py runserver 0.0.0.0:8080