FROM python:3.10

COPY . .

RUN pip install --upgrade pip
RUN pip install --no-cache-dir --upgrade -r Requirements.txt

RUN pip uninstall --yes werkzeug
RUN pip install -v https://github.com/pallets/werkzeug/archive/refs/tags/2.0.3.tar.gz

CMD ["python","viz.py"]
