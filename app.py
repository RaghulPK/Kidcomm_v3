import string
import time
import csv

import pyrebase

from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_cors import CORS
from connectDB import workingWithBackend

# Plotting using libraries
from bokeh.embed import components
from bokeh.resources import CDN

import requests
from zipfile import ZipFile

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

drive_imgPaths = \
    ["https://drive.google.com/file/d/1NAR015rAWp498T_bCEuSYBQb5FAIoWy8/view?usp=sharing",
     "https://drive.google.com/file/d/1xgaOzROCiGf1qumDSwxkV24IOS7oa3jb/view?usp=sharing",
     "https://drive.google.com/file/d/1zof_WoC6DPgp-MbvI_YWCDiUG2LB7DUH/view?usp=sharing",
     "https://drive.google.com/file/d/1_mEoh9VYZQhTKvBja667aWKTD-rSZrYi/view?usp=sharing",
     "https://drive.google.com/file/d/1FyhW-1pxMwoVzYRssvkzeTX_yV0PHyF7/view?usp=sharing",
     "https://drive.google.com/file/d/1wmyYT3kHqr3cj-z-SKZQIVdXeadIgEs_/view?usp=sharing",
     "https://drive.google.com/file/d/1BQ69tSDN3s7EAH18iu2UBSsJCJjDmdUU/view?usp=sharing",
     "https://drive.google.com/file/d/1asm_CZOftj96ZHiuRBrb_LTPuTTWIxc7/view?usp=sharing",
     "https://drive.google.com/file/d/1wHpaZ90ZBGMWgBrzBg1CH2Yn--c_T3Xm/view?usp=sharing",
     "https://drive.google.com/file/d/15sG2ngJES6qK0eS6i3Kd-OiABscKxAzQ/view?usp=sharing",
     "https://drive.google.com/file/d/1cNonl2PDqJN0G2XXig2g1-DdkSvfnqRV/view?usp=sharing",
     "https://drive.google.com/file/d/1ssMcNds6VMq9UqGKuug-VOYgxpcKD4zv/view?usp=sharing",
     "https://drive.google.com/file/d/1nnO2M1Hf5qnwlSXrM4JyhEFAwMoMbVMP/view?usp=sharing",
     "https://drive.google.com/file/d/1PdXB4-40azir82o2WsyHcCzvzD_nzmAJ/view?usp=sharing",
     "https://drive.google.com/file/d/160rk1PwOhWaULUKAyvUbjyLAaDUs6VKL/view?usp=sharing",
     "https://drive.google.com/file/d/1dw_bpEvmUPOBNQv3L5aHK2ktuCJtRdPv/view?usp=sharing",
     "https://drive.google.com/file/d/1hueRpPSpphfdenzyKjxdx9Jar5i4uDBG/view?usp=sharing",
     "https://drive.google.com/file/d/1ZAWZZowOVWDP4wfO91VQbXgjeH234LSS/view?usp=sharing",
     "https://drive.google.com/file/d/1G_AvQyDZi0bAJRw2IDQ8tQV4EMm5BVJi/view?usp=sharing",
     "https://drive.google.com/file/d/1Yg38M0gHqpTKJDgC_fyB5-huChwZtAvf/view?usp=sharing"]


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


def extract_zipFile():
    print('Downloading started')
    url = "https://drive.google.com/uc?export=view&id=18D-7JyarJ__DBKKXwrOf_eE60o3vL9Dm"

    # Downloading the file by sending the request to the URL
    req = requests.get(url)

    # Writing the file to the local file system
    with open("Woodcutter.zip", 'wb') as output_file:
        output_file.write(req.content)
    print('Downloading Completed')

    # Extracting images from zip file
    with ZipFile("Woodcutter.zip", 'r') as zObject:
        zObject.extractall(path="static/images")


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


def endOfStory():
    global total_accuracy, total_time_taken, total_speed, avg_accuracy, avg_time_per_line, avg_words_per_sec
    global easy, medium, difficult
    global wrong_words_list, score
    global user_data

    avg_accuracy = round((total_accuracy / (line - 1)), 2)
    avg_time_per_line = round((total_time_taken / (line - 1)), 2)
    avg_words_per_sec = round((total_speed / (line - 1)), 2)

    wrong_words_set = set(wrong_words_list)
    wrong_words_ten = list(sorted(wrong_words_set, reverse=True))[:10]
    wrong_words = ""
    for word in wrong_words_ten:
        wrong_words += word + ","

    score = total_user_score / total_max_score * 100

    user_data = {'Accuracy': int(avg_accuracy * 100), 'Time': round(avg_time_per_line, 2),
                 'Speed': round(avg_words_per_sec, 2),
                 'Score': int(score), 'Difficulty': [easy, medium, difficult], 'WrongWords': wrong_words}
    print(user_data)

    return user_data


@app.route('/')
def home_page():
    return render_template('home.html')


@app.route('/story')
def story_page():
    global line
    line = 1
    extract_zipFile()
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
    global story_play, line, difficult, max_line_score, total_max_score
    if button_data == "PREV":
        if line != 0: line -= 1
        image = img_data[line]
        data = "_ _ _ _ _" + ";" + image + ";" + "1" + ";" + str(line)
        print(story_play)
    elif button_data == "NEXT":
        line += 1
        image = img_data[line]
        data = "_ _ _ _ _" + ";" + image + ";" + "1" + ";" + str(line)
        difficult += 1
        max_line_score = len(story_data[line].split(" "))
        total_max_score += max_line_score
        print(story_play)
    elif button_data == "PAUSE":
        image = img_data[line]
        data = "Story Paused" + ";" + image + ";" + "1" + ";" + str(line)
        story_play = 0
    elif button_data == "PLAY":
        image = img_data[line]
        data = "_ _ _ _ _" + ";" + image + ";" + "1" + ";" + str(line)
        story_play = 1
    return jsonify(data)

@app.route('/output')
def output_page():
    performance_data = endOfStory()
    return render_template('output1.html', data=performance_data)

@app.route('/plots')
def home_page2():
    g1 = workingWithBackend(user_data, [easy, medium, difficult])
    demo_script_code1 , chart_code1 = components(g1)
    cdn_js=CDN.js_files[0]
    return render_template('datetime_3.html',demo_script_code1=demo_script_code1,chart_code1=chart_code1,cdn_js=cdn_js)

if __name__ == '__main__':
    app.run(debug=True)
