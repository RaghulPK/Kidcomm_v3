import string
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

line = 1
firebase = pyrebase.initialize_app(config)

db = firebase.database()

usersI = db.child("kidcommImages").get()
dictI = usersI.val()
img_data = list(dictI.values())

usersT = db.child("kicommText").get()
dictT = usersT.val()
story_data = list(dictT.values())

def createWordlist(s):
    new_s = s.translate(str.maketrans('', '', string.punctuation))
    word_list = []
    lower_s = new_s.lower()
    for word in lower_s.split(" "):
        word_list.append(word)
    return word_list

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
    global line
    speech_data = request.get_json()
    accuracy, common_words, wrong_words = speechMatch(speech_data, story_data[line])
    accuracy = round(accuracy, 2)

    print("Speech :" + speech_data)
    old_line = line

    if accuracy >= 0.4:
        line += 1

    print("Line no = " + str(old_line) + "-->" + str(line))

    image = img_data[line]
    jsonified_data = jsonify(image)
    return jsonified_data

if __name__ == '__main__':
    app.run(debug=True)
