
FROM python:3.11

#WORKDIR /code

COPY requirements.txt .

RUN pip install --upgrade -r requirements.txt
RUN pip install numpy --upgrade

COPY /challenge /challenge
COPY model.json .

CMD ["uvicorn", "challenge.api:app", "--host", "0.0.0.0", "--port", "8000"]

# docker build -t latam-challenge .
# docker run -d --name latam-challenge-container -p 80:80 latam-challenge
