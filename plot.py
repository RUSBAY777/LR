import pandas as pd
import plotly.express as px

# Читаем скачанные данные
df = pd.read_csv('roschart_data.csv')

# Преобразуем таблицу
df_melted = df.rename(columns={df.columns[0]: 'Ряд'}).melt(id_vars=['Ряд'], var_name='Дата', value_name='Значение')

# Очищаем данные (на случай, если там остались прочерки)
df_melted['Значение'] = pd.to_numeric(df_melted['Значение'].astype(str).str.replace(',', '.').str.replace('—', ''), errors='coerce')
df_graph = df_melted[df_melted['Ряд'] == 'к концу предыдущего месяца'].dropna(subset=['Значение'])

# Строим график
fig = px.line(df_graph, x='Дата', y='Значение', title='Индексы потребительских цен')
fig.update_layout(xaxis_tickangle=-45)
fig.show()