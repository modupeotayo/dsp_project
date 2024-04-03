mkdir -p ../airflow-data/config ../airflow-data/logs ../airflow-data/plugins ../airflow-data/postgres
mkdir -p ../data
python csvsplitscript.py
docker-compose up -d