from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
import pandas as pd
import matplotlib.pyplot as plt
import re
import mysql.connector

# Set up Client Credentials
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id="27023e58e710449ca94c9d14901591a4",
    client_secret="12e3f9976e1d4d479f8a32f9fbf77437"
))


# MYSQL database connection
db_config={
    'host':'localhost',
    'user':'root',
    'password':'password',
    'database':'spotify_db'
}

# Connect database
connection = mysql.connector.connect(**db_config)
cursor = connection.cursor()

# Playlist URL
track_url = "https://open.spotify.com/track/6P8dmbcOEz7XPFQjd1V6d5"

# Extract playlist ID from URL
track_id = re.search(r'track/([a-zA-Z0-9]+)', track_url).group(1)

# Get track tracks
track = sp.track(track_id)

# Print track names
# print(track)
track_data={
    'Track Name' : track['name'],
    'Artist':track['artists'][0]['name'],
    'Album': track['album']['name'],
    'Popularity' : track ['popularity'],
    'Duration (minutes)':track['duration_ms']/60000
}

# INSERT data into MYSQL


insert_query = """
    INSERT INTO spotify_tracks (track_name, artist, album, popularity, duration_minutes)
    VALUES (%s, %s, %s, %s, %s)
"""

# cursor execute
cursor.execute(insert_query,(
    track_data['Track Name'],
    track_data['Artist'],
    track_data['Album'],
    track_data['Popularity'], 
    track_data['Duration (minutes)'],
))
connection.commit()

print(f"Track '{ track_data['Track Name']}' by {track_data['Artist']} inserted into the database")

# Close the Connection
cursor.close()
connection.close()


# display metadata

print(f"\nTrack Name : {track_data['Track Name']}")
print(f"Artist : {track_data['Artist']}")
print(f"Album : {track_data['Album']}")
print(f"Duration : {track_data['Duration (minutes)']:.2f} minutes")

# Convert metadata to DataFrame

df=pd.DataFrame([track_data])
print('\n Trak Data as DataFrame')
print(df)

# print metadata to CSV
df.to_csv('spotify_track_data.csv',index=False)

# Visualization track data
features = ['Popularity', 'Duration (minutes)']
values = [track_data['Popularity'],track_data['Duration (minutes)']]

plt.figure(figsize=(8,5))
# plt.bar(features,values,color='skyblue',edgecolor='black')
plt.pie(values, labels=features, colors=['skyblue', 'lightgreen'], autopct='%1.1f%%', startangle=140)
plt.title (f"Track Metadata for '{track_data['Track Name']}'")
plt.ylabel('Value')
plt.show()
