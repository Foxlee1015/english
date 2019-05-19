from flask import Flask, render_template, request, flash, url_for, redirect
from wtforms import Form, SubmitField, TextAreaField, validators
import random, json, pathlib
from random import shuffle
from bs4 import BeautifulSoup
import urllib.request

app = Flask(__name__)
app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'

class input_sentent_Form(Form):
    sentence_input = TextAreaField('input', [validators.Length(min=1, max=100)])
    submit = SubmitField('문장 제출')

class search_word_Form(Form):
    word = TextAreaField('words', [validators.Length(min=1, max=10)])
    submit = SubmitField('단어 검색')

def get_verbs():
    with open("static/sentences.json", encoding='UTF8') as config_file:         # 인코딩 에러 -   encoding='UTF8' 필요
        data = json.load(config_file)
        verbs = [key for key in data["Sentences"]]                              # json 읽고, 그 안에 "Sentences" 안에 키값만 가져옴 즉, 동사 리스트 가져오기 Key = verbs, value = sentences of the verb
        return verbs

def get_sentence(verb):
    with open("static/sentences.json", encoding='UTF8') as config_file:
        data = json.load(config_file)
        return data["Sentences"][verb], data["Explanation"][verb]                # input = verb, output = the sentence, explanation of the verb

def disorder_sentence(sen1):
    sentence = sen1
    sentence_words = sentence.split(' ')
    n = len(sentence_words)
    new_sentence = []
    while n > 0:
        number = random.randint(0, n - 1)
        new_sentence.append(sentence_words[number])
        sentence_words.pop(number)
        n = len(sentence_words)
    return new_sentence

def get_data(verb):
    sen1, exp1 = get_sentence(verb)
    rd_sen = disorder_sentence(sen1)
    r_n = len(rd_sen)
    return sen1, exp1, rd_sen, r_n           # input = verb, output = the sentence, explanation of the verb, disorder_sentence of the sentence, the length of disorder_sentence

def get_random_verb():
    verbs = get_verbs()
    n = len(verbs)
    r_n = random.randint(0,n-1)
    verb = verbs[r_n]
    return verb

@app.route("/")
@app.route("/home", methods=["GET", "POST"])
def home():
    form = search_word_Form(request.form)
    print('2')
    if request.method == "POST" and form.validate():
        word = form.word.data
        word_meaning = Get_meaning(word)
        print(word_meaning)
        return render_template('home.html', word_meaning=word_meaning, form=form)
    else:
        return render_template('home.html', form=form)

@app.route("/verb")
def verb_random():
    verb = get_random_verb()
    form = input_sentent_Form(request.form)
    sen1, exp1, rd_sen, r_n = get_data(verb)
    meaning = Get_meaning(verb)
    return render_template('verb.html', form=form, rd_sen=rd_sen, r_n=r_n, exp1=exp1, verb=verb, sen=sen1, meaning=meaning)

@app.route("/verb/<string:verb>", methods=["GET", "POST"])
def verb(verb):
    form = input_sentent_Form(request.form)
    sen1, exp1, rd_sen, r_n = get_data(verb)
    meaning = Get_meaning(verb)
    if request.method == "POST" and form.validate():
        sentence_in = form.sentence_input.data
        if sen1 == sentence_in:
            flash('Correct')
            return redirect(url_for('verb_random'))
        else:
            flash('Wrong')
            return render_template('verb.html', form=form, rd_sen=rd_sen, r_n=r_n, exp1=exp1, verb=verb, sen=sen1, meaning=meaning)
    elif request.method == "POST":
        flash('Try again. (Nothing is submitted.)')
        return render_template('verb.html', form=form, rd_sen=rd_sen, r_n=r_n, exp1=exp1, verb=verb, sen=sen1, meaning=meaning)

    else:
        return render_template('verb.html', form=form, rd_sen=rd_sen, r_n=r_n, exp1=exp1, verb=verb, sen=sen1, meaning=meaning)

@app.context_processor                # verbs, n = global var
def context_processor():
    verbs = get_verbs()
    shuffle(verbs)
    n = len(verbs)
    return dict(verbs=verbs, n=n)

def Get_dicionary_meaing(verb):
    try:
        with urllib.request.urlopen("https://dictionary.cambridge.org/dictionary/english/"+verb) as response:
            html = response.read()
            soup = BeautifulSoup(html, 'html.parser')
            meaning = soup.find('b', {'class':'def'})
            if meaning == None:
                return None
            else:
                meaning = meaning.get_text()
                print(meaning)
                return meaning
    except:
        return None

def Get_meaning(verb):
    with open('static/meaning.json', 'r', encoding='utf-8') as f1:
        m_data = json.load(f1)  # 기존 데이터
        try:
            meaning = m_data[verb]
            return meaning
        except: # 크롤링 업데이트
            meaning = Get_dicionary_meaing(verb)
            data = {verb: meaning}
            m_data.update(data)    # 데이터 추가
            with open('static/meaning.json', 'w', encoding='utf-8') as f1:
                json.dump(m_data, f1) # 저장
                return meaning

if __name__ == '__main__':
    app.run(debug=True) # , host='0.0.0.0', port=5001

