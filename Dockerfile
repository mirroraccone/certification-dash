FROM python:3.10

COPY . .

RUN pip install --upgrade pip
RUN pip install --no-cache-dir --upgrade -r Requirements.txt

CMD ["python","viz.py"]
