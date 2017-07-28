import sys
import datetime
from flask import Flask, request, render_template, jsonify
import random
import json
import requests
import pytz
import time
import os
import pickle
import pandas as pd
import numpy as np
from collections import Counter

app = Flask(__name__)
here = os.path.dirname(__file__)

# get student ids from ehre: https://api.slack.com/methods/users.list/test
students = ["LIST OF STUdENT NAMES"]

student_ids = [s.split('@')[1].split("|")[0] for s in students]
student_names = [s.split('(')[0] for s in students]
scores = json.loads(open('/var/www/slackFlask/static/students.json').read())


def hasAccess(data):
    if data["channel_name"] != "summer_students":
        if data["user_id"] not in student_ids or data["user_id"] in ['U1JJT2WCV', 'U1JE6D9CK', 'U1H59603D']:
            return True
        return False
    else:
        return True


def url(channel):
    if channel == "summer_students":
        return "SLACK WEBHOOK URL"
    else:
        return "SLACK WEBHOOK URL"


@app.route('/')
def index():
    return 'Index Page'

dois = list()
file = pd.read_excel('DOI DATA FILE')
for i in range(len(file)):
    dois.append([file['title'][i], file['DOI'][i]])
@app.route('/doiiiii', methods = ["POST"])
def doiiiii():
    sentence = request.form['text']
    words = sentence.split(" ")
    word = random.choice(words)
    possibleDOIs = list()
    for title in dois:
        if title[0].find(word) != -1:
            possibleDOIs.append(title[1])
    if len(possibleDOIs) == 0:
        requests.post(url(request.form['channel_name']), data = 
            json.dumps({'text':"you searched: " + sentence + ', no doi found'}))
    else:
        doi = random.choice(possibleDOIs)
        requests.post(url(request.form['channel_name']), data =
            json.dumps({'text':"you searched: " + sentence +  ", doi:" + doi}))
    return ""


@app.route('/shame', methods=["POST"])
def shame():
    if hasAccess(request.form):
        requests.post(url(request.form['channel_name']), data=json.dumps(
            {'text': 'SHAME ON <@' + request.form['text'] + '>'}))
    return ""


@app.route('/bing', methods=["POST"])
def bing():
    requests.post(url(request.form['channel_name']), data=json.dumps(
        {'text': '<http://lmgtfy.com/?q=' + request.form['text'].replace(' ', '+') + ">"}));
    return ""


@app.route('/delegate', methods=["POST"])
def delegate():
    if hasAccess(request.form):
        student = random.choice(students) + ": " + request.form['text'] + "\n\t -requested by " + \
            request.form['user_name'] + "(<@" + request.form["user_id"] + ">)"
        requests.post(url(request.form['channel_name']),
                      data=json.dumps({'text': student}))
    else:
        requests.post(url(request.form['channel_name']), data=json.dumps(
            {'text': request.form['user_name'] + "(<@" + request.form["user_id"] + ">) attempted to delegate a task, but did not have permission."}))
    return ""


@app.route('/say', methods=["POST"])
def say():
    if hasAccess(request.form):
        requests.post(url(request.form['channel_name']), data=json.dumps(
            {'text': request.form['text']}))
    else:
        requests.post(url(request.form['channel_name']), data=json.dumps(
            {'text': request.form['user_name'] + "(<@" + request.form["user_id"] + ">) attempted to say something, but did not have permission."}))
    return ""


@app.route('/pick', methods=['POST'])
def pick():
    requests.post(url(request.form['channel_name']), data=json.dumps({'text': '"' + str(random.choice(request.form['text'].split(','))) + '" was picked from ' + json.dumps(
        request.form["text"].split(',')) + "\n\t -requested by " + request.form['user_name'] + "(<@" + request.form["user_id"] + ">)"}))
    return ""


@app.route('/palindrome', methods=['POST'])
def palindrome():
    requests.post("SLACK WEBHOOK URL",
                  data=json.dumps({'text': request.form['text'][:-1] + request.form['text'][::-1]}))
    return ""


@app.route('/bathroom', methods=["POST"])
def bathroom():
    time = str(datetime.datetime.now(pytz.timezone('US/Central')))
    if request.form['text'].lower() == 'leave':
        use = ' left to use'
    elif request.form['text'].lower() == 'return':
        use = ' returned from'
    else:
        return ""

    string = request.form['user_name'] + \
        "(<@" + request.form['user_id'] + ">)" + \
        use + " the restroom at " + time + "."
    requests.post('SLACK WEBHOOK URL',
                  json.dumps({'text': string}))
    return ""


@app.route('/leaderboard', methods=["GET"])
def leaderboard():
    scores = json.loads(
        open('STUDENT SCORES DATA FILE').read())
    return render_template("leaderboard.html", scores=scores)


@app.route('/calculate')
def calculate():
    dict = {}
    for student in student_names:
        dict2 = {}
        dict2['name'] = student
        dict2['concern'] = 0
        dict2['pride'] = 0
        dict[student] = dict2
    file = open('STUDENT SCORES DATA FILE', "w")
    file.write(json.dumps(dict, indent=4))
    return ""


@app.route('/praise', methods=['POST'])
def praise():
    if hasLeaderboardAccess(request.form):
        student = request.form['text'].title()
        scores = json.loads(
            open('STUDENT SCORES DATA FILE').read())
        scores[student]["pride"] += 1
        file = open('STUDENT SCORES DATA FILE', "w")
        file.write(json.dumps(scores, indent=4))
        requests.post('SLACK WEBHOOK', json.dumps(
            {'text': student + " has been praised!""\n\t -requested by " + request.form['user_name'] + "(<@" + request.form["user_id"] + ">)"}))
        return ""
    else:
        requests.post(url(request.form['channel_name']), data=json.dumps(
            {'text': request.form['user_name'] + "(<@" + request.form["user_id"] + ">) attempted to praise someone but was denied access."}))
        return ""


@app.route('/concern', methods=['POST'])
def concern():
    if hasLeaderboardAccess(request.form):
        student = request.form['text'].title()
        print(student)
        scores = json.loads(
            open('STUDENT SCORES DATA FILE').read())
        print(scores)
        scores[student]["concern"] += 1
        file = open('STUDENT SCORES DATA FILE', "w")
        file.write(json.dumps(scores, indent=4))
        requests.post('SLACK WEBHOOK URL', json.dumps(
            {'text': student + " has exhibited concerning behavior!" + "\n\t -requested by " + request.form['user_name'] + "(<@" + request.form["user_id"] + ">)"}))

        return ""
    else:
        requests.post(url(request.form['channel_name']), data=json.dumps(
            {'text': request.form['user_name'] + "(<@" + request.form["user_id"] + ">) attempted to report concerning behavior but was denied access."}))
        return ""


def hasLeaderboardAccess(data):
    if data["user_id"] not in student_ids:
        return True
    elif data["user_id"] in ['U1JJT2WCV', 'U1JE6D9CK', 'U1H59603D']:
        return (True, "The Delegator Bot")
    else:
        return False


def hasBonsaiAccess(data):
    return data["user_id"] in ['U5T3BLJF3', 'U1H59603D']


def getBonsaiLevel(str):
    lower = str.lower()
    if lower == 'red' or lower == '1':
        return 1
    elif lower == 'yellow' or lower == '2':
        return 2
    elif lower == 'green' or lower == '3':
        return 3
    else:
        return None


def updateBonsaiData(bonsai_levels):
    output = '''$(function() {

        Morris.Area({
            element: 'morris-area-chart',
            data: ['''
    dates = bonsai_levels.keys()
    num_dates = len(dates)
    for date in dates:
        names = bonsai_levels[date].keys()
        output += '{\n' + 'time: \'' + date + '\'' + ',\n'
        num_names = len(names)
        for person in names:
            output += person + ': ' + str(bonsai_levels[date][person])
            output += '\n' if person == names[num_names - 1] else ',\n'
        output += '}\n' if date == dates[num_dates - 1] else '},\n'
    output += '''],
        xkey: 'time'
        pointSize: 2,
        hideHover: 'auto',
        resize: true
    });
});'''
    # write output to jss data file
    with open('MORRIS DATA JS FILE', 'w') as f:
        try:
            f.write(output)
        except:
            print "Could not write to file"
            print output
    return output


def me(data):
    return data["user_id"] in ['U1JJT2WCV', 'U1JE6D9CK', 'U1H59603D']


@app.route('/mypraise', methods=['POST'])
def mypraise():
    if hasLeaderboardAccess(request.form):
        student = request.form['text'].title()
        scores = json.loads(
            open('STUDENT SCORES DATA FILE').read())
        scores[student]["pride"] += 1
        file = open('STUDENT SCORES DATA FILE', "w")
        file.write(json.dumps(scores, indent=4))
        requests.post('SLACK WEBHOOK URL',
                      json.dumps({'text': student + " has been praised!""\n\t -requested by the delegator bot"}))
        return ""
    else:
        requests.post(url(request.form['channel_name']), data=json.dumps(
            {'text': request.form['user_name'] + "(<@" + request.form["user_id"] + ">) attempted to praise someone but was denied access."}))
        return ""


@app.route('/myconcern', methods=['POST'])
def myconcern():
    if me(request.form):
        student = request.form['text'].title()
        print(student)
        scores = json.loads(
            open('STUDENT SCORES DATA FILE').read())
        print(scores)
        scores[student]["concern"] += 1
        file = open('STUDENT SCORES DATA FILE', "w")
        file.write(json.dumps(scores, indent=4))
        requests.post('WEBHOOK URL', json.dumps(
            {'text': student + " has exhibited concerning behavior!" + "\n\t -requested by the delegator bot"}))

        return ""
    else:
        requests.post(url(request.form['channel_name']), data=json.dumps(
            {'text': request.form['user_name'] + "(<@" + request.form["user_id"] + ">) attempted to report concerning behavior but was denied access."}))
        return ""


bonsaiOwners = ['BONSAI TREE OWNERS']


def bonsaiPostMessage(text):
    requests.post('WEB HOOK RUL',
                  json.dumps({'text': text}))


def printBonsaiTable(values):
    names = values.keys()
    output = 'BONSAI TREES HEALTH RECORD:\n'
    n = len(names)
    for name in names:
        output += name.title() + ' is at: ' + str(values[name]) + '/3'
        output += ', ' if name != names[n - 1] else '\n'
    bonsaiPostMessage(output)


@app.route('/bonsai', methods=["POST"])
def bonsai():
    args = request.form['text'].lower().split(' ')
    num_args = len(args)
    if num_args == 0:
        bonsaiPostMessage(request.form['user_name'] + '(<@' +
                          request.form["user_id"] + '>) tried to use /bonsai.\n')
        bonsaiPostMessage(
            'Invalid input. Please say: /bonsai [name] [score out of 3 or "status"]')
        return ''
    elif args[0].lower() == 'status':
        levels = json.load(
            open('TREE HEALTH DATA'))
        date = max(levels.keys())
        user = request.form['user_name'] + \
            '(<@' + request.form["user_id"] + '>) requested bonsai status.\n'
        bonsaiPostMessage(user)
        printBonsaiTable(levels[date])
    elif num_args > 1 and args[1].lower() == 'status' and args[0].lower() in bonsaiOwners:
        levels = json.load(
            open('TREE HEALTH DATA FILE'))
        date = max(levels.keys())
        user = request.form['user_name'] + \
            '(<@' + request.form["user_id"] + '>) requested bonsai status.\n'
        bonsaiPostMessage(user)
        bonsaiPostMessage(args[0].title() + ' is at: ' +
                          str(levels[date][args[0].title()]) + '/3\n')
    elif hasBonsaiAccess(request.form):
        args = request.form['text'].lower().split(' ')
        if len(args) != 2:
            bonsaiPostMessage(
                request.form['user_name'] + '(<@' + request.form["user_id"] + '>) tried to use /bonsai.\n')
            bonsaiPostMessage(
                'Invalid input. Please say: /bonsai [name] [score out of 3 or "status"]')
            return ''
        person = args[0]
        value = getBonsaiLevel(args[1])
        if value == None or person not in bonsaiOwners:
            bonsaiPostMessage(
                request.form['user_name'] + '(<@' + request.form["user_id"] + '>) tried to use /bonsai.\n')
            bonsaiPostMessage(
                'Invalid input. Please say: /bonsai [name] [score out of 3 or "status"]')
            return ''
        levels = json.load(
            open('TREE HEALTH DATA FILE'))
        date = time.strftime('%Y-%m-%d')
        old_date = max(levels.keys())
        new_levels = {date: levels[old_date]}
        new_levels[date][person.title()] = value
        levels.update(new_levels)
        try:
            f = open('TREE HEALTH DATA FILE', 'w')
            json.dump(levels, f)
            # updateBonsaiData(levels)
            bonsaiPostMessage(
                request.form['user_name'] + '(<@' + request.form["user_id"] + '>) updated a bonsai status.\n')
            bonsaiPostMessage(
                person.title() + '\'s bonsai tree is now at health level ' + str(value) + '/3.')
        except Exception as e:
            print(e)
        # requests.post()
    else:
        bonsaiPostMessage(request.form['user_name'] + '(<@' + request.form["user_id"] +
                          '>) attempted to update a bonsai tree\'s status but was denied access. Only bonsai masters can update a bonsai tree\'s status.')
    return ''


@app.route('/trees', methods=['GET'])
def trees():
    return render_template('tree.html')


@app.route('/_ajax_tree_data')
def ajax_tree_data():
    data = json.load(open("TREE HEALTH DATA FILE"))
    data = [data[date].update({'time': date}) for date in data.keys()]
    return jsonify(data)


@app.route('/boiiiii', methods=["POST"])
def boiiiii():
    if me(request.form):
        requests.post(url(request.form['channel_name']),
                      json.dumps({'text': 'u rite'}))
    else:
        requests.post(url(request.form['channel_name']),
                      json.dumps({'text': 'u rong'}))
