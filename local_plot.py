import pandas as pd
import plotly.express as px

# Читаем файл
df = pd.read_csv('clean_data.csv')

# Фильтруем нужный ряд
df_graph = df[df['Ряд'] == 'к концу предыдущего месяца']

# Строим график
fig = px.line(df_graph, x='Дата', y='Значение', title='Индексы потребительских цен')
fig.update_layout(xaxis_tickangle=-45)
fig.show()