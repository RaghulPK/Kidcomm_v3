from datetime import datetime, date
from math import pi

import numpy as np
import pandas as pd
import pyrebase
from bokeh.io import output_file, curdoc, show
from bokeh.layouts import layout
from bokeh.models import HoverTool
from bokeh.plotting import figure
from bokeh.transform import cumsum

from datetime import datetime
from dateutil.relativedelta import relativedelta

config = {
    "apiKey": "AIzaSyD7IYK6nNprDHxFEWWsGEfR_u13ECdlJ34",
    "authDomain": "tempbackend-7c9b3.firebaseapp.com",
    "databaseURL": "https://tempbackend-7c9b3-default-rtdb.firebaseio.com",
    "projectId": "tempbackend-7c9b3",
    "storageBucket": "tempbackend-7c9b3.appspot.com",
    "messagingSenderId": "17153523147",
    "appId": "1:17153523147:web:d597c786940c4392c08a4e",
    "measurementId": "G-W4KBLDEWDL"
}

firebase = pyrebase.initialize_app(config)

db = firebase.database()

diff_list = []

def plot_attemptsPerDay(user_df):
    # load data into a DataFrame object:
    # df = pd.DataFrame(dat)
    df = user_df
    print(df)

    dates = df['Date']
    min_date = dates[0]
    max_date = dates[0]

    dic = {}

    for i in range(0, len(dates)):
        min_date = min(min_date, dates[i])
        max_date = max(max_date, dates[i])

        if (dates[i] in dic):
            dic[dates[i]] = dic[dates[i]] + 1
        else:
            dic[dates[i]] = 1

    print(type(min_date), max_date, '$')

    min_date_object = datetime.strptime(min_date, '%d-%m-%Y')
    past_date = min_date_object - relativedelta(months=2)
    min_date = past_date.strftime('%d-%m-%Y')

    max_date_object = datetime.strptime(max_date, '%d-%m-%Y')
    future_date = max_date_object + relativedelta(months=2)
    max_date = future_date.strftime('%d-%m-%Y')

    date_generated = pd.date_range(min_date, max_date)
    date_generated_2 = date_generated.strftime("%d-%m-%Y")
    print(date_generated)
    y = []

    for i in range(len(date_generated_2)):
        if (date_generated_2[i] in dic):
            y.append(dic[date_generated_2[i]])
        else:
            y.append(0)

    # Current streak
    curr = 0
    for i in range(len(y) - 1, 0, -1):
        if (y[i] == 0):
            break
        curr += 1
    print("CURRENT STREAK : ", curr, y)
    print(date_generated[0], date_generated[len(y) - 1])
    # output_file("templates/datetime_3.html")
    curdoc().theme = 'dark_minimal'
    # Attempts every day
    x = date_generated
    pl = figure(title="Attempts History", width=755, height=355, x_axis_type="datetime",
                x_range=(date_generated[0], date_generated[len(y) - 1]), y_range=(0, 10), x_axis_label='Date',
                y_axis_label='Attempts')
    pl.title.text_font_size = '15pt'
    pl.vbar(x, top=y, width=36000000)

    # Accuracy trend
    pl_2 = figure(title="Accuracy trend", width=755, height=355, x_range=(1, len(df) + 1), y_range=(0, 100),
                  x_axis_label='Number of Attempts', y_axis_label='Averaged Accuracy')
    pl_2.title.text_font_size = '15pt'

    attempts = np.linspace(1, len(df), num=len(df))
    pl_2.line(attempts, df['Accuracy']*100, color="yellow", alpha=1, width=2)

    cr = pl_2.circle(attempts, df['Accuracy']*100, size=20, fill_color="grey", hover_fill_color="firebrick",
                     fill_alpha=0.05, hover_alpha=0.3, line_color=None, hover_line_color="white")

    pl_2.add_tools(HoverTool(tooltips=None, renderers=[cr], mode='hline'))

    # Plotting fluency curve
    pl_3 = figure(title="Fluency Trend", width=755, height=355, x_range=(1, len(df) + 1), y_range=(0, 5),
                  x_axis_label='Number of Attempts', y_axis_label='Speed (Words/Sec)')
    pl_3.title.text_font_size = '15pt'

    pl_3.line(attempts, df['Speed'], color="red", alpha=1, width=2)

    cr = pl_3.circle(attempts, df['Speed'], size=15, fill_color="grey", hover_fill_color="firebrick", fill_alpha=0.05,
                     hover_alpha=0.3, line_color=None, hover_line_color="white")

    pl_3.add_tools(HoverTool(tooltips=None, renderers=[cr], mode='hline'))

    # Difficulty levels solved
    diff = {'Easy': diff_list[0], 'Medium': diff_list[1], 'Hard': diff_list[2]}

    chart_colors = ['#44e5e2', '#e29e44', '#e244db', '#d8e244', '#eeeeee', '#56e244', '#007bff', 'black']

    data = pd.Series(diff).reset_index(name='value').rename(columns={'index': 'country'})
    data['angle'] = data['value'] / data['value'].sum() * 2 * pi
    data['color'] = chart_colors[:len(diff)]

    p = figure(title="Difficulty levels", width=755, height=355, toolbar_location=None,
               tools="hover", tooltips="@country: @value", x_range=(-0.5, 1.0))

    p.wedge(x=0, y=1, radius=0.25,
            start_angle=cumsum('angle', include_zero=True), end_angle=cumsum('angle'),
            line_color="white", fill_color='color', legend_field='country', source=data)

    p.axis.axis_label = None
    p.axis.visible = False
    p.grid.grid_line_color = None

    # show(layout([[pl, pl_2], [pl_3, p]]))
    return layout([[pl, pl_2], [pl_3, p]])
    # print(dic)

def retrieveFirebaseData(user_name):
    user_dict = (db.child("Data").child(user_name).get()).val()
    date_keys = list(user_dict.keys())

    user_data = []
    # for time stamps in a date
    for date in date_keys:
        time_keys = list(user_dict[date].keys())
        for time in time_keys:
            acc = user_dict[date][time]["Accuracy"]
            speed = user_dict[date][time]["Speed"]
            time_taken = user_dict[date][time]["Time"]
            user_data.append([date, time, acc, speed, time_taken])

    user_data_df = pd.DataFrame(user_data, columns=['Date', 'Time', 'Accuracy', 'Speed', 'Time'])
    return user_data_df


def putOnFirebaseData(data, user_name):
    today = date.today()
    current_date = today.strftime("%d-%m-%Y")

    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")

    avg_accuracy = data['Accuracy']/100
    avg_time_per_line = data['Time']
    avg_words_per_sec = data['Speed']

    data = {'Accuracy': avg_accuracy, 'Time': avg_time_per_line, 'Speed': avg_words_per_sec}
    db.child('Data').child(user_name).child(current_date).child(current_time).set(data)


def workingWithBackend(data, difficulty_list, user_name):
    global diff_list
    diff_list = difficulty_list
    putOnFirebaseData(data, user_name)
    user_data_df = retrieveFirebaseData(user_name)
    return plot_attemptsPerDay(user_data_df)