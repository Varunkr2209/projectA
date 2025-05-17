FROM python:3.11-slim

WORKDIR /task3

COPY . /task3

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

CMD [ "python","task3.py" ]