FROM python:3.12-slim
COPY requirements.txt .
RUN pip install --upgrade setuptools
RUN apk update
RUN apk add postgresql-dev gcc python3-dev musl-dev
RUN pip install -r requirements.txt
WORKDIR /app
COPY . /app
EXPOSE 5000
ENV FLASK_APP=__init__.py
CMD ["flask", "run", "--host", "0.0.0.0"]