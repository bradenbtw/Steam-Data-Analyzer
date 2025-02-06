import csv
import os
import numpy as np
import plotly
from collections import Counter
from wordcloud import WordCloud

categories_path = 'data_sets/categories.csv'
descriptions_path = 'data_sets/descriptions.csv'
games_path = 'data_sets/games.csv'
genres_path = 'data_sets/genres.csv'
promotional_path = 'data_sets/promotional.csv'
reviews_path = 'data_sets/reviews.csv'
steamspy_insights_path = 'data_sets/steamspy_insights.csv'
tags_path = 'data_sets/tags.csv'

# Models Folder
output_folder = 'models'
os.makedirs(output_folder, exist_ok=True)

# Counting Entries
counterIds = 0

# Prices
priceList = [ [] for i in range(27) ]
averagePriceList = [ [] for i in range(27) ]

# Game Count
gamesCount = [ [0] for i in range(27) ]
gameReleasePerYear = [ [0] for i in range(27) ]

# Word Frequency
tag_counter = Counter()
tag_total_counter = 0

with open(games_path, mode='r', encoding='utf-8') as file:
    reader = csv.reader(file)
    next(reader, None)

    for row in reader:
        app_id = row[0]           # app_id
        name = row[1]             # name
        release_date = row[2]     # release_date
        is_free = row[3]          # is_free
        price_overview = row[4]   # price_overview
        languages = row[5]        # languages
        game_type = row[6]        # type
        counterIds += 1
            
        price_string = "" 
        if(isinstance(price_overview, str) and isinstance(release_date, str) and len(release_date) > 2):
            for char in price_overview:
                if char.isdigit():
                    price_string += char
            if(price_string != ""): 
                price = (float(price_string))/100
                if price < 113: # Excluding Prices over $113
                    releaseYear = ""
                    for char in release_date:
                        if(char == '-'):
                            break
                        releaseYear += str(char)
                    if releaseYear.isdigit():
                        priceList[int(releaseYear) - 1998].append(price)
                
                # Game Counter
            releaseYear = ""
            for char in release_date:
                if(char == '-'):
                    break
                releaseYear += str(char)
            if releaseYear.isdigit():
                gamesCount[int(releaseYear) - 1998].append(1)

with open(tags_path, mode='r', encoding='utf-8') as file:
    reader = csv.DictReader(file)
    for row in reader:
        tag = row['tag'].lower()
        tag_counter[tag] += 1 
        tag_total_counter += 1

# Iterating through Lists
for i in range(27):
    # Average Price over 76092 games per year
    priceTotal = 0
    if len(priceList[i]) > 0:
        for j in priceList[i]:
            priceTotal += j
        averagePriceList[i] = round((priceTotal / len(priceList[i])), 2)
    else:
        averagePriceList[i] = 0.00
    
    # Game Per Year Total Calculation
    gameTotal = 0
    if len(gamesCount[i]) > 0:
        for j in gamesCount[i]:
            gameTotal += 1
        gameReleasePerYear[i] = gameTotal
    else:
        gameReleasePerYear[i] = 0
        
# WordCloud Model (for frequency in Tags)
wordcloud = WordCloud(width=3000, height=2200, max_words=tag_total_counter, background_color='black').generate_from_frequencies(tag_counter)
output_tag_frequency = os.path.join(output_folder, 'tag_frequency.png')
wordcloud.to_file(output_tag_frequency)