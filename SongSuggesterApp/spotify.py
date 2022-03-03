import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from os import getenv
from models import DB, Track
import numpy as np

CLIENT_ID = getenv('SPOTIFY_CLIENT_ID')
CLIENT_SECRET = getenv('SPOTIFY_CLIENT_SECRET')

client_credentials_manager = SpotifyClientCredentials(client_id=CLIENT_ID,
                                                      client_secret=CLIENT_SECRET)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)


def search_tracks(n_tracks=100, artist=None, name=None):
    '''Returns a list of dictionaries
       Each dictionary contains a track's
       id, name, artists, and album
    '''
    tracks = []

    # track limit
    n_tracks = min(n_tracks, 1000)

    # generate query string
    query = ''
    if artist:
        query += f'artist:{artist}'
        if name:
            query += f' track:{name}'
    else:
        if name:
            query += f'track:{name}'
        else:
            print('error: no search parameters entered')
            return

    # results are limited to 1000 items
    #  and each search will only return 50 items
    #  so we have to loop over them with an offset index
    n = 0  # number of tracks found
    for i in range(0, 1000, 50):
        result = sp.search(q=query,
                           type='track',
                           limit=50,
                           offset=i)['tracks']['items']
        for track in result:
            tracks.append({'id': track['id'],
                           'name': track['name'],
                           'artists': track['artists'][0]['name'],
                           'album': track['album']['name']})
            n += 1
            # stops looking at songs if enough were found
            if n >= n_tracks:
                break
        # stops querying if spotify is out of results
        # or if enough tracks were found
        if len(result) < 50 or n >= n_tracks:
            break
    return tracks


def find_track_info(track_id):
    '''Returns a tuple with information about the track
       (name_of_track, track_artists, audio_features)
       name_of_track --- string
       track_artists -- string
       audio_features -- numpy array containing
            audio features in alphabetic order:
                acousticness
                danceability
                duration_ms
                energy
                instrumentalness
                key
                liveness
                loudness
                mode
                speechiness
                tempo
                time_signature
                valence
    '''
    result = sp.audio_features(track_id)[0]
    vector = np.array([
        result['acousticness'],
        result['danceability'],
        result['duration_ms'],
        result['energy'],
        result['instrumentalness'],
        result['key'],
        result['liveness'],
        result['loudness'],
        result['mode'],
        result['speechiness'],
        result['tempo'],
        result['time_signature'],
        result['valence']
    ])
    name = sp.track(track_id)['name']
    artists = sp.track(track_id)['artists'][0]['name']
    return name, artists, vector


def add_track_to_db(track_id, preference=False):
    '''Returns 0 if failed to add, 1 if successfully added'''
    added = 0
    try:
        # spotify keeps giving song duplicates...
        # this check doesn't even work half the time
        # no idea what is going on, server/DB issues?
        already_exists = Track.query.filter(Track.id == track_id).all()
        if already_exists:
            print(f'{track_id} already in database, skipping...')
        else:
            name, artists, vector = find_track_info(track_id)

            new_track = Track(id=track_id,
                              preference=preference,
                              name=name,
                              artists=artists,
                              vector=vector)

            DB.session.add(new_track)

    except Exception as error:
        print(f"Could not add {track_id} to database: {error}")
        pass
    else:
        DB.session.commit()
        added = 1

    return added


def update_tracks_in_db(num_tracks=1000):
    '''Adds new hipster tracks 
       directly to the database
       with all information updated
       (very slow)'''

    # Request Cap
    num_tracks = min(num_tracks, 1000)

    # Parameters
    max_tracks_per_album = 3

    # Remove old tracks
    try:
        Track.query.filter(Track.preference == False).delete()
    except Exception as error:
        print(f'error deleting tracks: {error}')
        raise error
    else:
        DB.session.commit()

    i = 0  # num_tracks added
    j = 0  # number of albums looked at
    while i < num_tracks:
        # Find Hipster Albums
        albums = sp.search(q="tag:hipster tag:new",
                           type='album',
                           limit=50,
                           offset=j)['albums']['items']
        # Find Tracks in each Album
        for album in albums:
            tracks = sp.album_tracks(album['id'],
                                     limit=max_tracks_per_album)['items']
            # Add each Track to Database
            for result in tracks:
                i += add_track_to_db(track_id=result['id'])
                # stops searching tracks after num_tracks
                if i >= num_tracks:
                    break
            # stops searching albums after num_tracks
            if i >= num_tracks:
                break
        # Update offset index for next set of albums
        j += 50
    return
