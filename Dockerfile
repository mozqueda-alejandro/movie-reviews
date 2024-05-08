FROM python:3.12-slim
COPY requirements.txt .
RUN python -m pip install --upgrade pip
RUN python -m pip install --upgrade setuptools
RUN python -m pip install -r requirements.txt
WORKDIR /app
COPY . /app
EXPOSE 5000
ENV FLASK_APP=__init__.py
CMD ["flask", "run", "--host", "0.0.0.0"]