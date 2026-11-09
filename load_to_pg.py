import pandas as pd
from sqlalchemy import create_engine

print("Читаем CSV...")
df = pd.read_csv('clean_data.csv')

print("Загружаем в PostgreSQL...")

engine = create_engine('postgresql://postgres:postgres@localhost:5433/airflow_lab')

df.to_sql('indices_table', engine, if_exists='replace', index=False)

print("Готово! Таблица indices_table создана в PostgreSQL.")