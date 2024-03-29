from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import PythonOperator

def print_hello():
    return 'Hello!'

def print_goodbye():
    return 'Goodbye!'

# Define the default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email': ['modupe.otayo@gmail.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Define the DAG
dag = DAG(
    'dummy_dag',
    default_args=default_args,
    description='A simple dummy DAG',
    schedule_interval=timedelta(days=1),
    start_date=datetime(2022, 1, 1),
    catchup=False,
)

# Define the tasks
start_task = DummyOperator(
    task_id='start',
    dag=dag,
)

hello_task = PythonOperator(
    task_id='print_hello',
    python_callable=print_hello,
    dag=dag,
)

goodbye_task = PythonOperator(
    task_id='print_goodbye',
    python_callable=print_goodbye,
    dag=dag,
)

end_task = DummyOperator(
    task_id='end',
    dag=dag,
)

# Set the task dependencies
start_task >> hello_task >> goodbye_task >> end_task
