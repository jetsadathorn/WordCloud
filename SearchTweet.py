import re
import sys
import json
import string
import tweepy
import tkinter as tk
import numpy as np
import matplotlib.pyplot as plt

from pymongo import MongoClient
from wordcloud import WordCloud
from tkinter import *
from pprint import pprint

#GUI
root = tk.Tk()
canvas1 = tk.Canvas(root, width = 400, height = 300,  relief = 'raised')
canvas1.pack()
root.title("Word Clouds")

#ข้อความ Word Cloud Project
label1 = tk.Label(root, text='Word Cloud Project')
label1.config(font=('helvetica', 14))
canvas1.create_window(200, 25, window=label1)

#ข้อความ Input Hashtag
label2 = tk.Label(root, text='Input Hashtag :')
label2.config(font=('helvetica', 10))
canvas1.create_window(200, 100, window=label2)

#กล่องรับ input
entry1=tk.Entry(root)
canvas1.create_window(200, 140, window=entry1)

#create main of program
def main():

    #รับ input จากกล่องรับข้อความ
    Input = entry1.get()

    #read argument input
    args = sys.argv[1:]
    try:
        get = args[0]
    except IndexError:
        get = Input
        
    choice = get

    #mongoDB create connection
    client = MongoClient('localhost', 27017)
    # localhost is server url
    # 27017 is default port of mongol server
    
    #select database collection
    db = client.quest
    
    #clear data
    db.inventory.delete_many({})
    
    #setting tweepy
    consumer_key = "FrT7b9vYcz9DQM2nN1m2j3AfW"
    consumer_secret = "ErpblvNSIVKgHZS14xLiRcpfQ9Q9CnJghB2I8WO5V4sDh8jrzE"
    access_token = "1456578477407145987-zQbvyvtPkxYrQGP3iLefE7D0fPBoOp"
    access_token_secret = "JbGWqehRY6OfffWfklalUXDVjj3UGoEIofvhn0L6xSNJn"

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)

    
    #search data
    tweets = tweepy.Cursor(api.search_tweets, q=choice , lang="en").items(100)
    
    #store data
    for tweet in tweets :
        text = re.sub(r"http\S+", "", tweet.text)
        text = re.sub(r"RT", "", text)
        text = re.sub("@[A-Za-z0-9_]+","", text)
        text = re.sub("#[A-Za-z0-9_]+","", text)
        text = re.sub("[\r|\n|\r\n]+","", text)
        text = re.sub("[^A-Za-z0-9 cls_]+","", text)

        data_set = {"text" : text}

        #insert data json to mongo DB database
        db.inventory.insert_one(data_set)
        
        
    #create variable to store text
    text_data = ""
    
    #create cursor for read mongoDB data
    cursor = db.inventory.find({})
    
    #loop for read all data in collection
    for inventory in cursor:
        #save description to temp
        #print(inventory)
        text_data += inventory['text']+'\n'
     
    #close mongoDB connection
    client.close()
    
  
    word_freq = frequency_find(text_data)             #count text
    #word_use = remove_common_words(word_freq)         #remove common
    
    text = ""
    for word in word_freq:
        #if word['count'] > 2 : 
        text += word['word'] + " " 
            
    
    #check word not null
    if(len(text) == 0) :
        print("Don't have any word.")
        return
    
    #import ข้อความใน tweet เข้าในไฟล์ data.txt
    f=open("data.txt" , "w")
    f.write(text)
    f.close()

    #command to run word clound
    word_cloud(text)


#create function to find most word in text
def frequency_find(str):
    
    # slite string into list of words
    str_list = re.split(r"\W+",str)
  
    # gives set of unique words
    unique_words = set(str_list)
    
    
  
    # loop till string values present in list str
    string = []
    for word in unique_words:             
        string.append({"word" : word, "count": str.count(word)})
    
    #sorting by count in object
    string.sort(reverse=True,key=lambda s: s['count'])
    #reverse to sort high to low , ket to set variable key to sort
    
    return string
    
#function for remove common word
def remove_common_words(str) :
    #common word we need remove
    target = {"s", "also","and","as","at","be","because","but","by","can","come","could","do","even","for","from","give","go","have","he","her","here","him","his","how","i","in","it","its","just","know","like","look","make","many","me","my","new","no","not","now","of","on","or","other","our","out","say","see","she","so","some","take","tell","than","that","the","their","them","then","there","these","they","thing","think","this","those","to","up","very","want","well","what","when","which","will","with","would","you","your","http","https","co"}
  
    #loop all word we have a
    for s in str :
        #check word is common ??
        #remove common word
        if len(s['word']) < 5 or s['word'].lower() in target :
            str.remove(s)
    
    #return word that not common
    return str
 
def word_cloud(text) :
    
    #create Word Clound Area image size 300 x 300
    x, y = np.ogrid[:800, :800]

    #set Area can plot text in circle radian 130
    mask = ((x - 400) ** 2 ) + ((y - 400) ** 2) / (2)  > 280 ** 2
    mask = 255 * mask.astype(int)
    
    # Create Word Cloud
    wc = WordCloud(background_color="black", repeat=False ,mask=mask,)
    wc.generate(text)

    #output panel of word_clounds
    plt.axis("off")
    plt.imshow(wc, interpolation="bilinear")
    plt.show()

#Gui cont.
#ปุ่มสร้าง word clouds
button1 = tk.Button(text='Create Word Clouds!', command=main, bg='brown', fg='white', font=('helvetica', 9, 'bold'))
canvas1.create_window(200, 180, window=button1)
root.mainloop()
