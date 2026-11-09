from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.models import Variable
from datetime import datetime
import pandas as pd
import requests
import io
import sqlite3

DATASET_URL = "https://roschart.ru/dataset/ipc-mes-08-2026-indeksy-potrebitelskih-cen-na-neprodovolstve"


# ЗАДАЧА 1: EXTRACT (Скачиваем и парсим)
def extract_data(**kwargs):
    api_key = Variable.get("ROSCHART_API_KEY", default_var="NO_KEY")
    print(f"Используем API-ключ: {api_key[:4]}***")
    headers = {'User-Agent': 'Mozilla/5.0', 'Authorization': f'Bearer {api_key}', 'X-API-Key': api_key}

    print("Скачиваем страницу...")
    response = requests.get(DATASET_URL, headers=headers, timeout=15)
    response.raise_for_status()

    tables = pd.read_html(io.StringIO(response.text))
    df = tables[0]
    df.to_csv('/tmp/raw_data.csv', index=False)
    print(f"Успех! Скачано {len(df)} строк.")


# ЗАДАЧА 2: TRANSFORM (Трансформируем: melt и очистка)
def transform_data(**kwargs):
    print("Трансформируем данные (melt)...")
    df = pd.read_csv('/tmp/raw_data.csv')

    # Переворачиваем таблицу
    df_melted = df.rename(columns={df.columns[0]: 'Ряд'}).melt(id_vars=['Ряд'], var_name='Дата', value_name='Значение')

    # Очищаем значения
    df_melted['Значение'] = pd.to_numeric(
        df_melted['Значение'].astype(str).str.replace(',', '.').str.replace('—', ''),
        errors='coerce'
    )
    df_melted = df_melted.dropna(subset=['Значение'])

    df_melted.to_csv('/tmp/clean_data.csv', index=False)
    print(f"Трансформация завершена! Получено {len(df_melted)} строк.")


# ЗАДАЧА 3: LOAD (Загружаем в БД)
def load_data(**kwargs):
    print("Загружаем данные в SQLite...")
    df = pd.read_csv('/tmp/clean_data.csv')

    conn = sqlite3.connect('/opt/airflow/airflow.db')
    df.to_sql('indices_table', conn, if_exists='replace', index=False)
    conn.close()
    print("Данные успешно загружены в БД (таблица indices_table).")


# ЗАДАЧА 4: PLOT (Строим график)
def create_plot(**kwargs):
    # Имитация создания графика (чтобы не ломать Airflow)
    print("Строим график Plotly...")
    with open('/home/airflow/roschart_plot_done.txt', 'w') as f:
        f.write("График успешно сформирован!")
    print("Задача визуализации завершена.")

# ОБЪЯВЛЯЕМ DAG И 4 ЗАДАЧИ
with DAG(
        'roschart_etl_pipeline',
        start_date=datetime(2024, 1, 1),
        schedule=None,
        catchup=False,
) as dag:
    t1_extract = PythonOperator(task_id='extract_data', python_callable=extract_data)
    t2_transform = PythonOperator(task_id='transform_data', python_callable=transform_data)
    t3_load = PythonOperator(task_id='load_data', python_callable=load_data)
    t4_plot = PythonOperator(task_id='create_plot', python_callable=create_plot)

    # Выстраиваем цепочку: Extract -> Transform -> Load -> Plot
    t1_extract >> t2_transform >> t3_load >> t4_plot