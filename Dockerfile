FROM python:3
RUN pip install pipenv

WORKDIR /src
COPY Pipfile* /src/
RUN pipenv install --system --deploy

COPY . /src
CMD python manage.py runserver