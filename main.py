import time
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from datetime import datetime
import numpy as np
import json
from spotify_player import play_song
import requests
from auth import auth_dict
import pandas as pd
print("RUN ANALYSIS")
spotify = pd.read_csv("SpotifyFeatures.csv")

def set_parameters(time_of_day, busyness, std_div):
    params = {}

    # Setting parameters for time_of_day...
    if (hour < 6):
         params['mode'] = 'Minor'
         params['tempo'] = (0, 90)
         params['loudness'] = (-33, -10)
    elif (time_of_day < 15):
         params['mode'] = 'Major'
         params['tempo'] = (90, 160)
         params['loudness'] = (-13, -3)
    elif (time_of_day < 21):
         params['mode'] = 'Major'
         params['tempo'] = (130, 230)
         params['loudness'] = (-10, 0)
    else:
         params['mode'] = 'Minor'
         params['tempo'] = (50, 150)
         params['loudness'] = (-16, -12)

    # Setting parameters for busyness...
    if (busyness < 200):
        params['danceability'] = (0.75, 1)
        params['energy'] = (0.8, 1)
    elif (busyness < 1500):
        params['danceability'] = (0.45, 0.75)
        params['energy'] = (0.6, 0.8)
    elif (busyness < 3000):
        params['danceability'] = (0.25, 0.45)
        params['energy'] = (0.4, 0.6)
    else:
        params['danceability'] = (0, 0.3)
        params['energy'] = (0, 0.84)

    # Setting parameters for std_div...
    if (std_div < 5):
        params['valence'] = (0.8, 1)
    elif (std_div < 10):
        params['valence'] = (0.6, 0.8)
    elif (std_div < 15):
        params['valence'] = (0.4, 0.6)
    elif (std_div < 20):
        params['valence'] = (0.2, 0.4)
    else:
        params['valence'] = (0, 0.2)

    return params
    
# Initialize client_credentials_manager and then refresh when needed in isExplicit
client_id = auth_dict["client_id"]
client_secret = auth_dict["client_secret"]
client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)

def isExplicit(track_id, client_credentials_manager):
    # generates new access token if needed, otherwise use old one
    client_credentials_manager.get_access_token()
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    isExplicit = bool (sp.track(track_id)["explicit"])
    return isExplicit


while (True):
    try:
        hour = datetime.now().hour
        print("hour =", hour)

        occuspace_api = auth_dict["occuspace_api"]
        raw_occuspace = requests.get(occuspace_api)
        occuspace_dict = json.loads(raw_occuspace.text)
        print(occuspace_dict.keys())
        sublocations = occuspace_dict["sublocations"]

        # Group different floors to different stress weights
        loud = ["1E", "1W", "2E", "2W"]
        medium = ["4", "5", "6", "7"]
        silent = ["8"]
        stress_gauge = 0
        # Weight different floors with different stress levels depending on the ideal quietness
        for floor in sublocations:
            if floor["abbreviation"] in loud:
                stress_gauge += floor["busyness"] * 1
            elif floor["abbreviation"] in medium:
                stress_gauge += floor["busyness"] * 1.5
            elif floor["abbreviation"] in silent:
                stress_gauge += floor["busyness"] * 2
        print("stress_gauge", stress_gauge)
        busyness_floors = []

        # Calculate standard deviation of all floors' busynesses
        for floor in sublocations:
            busyness_floors.append(floor["busyness"])
        print("mean", np.mean(busyness_floors))
        floors_stdev = np.std(busyness_floors)
        print("stdev", floors_stdev)

        current_params = set_parameters(hour, stress_gauge, floors_stdev)

        # Filter through spotify table and find the appropriate song to play
        # pandas conversion
        print(current_params["mode"])
        no_comedy = spotify[spotify["genre"] != "Comedy"]
        matching_mode = no_comedy[spotify["mode"] == current_params["mode"]]
        matching_tempo = matching_mode[spotify.tempo.between(current_params["tempo"][0], current_params["tempo"][1])]
        matching_loudness = matching_tempo[matching_tempo.loudness.between(current_params["loudness"][0], current_params["loudness"][1])]
        matching_danceability = matching_loudness[matching_loudness.danceability.between(current_params["danceability"][0], current_params["danceability"][1])]
        matching_valence = matching_danceability[matching_danceability.valence.between(current_params["valence"][0], current_params["valence"][1])]
        random_song = matching_valence.sample(1)
        random_song
        while isExplicit(random_song.track_id.iloc[0], client_credentials_manager):
            random_song = matching_valence.sample(1)
        track_id = random_song.track_id.iloc[0]
        track_duration = random_song.duration_ms.iloc[0]/1000
        print("tempo", random_song["tempo"].iloc[0])
        print("mode", random_song["mode"].iloc[0])
        print("danceability", random_song["danceability"].iloc[0])
        print("valence", random_song["valence"].iloc[0])
        # open web browser and play song
        print("PLAY SONG")
        
        play_song(track_id, track_duration)

        ## Pause for random amount of seconds
        pause_range = np.arange(180, 420)
        pause_time = np.random.choice(pause_range)
        print("pausing for {} minutes".format(pause_time / 60))
        time.sleep(pause_time)
        
    except:
        print("Exception")
        pass