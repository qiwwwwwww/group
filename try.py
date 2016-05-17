import plotly.plotly as py
import plotly.graph_objs as go
import psycopg2
import pandas as pd

con = psycopg2.connect(dbname='energy', \
                       host='146.169.45.110', \
                       port=5432, \
                       user='postgres', \
                       password='password')

sql= "SELECT * FROM user_appliance_pie('2011-05-06 00:00:00', '2011-05-13 00:00:00', 101009)"
df = pd.read_sql(sql, con)

fig = {
       'data': [{'labels': df['appliance_group'],
                'values': df['energy_kwh'],
                'type':'pie'}],
    'layout': {'title': 'Forcasted 2014 U.S. PV Installations by Market Segment'}
}

url = py.plot(fig, filename='Pie Chart Example')