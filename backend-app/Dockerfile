# 
FROM python:3.9

# 
WORKDIR /code

# 
COPY ./requirements.txt /code/requirements.txt

# 
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# 
COPY . /code/app

# Copy the credentials JSON file
COPY high-producer-412815-3b916fb32033.json /app/high-producer-412815-3b916fb32033.json

#
CMD uvicorn app.fast_api_backend:app --host=0.0.0.0 --port=8000
