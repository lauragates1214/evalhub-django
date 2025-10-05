FROM python:3.13-slim   

RUN python -m venv /venv
ENV PATH="/venv/bin:$PATH"

COPY requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt
RUN pip install "django<6" gunicorn whitenoise

COPY src /src

WORKDIR /src

RUN python manage.py collectstatic --noinput

ENV DJANGO_DEBUG_FALSE=1
ENV DJANGO_SETTINGS_MODULE=evalhub.settings.staging

RUN adduser --uid 1234 nonroot
USER nonroot

CMD ["gunicorn", "--bind", ":8888", "evalhub.wsgi:application"]