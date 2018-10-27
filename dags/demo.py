# -*- coding: utf-8 -*-
#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
from __future__ import print_function
import airflow
from airflow.operators.python_operator import PythonOperator
from airflow.operators.bash_operator import BashOperator
from airflow.models import DAG
import os

args = {
    'owner': 'airflow',
    'start_date': airflow.utils.dates.days_ago(2)
}

dag = DAG(
    dag_id='demo_tensorflow_mnist', default_args=args,
    schedule_interval=None
)


def run():
    execfile('/root/airflow/runtime/mnist_keras.py')

# But you can if you want to
t1 = PythonOperator(
    task_id="train_and_save", python_callable=run, dag=dag,
    executor_config={"KubernetesExecutor": {"image": "tensorflow:airflow"}}
)

serve = '''tensorflow_model_server --port=8500 --rest_api_port=8501 \
  --model_name=MnistModel --model_base_path=/root/airflow/runtime/models/MnistModel'''

t2 = BashOperator(
    task_id="serve_model", bash_command=serve, dag=dag,
    executor_config={"KubernetesExecutor": {"image": "tfserving:airflow"}}
)

t1.set_downstream(t2)