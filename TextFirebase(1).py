import pyrebase

config = {"apiKey": "AIzaSyDwihdWH7MJ80hAVvOA-PAwjjR2XS1Nwvo",
          "authDomain": "notes-fb865.firebaseapp.com",
          "databaseURL": "https://notes-fb865.firebaseio.com",
          "projectId": "notes-fb865",
          "storageBucket": "notes-fb865.appspot.com",
          "messagingSenderId": "417831066689"}
firebase = pyrebase.initialize_app(config)

from googletrans import Translator
from webb import webb
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.stem.snowball import SnowballStemmer

num = 1;

while True:


    db = firebase.database()
    textt = db.child("Transcripts").child(num).child("speechText").get().val();

    print(textt)
    while textt is None:
        textt = db.child("Transcripts").child(num).child("speechText").get().val();
        continue
    print(textt)
    topic = db.child("Transcripts").child(num).child("topic").get().val();

    translator = Translator()
    translator.detect(textt)

    trans=translator.translate(textt,dest='en')
    textt = trans.text

    search = list(topic)
    for i in range(len(search)):
        if search[i] == ' ':
            search[i] = '+'  # Putting '+' sign for the link to work
    searchnew = "".join(search)

    x = webb.find_all_links('https://www.google.com/search?q=' + searchnew+"+youtube")  # Searching on Google used webb library to
    # bypass google bot restriction

    k = 0
    j = 0

    y = list()

    for i in x:
        if (k > 3):
            break
        elif (i.startswith('https://')  # Bypassing all the sites we dont want to use in the variable x
              and ('youtube' in i)):
            y.append(i)
            k = k + 1
    print(y)

    print(textt)
    # textt = input("Enter Text to get summarize : ")
    stemmer = SnowballStemmer("english")
    stopWords = set(stopwords.words("english"))

    words = word_tokenize(textt)
    freqTable = dict()
    for word in words:
        word = word.lower()
        if word in stopWords:
            continue
        word = stemmer.stem(word)
        if word in freqTable:
            freqTable[word] += 1
        else:
            freqTable[word] = 1
    sentences = sent_tokenize(textt)
    sentenceValue = dict()
    for sentence in sentences:
        for word, freq in freqTable.items():
            if word in sentence.lower():
                if sentence in sentenceValue:
                    sentenceValue[sentence] += freq
                else:
                    sentenceValue[sentence] = freq

    sumValues = 0
    for sentence in sentenceValue:
        sumValues += sentenceValue[sentence]

    # Average value of a sentence from original text
    average = int(sumValues / len(sentenceValue))

    summary = ''
    temp = ""
    sumlist = list()
    ct = 1

    # print(sentences)

    for sentence in sentences:
        if (sentence in sentenceValue) and (sentenceValue[sentence] > (1.2 * average)):
            summary += " " + sentence

    if summary is "":
        summary=textt
    for i in y:
        summary+=(" "+i)

    db = firebase.database()

    # data to save
    numData = {
        "summary": summary,
        "topic": topic
    }

    # Pass the user's idToken to the push method
    results = db.child("Summary").child(num).set(numData)
    num += 1;
    print(summary)
