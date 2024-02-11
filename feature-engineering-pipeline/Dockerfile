FROM bitnami/python
RUN apt-get install git
RUN pip install scikit-learn

COPY docker_random_number.py .

CMD ["python", "docker_random_number.py"]