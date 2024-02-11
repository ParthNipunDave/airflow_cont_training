from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime().now(),
    'retries': 1,
    'retry_delay': timedelta(days=1)
}
dag = DAG(
    'run_python_script',
    default_args=default_args,
    description='A DAG to Continous training of model',
    schedule_interval=timedelta(days=1),  # Run once a day
)


def run_python_script():
    # Import your Python script and call its main function
    import training
    training.main()


# Define the task to run the Python script
run_script_task = PythonOperator(
    task_id='Retraining',
    python_callable=run_python_script,
    dag=dag,
)

# Define task dependencies
run_script_task
