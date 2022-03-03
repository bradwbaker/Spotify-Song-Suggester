from Models import models
from sklearn.metrics.pairwise import cosine_similarity,cosine_distances
import numpy as np


def recommend_songs(music0_music, music1_music, hypo_music):
    '''
    determine and returns which songs are most similiar to the given song.
    '''

    # Query for the recommended songs 
    given_song = Music.query.filter(Music.music == music0_music).one()
    rec_songs = Music.query.filter(Music.music == music1_music).one()

    # get word embeddings of the songs for both given song and rec songs
    given_song_vects = np.array([music.vect for music in given_song.music])
    rec_songs_vects = np.array([music.vect for music in rec_songs.music])

    # combine two word embeddings into one big 2D numpy array
    vects = np.vstack([given_song_vects, rec_songs_vects])


    # create a np array to represent the y vector 
    labels = np.concatenate([np.zeros(len(given_song.music)),
                             np.ones(len(rec_songs.music))])
    

    #import and train our logisitic regression
    log_reg = LogisticRegression()

    # train out logisitic regression
    log_reg.fit(vects, labels)

    # get the word emebeddings for our hypo_music
    hypo_music_vect = vectorize_tweet(hypo_music)

    # generate a prediction
    prediction = log_reg.predict([hypo_music_vect])

    return prediction[0] 


