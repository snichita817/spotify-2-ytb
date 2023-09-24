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
# this search also compares the name extracted from spotify with the name of the youtube search
def get_yt_song_id(yt_song_search_result, sp_song_name):
    yt_song_name = None
    for info in yt_song_search_result:
        yt_song_name = get_yt_song_artist_and_name(info)
        
        similarity_ratio = fuzz.ratio(yt_song_name.lower(), sp_song_name.lower())
        
        print(yt_song_name)
        if similarity_ratio > 70:
            return info['videoId']
        
if __name__ == "__main__":      
    token = get_token()
    user_name = input("Enter your spotify ID: ")
    user_id = get_user_id(token, user_name)

    playlists = get_user_playlists(token, user_id)

    playlists_dict = {}

    for _, playlist in enumerate(playlists):    
        songs_name = list()
        playlist_id = playlist["id"]
        playlist_name = playlist["name"]
        
        songs = get_playlist_songs(token, playlist_id)
        
        for _, song in enumerate(songs):
            songs_name.append(song["track"]["artists"][0]["name"] + " " + song["track"]["name"])
        if songs_name != []:
            playlists_dict[playlist_name] = songs_name

    ytmusic = YTMusic("./oauth.json")

    for playlist_name, song_list in playlists_dict.items():
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
                print("Song not found on YouTube:", song)
        print(yt_songs_ids)
        ytmusic.add_playlist_items(playlistId=playlist_id, videoIds=yt_songs_ids)