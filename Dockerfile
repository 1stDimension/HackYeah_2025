FROM python:3.13.7-slim

WORKDIR /usr/src/app

COPY pyproject.toml ./
RUN pip install --no-cache-dir .

COPY . .

CMD [ "python", "./main.py" ]

