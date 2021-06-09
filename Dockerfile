# Using miniconda instead of Python
FROM continuumio/miniconda

LABEL maintainer "My LAW Project"

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Install conda requirements
COPY ./src/environment.yml .
RUN conda env create -f environment.yml python=3.8

# Make RUN commands use the new environment:
# https://pythonspeed.com/articles/activate-conda-dockerfile/
SHELL ["conda", "run", "-n", "myenv", "/bin/bash", "-c"]

# Install gunicorn/uvicorn
RUN python -m pip install gunicorn
RUN python -m pip install uvicorn

# Shift all codes to /app folder, otherwise there are many other folders in root
WORKDIR /home/my-law-project/
COPY . /home/my-law-project/

# Set PythonPath
ENV PYTHONPATH "${PYTHONPATH}:/home/my-law-project/"

# Creates a non-root user and adds permission to access the /app folder
# For more info, please refer to https://aka.ms/vscode-docker-python-configure-containers
RUN useradd appuser && chown -R appuser /home/my-law-project/
USER appuser

# Exposing port
EXPOSE 6128

# Command to host app using gunicorn
CMD ["uvicorn", "--host", "0.0.0.0", "--port", "6128", "--workers", "1", "src.api.fastapi_main:app"]

