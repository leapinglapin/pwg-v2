FROM python:3.10-buster


ADD requirements.txt /app/requirements.txt
ADD patreonlink/patreon-python /app/patreon-python


RUN set -ex \
    && python -m venv /env \
    && /env/bin/pip install --upgrade pip \
    && /env/bin/pip install --no-cache-dir -r /app/requirements.txt


COPY . /app
WORKDIR /app

RUN /env/bin/python manage.py collectstatic --no-input

ENV VIRTUAL_ENV /env
ENV PATH /env/bin:$PATH

EXPOSE 80

CMD ["gunicorn", "--bind", "0.0.0.0:80", "--workers", "3", "shopcgt.wsgi:application"]
