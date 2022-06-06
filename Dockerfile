FROM python:3
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR .
COPY . .
RUN pip install --upgrade pip && pip install -r requirements.txt
CMD ["python", "./backend/main.py"]