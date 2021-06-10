FROM python:3.9.5-slim
ENV PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY . .
# RUN python manage.py collectstatic
RUN ["chmod", "+x", "docker-entrypoint.sh"]
ENTRYPOINT [ "./docker-entrypoint.sh" ]