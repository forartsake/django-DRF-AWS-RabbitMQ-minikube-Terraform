# My Django Project
# Version: 1.0

# FROM - Image to start building on.
FROM python:3.10.6
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# PROJECT SETUP
# ----------------

# sets the working directory
WORKDIR /usr/src/django-docker

# copy these two files from <src> to <dest>
# <src> = current directory on host machine
# <dest> = filesystem of the container
COPY Pipfile Pipfile.lock ./

# install pipenv on the container
RUN pip install -U pipenv

# install project dependencies
RUN pipenv install --system

# copy all files and directories from <src> to <dest>
COPY . .


# RUN SERVER
# ------------

# expose the port
EXPOSE 8000

# Command to run
#CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
RUN chmod +x entrypoint.sh

CMD ./entrypoint.sh