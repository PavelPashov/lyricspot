FROM python:3.9

COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

RUN python3 -m pip install --upgrade pip

RUN python3 -m pip install -r requirements.txt

COPY . /app

EXPOSE 5000

CMD ["python3", "-m", "flask", "run", "--host", "0.0.0.0" ]