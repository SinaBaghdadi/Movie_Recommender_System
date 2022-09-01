## Movie Recommended System

import pandas as pd
from tkinter import *
from tkinter import ttk
from math import sqrt
import numpy as np
import warnings
warnings.filterwarnings('ignore')
##
movies_df = pd.read_csv('\DATA\moviedataset\movies.csv')
ratings_df = pd.read_csv('\DATA\moviedataset\ratings.csv')
All_Movie = movies_df.title.to_list()

''' Test 
userInput = [
            {'title':'Breakfast Club, The', 'rating':5},
            {'title':'Toy Story', 'rating':3.5},
            {'title':'Jumanji', 'rating':2},
            {'title':"Pulp Fiction", 'rating':5},
            {'title':'Akira', 'rating':4.5}
            ] 
'''
##
def MovieRecom():
    global movies_df
    global ratings_df
    #preprocessing
    movies_df['year'] = movies_df.title.str.extract('(\(\d\d\d\d\))',expand=False)
    movies_df['year'] = movies_df.year.str.extract('(\d\d\d\d)',expand=False)
    movies_df['title'] = movies_df.title.str.replace('(\(\d\d\d\d\))', '')
    movies_df['title'] = movies_df['title'].apply(lambda x: x.strip())
    movies_df = movies_df.drop('genres', 1)
    ratings_df = ratings_df.drop('timestamp', 1)
    ###
    
    Movie = [mov1.get(), mov2.get(), mov3.get(), mov4.get(), mov5.get() ]
    Rating = [float(rat1.get()), float(rat2.get()), float(rat3.get()), float(rat4.get()), float(rat5.get())]
    movie_dic = {'title':Movie, 'rating':Rating}
    ###
               
    inputMovies = pd.DataFrame(movie_dic)
    ###
    inputId = movies_df[movies_df['title'].isin(inputMovies['title'].tolist())]
    #Then merging it 
    inputMovies = pd.merge(inputId, inputMovies)
    inputMovies = inputMovies.drop('year', 1)
    #userSubset
    userSubset = ratings_df[ratings_df['movieId'].isin(inputMovies['movieId'].tolist())]
    userSubsetGroup = userSubset.groupby(['userId'])
    userSubsetGroup = sorted(userSubsetGroup,  key=lambda x: len(x[1]), reverse=True)
    userSubsetGroup = userSubsetGroup[0:100]
    ####
    #pearson Correlation
    pearsonCorrelationDict = {}

    #For every user group in our subset
    for name, group in userSubsetGroup:
        #Let's start by sorting the input and current user group so the values aren't mixed up later on
        group = group.sort_values(by='movieId')
        inputMovies = inputMovies.sort_values(by='movieId')
        #Get the N for the formula
        nRatings = len(group)
        #Get the review scores for the movies that they both have in common
        temp_df = inputMovies[inputMovies['movieId'].isin(group['movieId'].tolist())]
        #And then store them in a temporary buffer variable in a list format to facilitate future calculations
        tempRatingList = temp_df['rating'].tolist()
        #Let's also put the current user group reviews in a list format
        tempGroupList = group['rating'].tolist()
        #Now let's calculate the pearson correlation between two users, so called, x and y
        Sxx = sum([i**2 for i in tempRatingList]) - pow(sum(tempRatingList),2)/float(nRatings)
        Syy = sum([i**2 for i in tempGroupList]) - pow(sum(tempGroupList),2)/float(nRatings)
        Sxy = sum( i*j for i, j in zip(tempRatingList, tempGroupList)) - sum(tempRatingList)*sum(tempGroupList)/float(nRatings)

        #If the denominator is different than zero, then divide, else, 0 correlation.
        if Sxx != 0 and Syy != 0:
            pearsonCorrelationDict[name] = Sxy/sqrt(Sxx*Syy)
        else:
            pearsonCorrelationDict[name] = 0
    ####
    #top similar Users
    pearsonDF = pd.DataFrame.from_dict(pearsonCorrelationDict, orient='index')
    pearsonDF.columns = ['similarityIndex']
    pearsonDF['userId'] = pearsonDF.index
    pearsonDF.index = range(len(pearsonDF))
    topUsers=pearsonDF.sort_values(by='similarityIndex', ascending=False)[0:50]
    topUsersRating=topUsers.merge(ratings_df, left_on='userId', right_on='userId', how='inner')
    #Multiplies the similarity by the user's ratings
    topUsersRating['weightedRating'] = topUsersRating['similarityIndex']*topUsersRating['rating']
    #Applies a sum to the topUsers after grouping it up by userId
    tempTopUsersRating = topUsersRating.groupby('movieId').sum()[['similarityIndex','weightedRating']]
    tempTopUsersRating.columns = ['sum_similarityIndex','sum_weightedRating']
    #
    #Creates an empty recommendation dataframe
    #
    recommendation_df = pd.DataFrame()
    #Now we take the weighted average
    recommendation_df['weighted average recommendation score'] = tempTopUsersRating['sum_weightedRating']/tempTopUsersRating['sum_similarityIndex']
    recommendation_df['movieId'] = tempTopUsersRating.index
    recommendation_df = recommendation_df.sort_values(by='weighted average recommendation score', ascending=False)
    ######
    #recommended movies to user
    recommendation = movies_df.loc[movies_df['movieId'].isin(recommendation_df.head(10)['movieId'].tolist())]
    ### v_radio ###
    print(X)
    if X == 1 :
        recommendation = recommendation[recommendation['year'].astype(int) > 2000]
    ###
    recommended_mov = recommendation['title']+' ('+recommendation['year']+')'
    recommended_mov = recommended_mov.tolist()
    movi= ''
    for i, j in enumerate(recommended_mov) :
        movi = movi +str(i+1)+')'+ j +'\n'    
    Rec_Mov.insert(END, movi)
    


def update(data):
    lb.delete(0, 'end')
    for item in data :
        lb.insert('end', item)

def checkkey(word):
    global data
    value = word.widget.get()
    if value == '':
        data = All_Movie
    else :
        data = []
        for i in All_Movie :
            if value.lower() in i.lower():
                data.append(i)

    update(data)

def radio():
    global X
    X = v_radio.get()
            
## Bulid User interface

window = Tk()
tit = Label(window, text= 'Movie Recommend System',font = "75")
tit.grid(row=0,column=1)
#
mov1 = StringVar()
mov2 = StringVar()
mov3 = StringVar()
mov4 = StringVar()
mov5 = StringVar()
#
rat1 = StringVar()
rat2 = StringVar()
rat3 = StringVar()
rat4 = StringVar()
rat5 = StringVar()
#
v_radio = IntVar()
#       
input_Movie_label = Label(window, text='Input Movie Name', font=('calibre',12,'normal'))
ttk.Label(window, text='Choose Rate for Movie', font=('calibre',12,'normal')).grid(row=1,column=1, padx = 10, pady = 25)
#
search_box_L1 = Label(window, text = 'Don\'t Remember!!', font=('calibre',12,'normal'))
search_box_L2 = Label(window, text = 'Search Key Words :', font=('calibre',10,'normal'))
search_box = Entry(window, )
search_box.bind('<KeyRelease>', checkkey)
lb = Listbox(window)
update(All_Movie)

Mov_ent1 = Entry(window, textvariable= mov1)
Mov_ent2 = Entry(window, textvariable= mov2)
Mov_ent3 = Entry(window, textvariable= mov3)
Mov_ent4 = Entry(window, textvariable= mov4)
Mov_ent5 = Entry(window, textvariable= mov5)
#
R = [5, 4.5, 4, 3.5, 3, 2.5, 2, 1]
rat1_list = ttk.Combobox(window, width = 10, textvariable = rat1)
rat1_list['values']= R 
rat2_list = ttk.Combobox(window, width = 10, textvariable = rat2)
rat2_list['values'] = R 
rat3_list = ttk.Combobox(window, width = 10, textvariable = rat3)
rat3_list['values'] = R
rat4_list = ttk.Combobox(window, width = 10, textvariable = rat4)
rat4_list['values'] = R
rat5_list = ttk.Combobox(window, width = 10, textvariable = rat5)
rat5_list['values'] = R
#
#Radio1 = Checkbutton(window , text = 'After 2000', variable = v_radio, onvalue = 1, offvalue = 0, height = 2, width = 10)
Radio1 = Radiobutton(window, text = 'After 2000', variable = v_radio, value = 1, command = radio, indicator = 0,
                background = "light blue", height = 1, width = 10)
Radio2 = Radiobutton(window, text = 'All Year', variable = v_radio, value = 0, command = radio, indicator = 0,
                background = "light blue", height = 1, width = 10)
#Radio2 = Checkbutton(window , text = 'All!', variable = v_radio, value = 0)
#
bottomframe = Frame(window)
Run_but = Button(window, text='Run', command = MovieRecom, fg = "Black", bg = "green", height = 1, width = 10)
rec_mov_label = Label(window, text= 'See These Movies :', font=('calibre',12,'normal'))
#
Rec_Mov = Text(window, height = 15, width = 50)
#
search_box_L1.grid(row=1,column=2)
search_box_L2.grid(row=2,column=2)
search_box.grid(row=4,column=2)
lb.grid(row=6,column=2)
#
input_Movie_label.grid(row=1,column=0)
Mov_ent1.grid(row=2,column=0)
Mov_ent2.grid(row=3,column=0)
Mov_ent3.grid(row=4,column=0)
Mov_ent4.grid(row=5,column=0)
Mov_ent5.grid(row=6,column=0)
rat1_list.grid(row=2,column=1)
rat2_list.grid(row=3,column=1)
rat3_list.grid(row=4,column=1)
rat4_list.grid(row=5,column=1)
rat5_list.grid(row=6,column=1)
Radio1.grid(row=7, column=1)
Radio2.grid(row=8, column=1)
Run_but.grid(row=10, column=1, padx = 100)
rec_mov_label.grid(row=9, column=0)
Rec_Mov.grid(row=11, column=1)


window.mainloop()
