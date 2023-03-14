
FROM python:3.10.6
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# PROJECT SETUP

WORKDIR /usr/src/django-docker


COPY Pipfile Pipfile.lock ./

RUN pip install -U pipenv


RUN pipenv install --system


COPY . .

EXPOSE 8000

RUN chmod +x entrypoint.sh

CMD ./entrypoint.sh