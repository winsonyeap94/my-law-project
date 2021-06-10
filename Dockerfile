FROM python:3.8.10-slim-buster

LABEL maintainer="My LAW Project"

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# ODBC Drivers
RUN apt-get -y update \
    && apt-get -y install gcc g++

# Install pip requirements
COPY ./src/requirements.txt .
RUN python -m pip install psycopg2-binary
RUN python -m pip install -r requirements.txt
RUN python -m pip install gunicorn
RUN python -m pip install uvicorn

# Set PythonPath
ENV PYTHONPATH "${PYTHONPATH}:/home/my-law-project-dash/"

# Shift all codes to /app folder, otherwise there are many other folders in root
WORKDIR /home/my-law-project/
COPY . /home/my-law-project/

# Creates a non-root user and adds permission to access the /app folder
# For more info, please refer to https://aka.ms/vscode-docker-python-configure-containers
RUN useradd appuser && chown -R appuser /home/my-law-project/
USER appuser

# Exposing port
EXPOSE 6128

# Command to host app using gunicorn
 CMD ["uvicorn", "--host", "0.0.0.0", "--port", "6128", "--workers", "4", "src.api.fastapi_main:app", "--timeout-keep-alive", "300"]

