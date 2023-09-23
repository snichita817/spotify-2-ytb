# spotify-2-ytb
This small Python script that facilitates the synchronization of Spotify playlists with YouTube Music playlists. The script uses the Spotify API to retrieve user playlists and songs, and the YouTube Music API to search for corresponding songs and create playlists with matching names and songs on YouTube Music.

# Tutorial: How to Use the Script and Dependencies
1. Python Environment Setup:
   * Ensure you have Python 3.x installed on your system. If not, download and install it from the official Python website.
2. Installing Required Packages:
   * Run the following command to install the required Python packages using pip:  
     ```pip install ytmusicapi requests python-dotenv```
3. Setting Up Environment Variables:
   * Create a `.env` file in the same directory as the script.
   * Define the following environment variables in the `.env` file:
     ```
     CLIENT_ID=your_spotify_client_id
     CLIENT_SECRET=your_spotify_client_secret
     ```
4. OAuth Configuration for YouTube Music:
   * Obtain the necessary OAuth credentials for YouTube Music API running ```ytmusicapi oauth``` command in the terminal. For more guidance refer to the [YTMusicAPI setup page.](https://ytmusicapi.readthedocs.io/en/stable/setup/index.html)

5. Runn the script.
