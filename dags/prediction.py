from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago
import os
import requests
import json

# Define the default_args dictionary
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
}

# Initialize the DAG
dag = DAG(
    'prediction_job',
    default_args=default_args,
    description='A DAG to make scheduled predictions',
    schedule_interval='*/2 * * * *',  # Runs every 2 minutes
    start_date=days_ago(1),
    catchup=False,
)

# Function to check for new data
def check_for_new_data(**kwargs):
    good_data_path = '/path/to/good_data'
    processed_files_path = '/path/to/processed_files.txt'

    # Read already processed files
    if os.path.exists(processed_files_path):
        with open(processed_files_path, 'r') as f:
            processed_files = f.read().splitlines()
    else:
        processed_files = []

    # Find new files
    new_files = [f for f in os.listdir(good_data_path) if f not in processed_files]
    if not new_files:
        return 'skip_prediction'

    # Pass new files to the next task
    kwargs['ti'].xcom_push(key='new_files', value=new_files)

# Function to make predictions
def make_predictions(**kwargs):
    new_files = kwargs['ti'].xcom_pull(key='new_files', task_ids='check_for_new_data')
    good_data_path = '/path/to/good_data'
    api_endpoint = 'http://localhost:8000/predict'

    for file_name in new_files:
        file_path = os.path.join(good_data_path, file_name)
        with open(file_path, 'r') as f:
            data = f.read()
        response = requests.post(api_endpoint, json={'data': data})
        if response.status_code == 200:
            print(f'Successfully processed {file_name}')
        else:
            print(f'Failed to process {file_name}')

    # Append processed files to the processed_files.txt
    with open('/path/to/processed_files.txt', 'a') as f:
        for file_name in new_files:
            f.write(f"{file_name}\n")

# Define the tasks
check_for_new_data_task = PythonOperator(
    task_id='check_for_new_data',
    provide_context=True,
    python_callable=check_for_new_data,
    dag=dag,
)

make_predictions_task = PythonOperator(
    task_id='make_predictions',
    provide_context=True,
    python_callable=make_predictions,
    dag=dag,
)

skip_prediction_task = PythonOperator(
    task_id='skip_prediction',
    python_callable=lambda: print("No new data to process."),
    dag=dag,
)

# Set the task dependencies
check_for_new_data_task >> [make_predictions_task, skip_prediction_task]
