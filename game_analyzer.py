import csv
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import ticker
from matplotlib.ticker import PercentFormatter
from collections import Counter
from wordcloud import WordCloud

categories_path = 'data_sets/categories.csv'
games_path = 'data_sets/games.csv'
genres_path = 'data_sets/genres.csv'
reviews_path = 'data_sets/reviews.csv'
steamspy_insights_path = 'data_sets/steamspy_insights.csv'
tags_path = 'data_sets/tags.csv'

# Models Folder
output_folder = 'models'
os.makedirs(output_folder, exist_ok=True)

# DATA STRUCTURES
counterIds = 0
priceList = [[] for i in range(27)]
averagePriceList = [[] for i in range(27)]
gamesCount = [[0] for i in range(27)]
gameReleasePerYear = [[0] for i in range(27)]
tag_counter = Counter()
tag_total_counter = 0

# GAME SECTION
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

# Game Release Per Year Model
x = [1998 + i for i in range(27)]
y = gameReleasePerYear
plt.figure(figsize=(8, 6))
plt.bar(x, y)
plt.xlim(1998, 2025)
plt.title('Game Releases Per Year')
plt.xlabel('Year')
plt.ylabel('Game Release Amount')
output_game_releases_per_year = os.path.join(output_folder, 'game_releases_per_year.png')
plt.savefig(output_game_releases_per_year)

# TAG SECTION
# WordCloud Model (for frequency in Tags)
with open(tags_path, mode='r', encoding='utf-8') as file:
    reader = csv.DictReader(file)
    for row in reader:
        tag = row['tag'].lower()
        tag_counter[tag] += 1 
        tag_total_counter += 1

wordcloud = WordCloud(width=3000, height=2200, max_words=tag_total_counter, background_color='black').generate_from_frequencies(tag_counter)
output_tag_frequency = os.path.join(output_folder, 'tag_frequency.png')
wordcloud.to_file(output_tag_frequency)

# REVIEW SECTION
positiveList = []
negativeList = []

def nMaxElements(list1, N):
    final_list = []
 
    for _ in range(N):
        max_pair = max(list1, key=lambda x: x[0])
        list1.remove(max_pair)
        final_list.append(max_pair)
    
    return final_list

def abbreviate_number(x, pos):
    if x >= 1_000_000:
        return f'{x/1_000_000:.1f}M'
    elif x >= 1_000:
        return f'{x/1_000:.0f}k'
    else:
        return f'{x}'

with open(reviews_path, mode='r', encoding='utf-8') as file:
    reader = csv.reader(file)
    next(reader, None)
    
    for row in reader:
        if len(row) != 0 and len(row) > 12:
            app_id = row[0]        # app_id
            description = row[2]   # description
            positive = row[3]      # positive reviews
            negative = row[4]      # negative reviews
            total = row[5]
            
            # Positive
            if description == "Overwhelmingly Positive":
                if positive.isdigit() and total.isdigit():
                    if float(positive) != 0 and float(total) != 0 and float(total) != float(positive):
                        positiveList.append((int(positive), app_id))
            
            # Negative
            if description == "Overwhelmingly Negative":
                if negative.isdigit() and total.isdigit():
                    if float(negative) != 0 and float(total) != 0 and float(total) != float(negative):
                        negativeList.append((float(negative)/float(total), app_id))

# TOP 50 REVIEWED GAMES
top_50 = nMaxElements(positiveList, 50)
app_ids = [app_id for _, app_id in top_50]
y = []
with open(games_path, mode='r', encoding='utf-8') as file:
    reader = csv.reader(file)
    next(reader, None)
    
    for row in reader:
        app_id = row[0]           # app_id
        name = row[1]             # name

        for i in app_ids:
            if (i == app_id):
                y.append(name)
                break

x = [positive for positive, _ in top_50]
plt.figure(figsize=(12, 8))
plt.barh(y, x)
plt.xlabel('Amount of Reviews')
plt.title('Top 50 Reviewed Games')
plt.gca().invert_yaxis()
formatter = ticker.FuncFormatter(abbreviate_number)
plt.gca().xaxis.set_major_formatter(formatter)
plt.tight_layout()
output_top_50_best_reviewed_games = os.path.join(output_folder, 'top_50_best_reviewed_games.png')
plt.savefig(output_top_50_best_reviewed_games)

# TOP 50 WORST REVIEWED GAMES
low_10 = nMaxElements(negativeList, 10)
app_ids = [app_id for _, app_id in low_10]
y = []
with open(games_path, mode='r', encoding='utf-8') as file:
    reader = csv.reader(file)
    next(reader, None)
    
    for row in reader:
        app_id = row[0]           # app_id
        name = row[1]             # name

        for i in app_ids:
            if (i == app_id):
                y.append(name)
                break
            
x = [round(negative*100,2) for negative, _ in low_10]
plt.figure(figsize=(12, 8))
plt.barh(y, x)
plt.title('Top 10 Worst Reviewed Games')
plt.gca().xaxis.set_major_formatter(PercentFormatter())
plt.gca().invert_yaxis()
plt.xlabel('Percentage of Negative Reviews')
plt.tight_layout()
output_top_10_worst_reviewed_games = os.path.join(output_folder, 'top_10_worst_reviewed_games.png')
plt.savefig(output_top_10_worst_reviewed_games)