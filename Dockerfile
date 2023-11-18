FROM python:3.10.5

COPY Requirements.txt .

RUN pip install --no-cache-dir -r Requirements.txt

COPY . .

CMD ["python","viz.py"]
