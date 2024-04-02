from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
import os
import pandas as pd
import shutil

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 4, 2),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

def process_file(**kwargs):
    raw_data_path = kwargs.get('raw_data_path', '/path/to/raw_data/')
    good_data_path = kwargs.get('good_data_path', '/path/to/good_data/')
    bad_data_path = kwargs.get('bad_data_path', '/path/to/bad_data/')
    
    files = [f for f in os.listdir(raw_data_path) if f.endswith('.csv')]
    
    for file in files:
        file_path = os.path.join(raw_data_path, file)
        try:
            # Implement your data quality checks here. This is a simple check for non-empty files.
            df = pd.read_csv(file_path)
            if not df.empty:
                shutil.move(file_path, os.path.join(good_data_path, file))
            else:
                shutil.move(file_path, os.path.join(bad_data_path, file))
        except Exception as e:
            # Move files that cause errors to bad_data_path
            shutil.move(file_path, os.path.join(bad_data_path, file))
            print(f"Error processing file {file}: {e}")

dag = DAG('csv_quality_check', default_args=default_args, schedule_interval=timedelta(days=1))

t1 = PythonOperator(
    task_id='process_file',
    python_callable=process_file,
    op_kwargs={'raw_data_path': '../../data/raw-data/',
               'good_data_path': '../../data/good-data/',
               'bad_data_path': '../../data/bad-data/'},
    dag=dag,
)

t1
