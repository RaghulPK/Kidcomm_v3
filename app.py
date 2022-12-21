import string
import time
from datetime import datetime, date
import csv

import pyrebase

from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_cors import CORS

# Plotting using libraries
from bokeh.plotting import figure, output_file, show
import pandas as pd
import numpy as np
from bokeh.layouts import layout
from bokeh.io import curdoc
from bokeh.models import HoverTool

app = Flask(__name__)
cors = CORS(app)

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

usersI = db.child("kidcommImages").get()
dictI = usersI.val()
img_data = list(dictI.values())

usersT = db.child("kicommText").get()
dictT = usersT.val()
story_data = list(dictT.values())

line = 1
start = 0
end = 0
time_taken = 0

performance_dict = {}

# Keeps track whether the story is currently paused or in play
story_play = 1

# Values tracker block-----------------------------------------
user_data = {'Accuracy': 0, 'Time': 0, 'Speed': 0,
              'Score': 0, 'Difficulty': [0, 0, 0], 'WrongWords': []}
accuracy = 0
total_accuracy = 0
total_time_taken = 0
total_speed = 0
# Difficulty levels
easy = 0
medium = 0
difficult = 0
# Wrong words
wrong_words_list = []
# Score
max_line_score = 0
user_line_score= 0
score = 0
total_user_score = 0
total_max_score = 0


def createWordlist(s):
    new_s = s.translate(str.maketrans('', '', string.punctuation))
    word_list = []
    lower_s = new_s.lower()
    for word in lower_s.split(" "):
        word_list.append(word)
    return word_list


def createTranscript(s, common_words):
    new_s = s.translate(str.maketrans('', '', string.punctuation))
    new_s = new_s.lower()
    word_list = []
    for word in new_s.split(" "):
        if word in common_words:
            word_list.append(word.upper())
        else:
            word_list.append(word)
    sentence = ' '.join(word_list)
    return sentence


def speechMatch(speechLine, storyLine):
    # Remove all punctuations, convert everything to lowercase
    # Create a dictionary of words (hashmap)
    # If more than half words are matched, then goto next page
    speechList = createWordlist(speechLine)
    storyList = createWordlist(storyLine)
    common_words = set(speechList) & set(storyList)
    wrong_words = set(storyList).difference((set(speechList) & set(storyList)))
    common_words_len = len(set(speechList) & set(storyList))
    total_words = len(set(storyList))
    percent_overlap = common_words_len / float(total_words)
    return percent_overlap, common_words, wrong_words


def retrieveFirebaseData():
    user_dict = (db.child("Data").child("Kalam").get()).val()

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

    with open('users.csv', 'w', newline='') as file:
        fieldnames = ['Date', 'Time', 'Accuracy', 'Speed', 'Time taken']
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        writer.writeheader()
        for row in user_data:
            writer.writerow({'Date': row[0], 'Time': row[1], 'Accuracy': row[2], 'Speed': row[3], 'Time taken': row[4]})


def plot_attemptsPerDay(df):
    dates = df['Date of Attempt']
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

    print(min_date, max_date, '$')
    date_generated = pd.date_range(min_date, max_date)
    # print('date generated : ',date_generated)
    date_generated_2 = date_generated.strftime("%Y-%m-%d")
    print(date_generated[0] == min_date)
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
    output_file("datetime_3.html")
    curdoc().theme = 'dark_minimal'
    # Attempts every day
    x = date_generated
    pl = figure(title="Attempts History", width=750, height=350, x_axis_type="datetime",
                x_range=(date_generated[0], date_generated[len(y) - 1]), y_range=(0, 2), x_axis_label='Date',
                y_axis_label='Attempts')
    pl.title.text_font_size = '15pt'
    pl.vbar(x, top=y, width=36000000)

    # Accuracy trend
    pl_2 = figure(title="Accuracy Trend", width=750, height=350, x_range=(1, len(df) + 1), y_range=(0, 100),
                  x_axis_label='Number of Attempts', y_axis_label='Averaged Accuracy')
    pl_2.title.text_font_size = '15pt'

    attempts = np.linspace(1, len(df), num=len(df))
    pl_2.line(attempts, df['Averaged accuracy(Till Now)'], color="yellow", alpha=1, width=2)

    cr = pl_2.circle(attempts, df['Averaged accuracy(Till Now)'], size=20, fill_color="grey",
                     hover_fill_color="firebrick", fill_alpha=0.05, hover_alpha=0.3, line_color=None,
                     hover_line_color="white")

    pl_2.add_tools(HoverTool(tooltips=None, renderers=[cr], mode='hline'))

    # Plotting fluency curve

    pl_3 = figure(title="Fluency Trend", width=1500, height=350, x_range=(1, len(df) + 1), y_range=(0, 5),
                  x_axis_label='Number of Attempts', y_axis_label='Speed (Words/Sec)')
    pl_3.title.text_font_size = '15pt'

    pl_3.line(attempts, df['Speed(words/sec)'], color="red", alpha=1, width=2)

    cr = pl_3.circle(attempts, df['Speed(words/sec)'], size=20, fill_color="grey", hover_fill_color="firebrick",
                     fill_alpha=0.05, hover_alpha=0.3, line_color=None, hover_line_color="white")

    pl_3.add_tools(HoverTool(tooltips=None, renderers=[cr], mode='hline'))

    # Plotting them side by side
    show(layout([[pl, pl_2], [pl_3]]))
    print(dic)


def endOfStory():
    global total_accuracy, total_time_taken, total_speed, avg_accuracy, avg_time_per_line, avg_words_per_sec
    global easy, medium, difficult
    global wrong_words_list, score
    global user_data

    avg_accuracy = round((total_accuracy / (line - 1)), 2)
    avg_time_per_line = round((total_time_taken / (line - 1)), 2)
    avg_words_per_sec = round((total_speed / (line - 1)), 2)

    today = date.today()
    current_date = today.strftime("%d-%m-%Y")

    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")

    wrong_words_set = set(wrong_words_list)
    wrong_words_ten = list(sorted(wrong_words_set, reverse=True))[:10]
    wrong_words = ""
    for word in wrong_words_ten:
        wrong_words += word + ","

    score = total_user_score / total_max_score * 100

    # print("Story data : [Avg_Accuracy, Avg_Time_taken, Avg_Speed(words/min)]")
    # print(avg_accuracy, avg_time_per_line, avg_words_per_sec)
    user_data = {'Accuracy': int(avg_accuracy * 100), 'Time': round(avg_time_per_line, 2),
                 'Speed': round(avg_words_per_sec, 2),
                 'Score': int(score), 'Difficulty': [easy, medium, difficult], 'WrongWords': wrong_words}
    print(user_data)

    return user_data
    # db.child('Data').child("Kalam").child(current_date).child(current_time).set(data)
    #
    # retrieveFirebaseData()
    #
    # df = pd.read_csv(r'D:\pythonProject\WebProject\SpeechRecognition4\Player.csv', index_col=0)
    # plot_attemptsPerDay(df)




@app.route('/')
def home_page():
    return render_template('home.html')


@app.route('/story')
def story_page():
    global line
    line = 1
    return render_template('speech_recog.html')


@app.route('/story/receiver', methods=['POST'])
def changeStory():
    global total_accuracy, avg_accuracy, total_time_taken, avg_time_per_line, avg_words_per_sec, total_speed
    global plot_flag, accuracy
    global line, start, end, time_taken, story_play
    global wrong_words_list, easy, medium, difficult
    global max_line_score, user_line_score, total_user_score, total_max_score, score

    speech_data = request.get_json()


    accuracy, common_words, wrong_words = speechMatch(speech_data, story_data[line])
    accuracy = round(accuracy, 2)

    max_line_score = len(story_data[line].split(" "))
    user_line_score = accuracy * max_line_score
    total_user_score += user_line_score
    total_max_score += max_line_score

    wrong_words_list += wrong_words

    new_transcript = createTranscript(speech_data, common_words)

    end = time.time()
    time_taken = round(end - start, 2)
    start = end

    speed = round((time_taken / len(story_data[line].split())), 2)

    # if speech is greater than threshold
    if accuracy >= 0.4 and story_play == 1:
        if line == 1:  # First line is getting wrong values for time, so omit it for time being by making them 0
            accuracy = 0
            speed = 0
            time_taken = 0

        if 0.4 <= accuracy < 0.7:
            medium += 1
        else:
            easy += 1

        total_accuracy += accuracy
        total_speed += speed
        total_time_taken += time_taken

        performance_dict[line] = [accuracy, time_taken, speed]
        print("Line:"+str(line)+" ,"+str(performance_dict[line]))

        line += 1

    image = img_data[line]

    if accuracy >= 0.4 or (accuracy == 0 and line == 2):
        data = new_transcript + ";" + image + ";" + "1" + ";" + str(line)
    else:
        data = new_transcript + ";" + image + ";" + "0" + ";" + str(line)

    accuracy = 0

    jsonified_data = jsonify(data)
    return jsonified_data


@app.route('/story/button', methods=['POST'])
def buttonDetector():
    button_data = request.get_json()
    print(button_data)
    global story_play, line, difficult
    if button_data == "PREV":
        if line != 0: line -= 1
        image = img_data[line]
        data = "_ _ _ _ _" + ";" + image + ";" + "1" + ";" + str(line)
    elif button_data == "NEXT":
        line += 1
        image = img_data[line]
        data = "_ _ _ _ _" + ";" + image + ";" + "1" + ";" + str(line)
        difficult += 1
    elif button_data == "PAUSE":
        image = img_data[line]
        data = "Story Paused" + ";" + image + ";" + "1" + ";" + str(line)
        story_play = 0
    elif button_data == "PLAY":
        image = img_data[line]
        data = "_ _ _ _ _" + ";" + image + ";" + "1" + ";" + str(line)
        story_play = 1
    return jsonify(data)


@app.route('/charts')
def charts():
    # Upload data to firebase
    return "<h1>Hello</h1>"


@app.route('/output', methods=['GET', 'POST'])
def output_page():
    if request.method == "POST":
        print("Button pressed")
        return redirect(url_for('charts'))

    performance_data = endOfStory()
    return render_template('output1.html', data=performance_data)


if __name__ == '__main__':
    app.run(debug=True)
