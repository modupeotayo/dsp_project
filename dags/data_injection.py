import logging
from datetime import timedelta
import os 
import random

from airflow.decorators import dag, task
from airflow.utils.dates import days_ago
from airflow.operators.python_operator import BranchPythonOperator

RAW_DATA='/home/kuzhalogi/dsp_project/raw-data'

def decide_branch(**kwargs):
    return ['task_3', 'task_4', 'task_5']

@dag(
    dag_id='data_injection',
    description=' checks for issues and separate good and bad data from the .csv file ',
    tags=['dsp'],
    schedule=timedelta(minutes=5),
    start_date=days_ago(n=0, hour=1)
)
def data_injection():
    @task
    def read_data(task_number: int) -> int:
        raw_data_folder = RAW_DATA
        files = os.listdir(raw_data_folder)
        selected_file = random.choice(files)
        to_read = os.path.join(raw_data_folder, selected_file)
        return to_read

    # @task
    # def validate_data(task_number: int, x: int) -> int:
    #     logging.info(f'Task {task_number}, x = {x}')
    #     return x + 1

    # @task
    # def split_and_save_data(task_number: int, x: int) -> int:
    #     logging.info(f'Task {task_number}, x = {x}')
    #     return x + 1

    # @task
    # def send_alert(task_number: int, x: int) -> int:
    #     logging.info(f'Task {task_number}, x = {x}')
    #     return x + 1

    # @task
    # def save_data_errors(task_number: int, x: int) -> int:
    #     logging.info(f'Task {task_number}, x = {x}')
    #     return x + 1

    # Task 1
    t1 = read_data(1)

    # Task 2
    # t2 = validate_data(2, t1)
    
    # branching_task = BranchPythonOperator(
    #     task_id='branching_task',
    #     python_callable=decide_branch,
    #     provide_context=True,
    # )

    # Parallel tasks
    # t3 = split_and_save_data(3, t2)
    # t4 = send_alert(4, t2)
    # t5 = save_data_errors(5, t2)

    # Set dependencies
    # t1 >> t2 >> [t3, t4, t5]

# Run dag
first_dag = data_injection()

