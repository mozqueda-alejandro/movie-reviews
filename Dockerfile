FROM python:3.12-alpine
COPY requirements.txt .
RUN pip install --upgrade setuptools
RUN \
 apk add --no-cache postgresql-libs && \
 apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev && \
 python3 -m pip install -r requirements.txt --no-cache-dir && \
 apk --purge del .build-deps
RUN pip install -r requirements.txt
WORKDIR /app
COPY . /app
EXPOSE 5000
ENV FLASK_APP=__init__.py
CMD ["flask", "run", "--host", "0.0.0.0"]