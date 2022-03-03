import Models.models
from sklearn.metrics.pairwise import cosine_similarity,cosine_distances
import numpy as np

from SongSuggesterApp.Models.models import Track


def recommend_songs(track0_track, track1_track, hypo_track):
    '''
    determine and returns which songs are most similiar to the given song.
    '''

    # Query for the recommended songs 
    given_song = Track.query.filter(Track.track == track0_track).one()
    rec_songs = Track.query.filter(Track.track == track1_track).one()

    # get word embeddings of the songs for both given song and rec songs
    given_song_vects = np.array([Track.vect for track in given_song.track])
    rec_songs_vects = np.array([Track.vect for track in rec_songs.track])

    # combine two word embeddings into one big 2D numpy array
    vects = np.vstack([given_song_vects, rec_songs_vects])


    # create a np array to represent the y vector 
    labels = np.concatenate([np.zeros(len(given_song.track)),
                             np.ones(len(rec_songs.track))])
    

    #import and train our logisitic regression
    log_reg = LogisticRegression()

    # train out logisitic regression
    log_reg.fit(vects, labels)

    # get the word emebeddings for our hypo_music
    hypo_track_vect = vectorize_tweet(hypo_track)

    # generate a prediction
    prediction = log_reg.predict([hypo_track_vect])

    return prediction[0] 


