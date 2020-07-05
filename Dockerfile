FROM python:3.7

COPY requirements.txt /
RUN pip3 install -r requirements.txt

COPY src/ /app
WORKDIR /app

ENV PASSWORD_MANAGER_KEY /app/.ssh/fernet_key

#ENTRYPOINT ["python", "./pswd_mgr.py"]