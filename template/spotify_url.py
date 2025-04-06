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

# Playlist URL
# track_url = "https://open.spotify.com/track/6P8dmbcOEz7XPFQjd1V6d5"

# Connect database
connection = mysql.connector.connect(**db_config)
cursor = connection.cursor()

# Readt Track URL from file
file_path = 'track_urls.txt'
with open(file_path,'r') as file:
    track_urls = file.readlines()

# List to collect all track data
all_track_data = []

# Processing Each URL

for track_url in track_urls:
    track_url = track_url.strip()   # remove wite space
    
    try:

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

        # Add to list
        all_track_data.append(track_data)

        print(f"Track '{ track_data['Track Name']}' by {track_data['Artist']} inserted into the database")
    
    except Exception as e :
        print (f"Error Processing URL:{track_url}.Error:{e}")

        # Close the Connection
        cursor.close()
        connection.close()

    print("All track has been processed and intrest into database")

 # Create DataFrame from all tracks
df = pd.DataFrame(all_track_data)
print('\n📊 All Track Data as DataFrame:')
print(df)

# Export to CSV
df.to_csv('spotify_all_track_data.csv', index=False)
print("\n✅ All track data saved to 'spotify_track_data.csv'")

# 🎯 Visualization: Pie chart of all tracks' popularity
plt.figure(figsize=(10, 8))

# Labels = Track Names, Values = Popularity
labels = df['Track Name']
sizes = df['Popularity']

# Optional: Limit to top 10 most popular tracks for better readability
# df_sorted = df.sort_values(by='Popularity', ascending=False).head(10)
# labels = df_sorted['Track Name']
# sizes = df_sorted['Popularity']

plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140, colors=plt.cm.tab20.colors)
plt.title("Popularity Distribution of All Tracks")
plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
plt.tight_layout()
plt.show()
