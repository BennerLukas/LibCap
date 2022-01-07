# fetches Python image based on Slim
FROM python:3.8-slim

# setup working directory
WORKDIR /src

# copy folder into working directory
COPY ./ /src

# install requirements
RUN pip install -r requirements.txt

EXPOSE 5000

CMD ["python", "/src/run.py"]