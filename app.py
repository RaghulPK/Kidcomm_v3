import string
import time

import pyrebase

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
cors = CORS(app)

# story_data = list()
# story_data.append("The woodcutter was cutting trees in the forest")
# story_data.append("Suddenly the axe slipped out of his hands")
# story_data.append("Oh God! My axe fell into this deep river")
# story_data.append("What would I do now")
# story_data.append("The river fairy appeared and offered help")

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

final_dict = {"Accuracy":0, "Time_taken":0, "Speed":0}
total_accuracy = 0
avg_accuracy = 0
total_time_taken = 0
avg_time_per_line = 0
total_speed = 0
avg_words_per_sec = 0

plot_flag = 0

story_play = 1

accuracy = 0

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

@app.route('/')
def hello_world():
    return render_template('speech_recog.html')

@app.route('/receiver', methods = ['POST'])
def changeStory():
    global total_accuracy, avg_accuracy, total_time_taken, avg_time_per_line, avg_words_per_sec, total_speed
    global plot_flag, accuracy
    global line, start, end, time_taken

    speech_data = request.get_json()
    accuracy, common_words, wrong_words = speechMatch(speech_data, story_data[line])
    accuracy = round(accuracy, 2)

    new_transcript = createTranscript(speech_data, common_words)

    end = time.time()
    time_taken = round(end - start, 2)
    start = end

    speed = round((time_taken / len(story_data[line].split())), 2)

    # if speech is greater than threshold
    if accuracy >= 0.4:
        if line == 1:  # First line is getting wrong values for time, so omit it for time being by making them 0
            accuracy = 0
            speed = 0
            time_taken = 0

        total_accuracy += accuracy
        total_speed += speed
        total_time_taken += time_taken

        performance_dict[line] = [accuracy, time_taken, speed]

        line += 1
        print("Line no = " + str(line))

    image = img_data[line]

    if accuracy >= 0.4 or (accuracy == 0 and line == 2):
        data = new_transcript + ";" + image + ";" + "1" + ";" + str(line)
    else:
        data = new_transcript + ";" + image + ";" + "0" + ";" + str(line)

    accuracy = 0

    print(data)
    jsonified_data = jsonify(data)
    return jsonified_data

if __name__ == '__main__':
    app.run(debug=True)
