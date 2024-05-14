import logging
import os
import random
import shutil
from datetime import timedelta

import great_expectations as ge
from airflow.decorators import dag, task
from airflow.utils.dates import days_ago
from airflow.operators.python_operator import BranchPythonOperator
from airflow.operators.bash_operator import BashOperator

RAW_DATA_FOLDER = "/path/to/raw-data"
GOOD_DATA_FOLDER = "/path/to/good_data"
BAD_DATA_FOLDER = "/path/to/bad_data"


def decide_branch(**kwargs):
    # Simulate data quality validation result
    data_quality_issues = random.choice([None, "some", "all"])
    return ['split_and_save_data', 'send_alert', 'save_data_errors'] if data_quality_issues else ['split_and_save_data']


@dag(
    dag_id='data_injection',
    description='Checks for issues and separates good and bad data from the .csv file',
    tags=['dsp'],
    schedule_interval=timedelta(minutes=5),
    start_date=days_ago(n=0, hour=1)
)
def data_injection():
    @task
    def read_data():
        files = os.listdir(RAW_DATA_FOLDER)
        file = random.choice(files)
        file_path = os.path.join(RAW_DATA_FOLDER, file)
        return file_path

    @task
    def validate_data(file_path: str):
        # Use Great Expectations for data validation
        context = ge.data_context.DataContext()
        suite = context.get_expectation_suite('your_suite_name')
        df = ge.read_csv(file_path)
        results = df.validate(expectation_suite=suite)
        return results

    @task
    def split_and_save_data(file_path: str):
        if os.path.isfile(file_path):
            if not os.path.exists(GOOD_DATA_FOLDER):
                os.makedirs(GOOD_DATA_FOLDER)
            if not os.path.exists(BAD_DATA_FOLDER):
                os.makedirs(BAD_DATA_FOLDER)

            # Simulate data splitting based on validation result
            data_quality_issues = random.choice([None, "some", "all"])
            if data_quality_issues == "some":
                # Split file into good and bad data
                shutil.copy(file_path, GOOD_DATA_FOLDER)
                shutil.copy(file_path, BAD_DATA_FOLDER)
            elif data_quality_issues == "all":
                # Move file to bad data folder
                shutil.move(file_path, BAD_DATA_FOLDER)
            else:
                # Move file to good data folder
                shutil.move(file_path, GOOD_DATA_FOLDER)

    @task
    def send_alert():
        # Generate and send alert using Teams notification
        # Add your alert generation and notification logic here
        pass

    @task
    def save_data_errors(file_path: str):
        # Save detected data problems (statistics) to the database
        # Add your database saving logic here
        pass

    t1 = read_data()
    t2 = validate_data(t1.output)
    branching_task = BranchPythonOperator(
        task_id='branching_task',
        python_callable=decide_branch,
        provide_context=True,
    )

    t3 = split_and_save_data(t1.output)
    t4 = send_alert()
    t5 = save_data_errors(t1.output)

    t1 >> t2 >> branching_task
    branching_task >> [t3, t4, t5]


# Run dag
first_dag = data_injection()
