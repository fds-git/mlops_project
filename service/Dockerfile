# Install base Python image
FROM python:3.8-slim-buster

# Set working directory to previously added app directory
WORKDIR /workdir/

COPY requirements.txt ./
#RUN apt update

RUN  apt-get update \
  && apt-get install -y wget

# java для запуска spark-моделей
RUN apt install default-jdk scala git -y

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

# Install dependencies
RUN pip install -r requirements.txt

# устанавливаем spark
RUN wget https://downloads.apache.org/spark/spark-3.3.1/spark-3.3.1-bin-hadoop3.tgz
RUN tar xvf spark-3.3.1-bin-hadoop3.tgz
RUN mv spark-3.3.1-bin-hadoop3/ /opt/spark

# Set environment variable
#ENV MODEL=./fitted_model_name

# переменные окружения для spark
ENV SPARK_HOME=/opt/spark
ENV PATH=$PATH:$SPARK_HOME/bin:$SPARK_HOME/sbin

# Expose the port uvicorn is running on
EXPOSE 80

# Start
CMD ["bash", "entrypoint.sh"]