FROM python:3.8
ENV PROJECT_DIR /usr/local/bin/src/app
RUN pip install pipenv
WORKDIR ${PROJECT_DIR}
COPY . ${PROJECT_DIR}/
RUN chmod +w ${PROJECT_DIR}/data/final/CIM10-CLASSIFICATION_DATASET.csv && chmod +w ${PROJECT_DIR}/data/final/log.json
RUN pipenv install --system --deploy 
EXPOSE  80
CMD ["python","app.py"]