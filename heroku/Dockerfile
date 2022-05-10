FROM python:3.8-slim

RUN mkdir -p /usr/src/app/

WORKDIR /usr/src/app/

COPY . /usr/src/app/

RUN pip install --no-cache-dir -r requirements.txt -f https://download.pytorch.org/whl/torch_stable.html
CMD ["python", "bot.py"]