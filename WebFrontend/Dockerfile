# fetches Python image based on Slim
FROM python:3.8-slim

# setup working directory
WORKDIR /src

# install requirements
COPY requirements.txt requirements.txt
RUN pip install -U pip
RUN pip install -r requirements.txt

# copy folder into working directory
COPY ./ /src

EXPOSE 5000

CMD ["python", "/src/run.py"]