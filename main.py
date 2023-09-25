import json
import os
import base64
from dotenv import load_dotenv
from requests import post, get
from ytmusicapi import YTMusic
from fuzzywuzzy import fuzz

load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

def get_token():
    auth_string = client_id + ":" + client_secret
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")
    
    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}

    result = post(url, headers=headers, data=data)
    
    json_result = json.loads(result.content)
    token = json_result["access_token"]
    
    return token

def get_auth_header(token):
    return {"Authorization": "Bearer " + token}

def get_user_id(token, user_name):
    url = f"https://api.spotify.com/v1/users/{user_name}"
    headers = get_auth_header(token)
    
    result = get(url, headers=headers)
    json_result = json.loads(result.content)
    
    return json_result["id"]

def get_user_playlists(token, user_id):
    url = f"https://api.spotify.com/v1/users/{user_id}/playlists?limit=50"
    headers = get_auth_header(token)
    
    result = get(url, headers=headers)
    json_result = json.loads(result.content)
    
    return json_result["items"]

def get_playlist_songs(token, playlist_id):
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    headers = get_auth_header(token)
    
    result = get(url, headers=headers)
    json_result = json.loads(result.content)
    
    return json_result["items"]

def get_yt_song_artist_and_name(yt_song_info):
    return yt_song_info['artists'][0]['name'] + " " + yt_song_info['title']

# youtube does not showing sometimes most related search results
# sometimes it prioritizes remixes
# so i used fuzzywuzzy library to compute the similarity ratio
# def get_yt_song_id(yt_song_search_result, sp_song_name):
#     best_similarity = 0
#     best_video_id = None

#     for info in yt_song_search_result:
#         yt_song_name = get_yt_song_artist_and_name(info)
        
#         similarity_ratio = fuzz.ratio(yt_song_name.lower(), sp_song_name.lower())
        
#         print(yt_song_name + " " + str(similarity_ratio))
#         if similarity_ratio >= 55 and similarity_ratio > best_similarity:
#             best_similarity = similarity_ratio
#             best_video_id = info['videoId']

#     return best_video_id
def jaccard_similarity(str1, str2):
    set1 = set(str1.split())
    set2 = set(str2.split())
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    return intersection / union if union != 0 else 0

def get_yt_song_id(yt_song_search_result, sp_song_name):
    best_similarity = 0
    best_video_id = None

    for info in yt_song_search_result:
        yt_song_name = get_yt_song_artist_and_name(info)

        # Calculate Jaccard similarity
        similarity = jaccard_similarity(yt_song_name.lower(), sp_song_name.lower())

      #  print(yt_song_name + " Jaccard similarity: " + str(similarity))

        if similarity >= 0.55 and similarity > best_similarity:
            best_similarity = similarity
            best_video_id = info['videoId']

    return best_video_id
    
def create_spotify_library(token, user_name):
    user_id = get_user_id(token, user_name)
    playlists = get_user_playlists(token, user_id)
    playlists_dict = {}

    print("Creating your Spotify library...")
    for _, playlist in enumerate(playlists):
        songs_name = list()
        playlist_id = playlist["id"]
        playlist_name = playlist["name"]

        songs = get_playlist_songs(token, playlist_id)

        for _, song in enumerate(songs):
            songs_name.append(song["track"]["artists"][0]["name"] + " " + song["track"]["name"])
        if songs_name:
            playlists_dict[playlist_name] = songs_name

    return playlists_dict

def create_youtube_playlists(ytmusic, playlists_dict):
    for playlist_name, song_list in playlists_dict.items():
        print("Creating playlist {}...".format(playlist_name))
        playlist_id = ytmusic.create_playlist(playlist_name, playlist_name)
        yt_songs_ids = []

        for song in song_list:
            print("Searching for: ", song)
            yt_song_search_result = ytmusic.search(song, filter="songs")
            yt_song_id = get_yt_song_id(yt_song_search_result, song)

            if yt_song_id is None and yt_song_search_result:
                yt_song_id = yt_song_search_result[0]['videoId']
            if yt_song_id:
                yt_songs_ids.append(yt_song_id)
                print("Found:", song)
            else:
                print("\033[91mSong not found on YouTube: {}\033[0m".format(song))
        ytmusic.add_playlist_items(playlistId=playlist_id, videoIds=yt_songs_ids)

if __name__ == "__main__":
    token = get_token()
    user_name = input("Enter your Spotify ID: ")
    playlists_dict = create_spotify_library(token, user_name)

    ytmusic = YTMusic("./oauth.json")
    create_youtube_playlists(ytmusic, playlists_dict)
