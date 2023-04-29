"""Stwórz fantazyjną drużynę równą rzeczywistej (Flask/CLI)
 Aplikacja używa bazy danych z tabeli
 https://www.kaggle.com/aayushmishra1512/fifa-2021-complete-player-data
 Uzytkownik wybiera jeden z realnych klubów piłkarskich, aplikacja generuje dla niego
 fikcyjną drużynę przeciwną z którą mecz byłby najbardziej wyrównany
 (każda pozycja jest obsadzona, poszczególne formacje mają jak najbliższe sobie
  sumy overall rating)"""

import os
import pandas as pd
import pickle
import random
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fifa.db'
db = SQLAlchemy(app)

class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    club = db.Column(db.String(80))

with app.app_context():
    db.create_all()

@app.route('/teams', methods=['GET'])


def get_teams():
    club = request.args.get('club')
    if club:
        club = club.strip()
        players = Player.query.filter_by(club=club).all()
        team_size = len(players)
        if team_size == 0:
            return jsonify({'error': 'Brak Zawodnikow Wybranego Klubu'})
        team_rating = sum([player.overall_rating for player in players])
        avg_rating = team_rating // team_size
        positions = ['GK', 'CB', 'RB', 'LB', 'CDM', 'CM', 'CAM', 'RW', 'LW', 'ST']
        team = {}
        for position in positions:
            team[position] = Player.query.filter_by\
                (position=position).filter(Player.overall_rating >=
                                           avg_rating).first().name
        return jsonify(team)
    else:
        return jsonify({'error': 'Klub Nie Wybrany'})
if __name__ == '__main__':
        app.run(debug=True)

# Drużyny Bazowe
BASE_TEAMS_DIR = 'base_teams/'

# Utwórz DIR jesli nie istnieje
if not os.path.exists(BASE_TEAMS_DIR):
    os.mkdir(BASE_TEAMS_DIR)

# Funkcja zapisu bazowej druzyny
def save_base_team(base_team, team_name):
    filename = BASE_TEAMS_DIR + team_name + '.pkl'
    with open(filename, 'wb') as f:
        pickle.dump(base_team, f)

# Funkcja do pobierania bazowej druzyny
def load_base_team(team_name):
    filename = BASE_TEAMS_DIR + team_name + '.pkl'
    with open(filename, 'rb') as f:
        return pickle.load(f)
# plik CSV
fifa_df = pd.read_csv('C:/Users/Sniezyn/PycharmProjects/Druzyna/FIFA-21 Complete.csv',
                      sep=';')

#Kluby = Bazowe drużyny
clubs = ['Real Madrid', 'FC Barcelona', 'Manchester United',
         'Liverpool', 'Juventus', 'Paris Saint-Germain']
# wybór klubu
selected_club = input("Wybierz Klub Pilkarski z podanej Listy: "
                      + ", ".join(clubs) + "\n")

while selected_club not in clubs:
    print("Blad. Wybierz Klub Pilkraski z Listy.")
    selected_club = input("Wybierz Klub Pilkarski z podanej Listy: "
                          + ", ".join(clubs) + "\n")

print("Wybrales!!:", selected_club, "!!!!!")

players = fifa_df[fifa_df['club'] == selected_club]
# Statystyki
overall_ratings = {}
for index, player in players.iterrows():
    overall_rating = player[['shooting', 'passing', 'dribbling', 'defending',
                             'physic']].sum()
    overall_ratings[player['name']] = overall_rating
sorted_ratings = dict(sorted(overall_ratings.items(), key=lambda x: x[1], reverse=True))

base_team = list(sorted_ratings)[:11]
if base_team:
    base_rating = [player['overall_rating'] for player in base_team if player
    ['overall_rating'] is not None]
else:
    base_rating = []

total_rating = sum(sorted_ratings[player] for player in base_team)

print("Druzyna Bazowa", selected_club, "to:", ", ".join(base_team))
print("Statystyki dla Druzyny Bazowej:", total_rating)
# zachowaj bazowa druzyne
team_name = input("Wprowadz Nazwe Druzyny Bazowej by ja Zapisac: ")
save_base_team(base_team, team_name)

# pobierz bazowa druzyny
team_name = input("Wprowadz Nazwe Druzyny Bazowej by ja Pobrac: ")
base_team = load_base_team(team_name)

other_players = fifa_df[~fifa_df['name'].isin(base_team)]
base_team_positions = ['GK', 'RB', 'CB1', 'CB2', 'LB', 'CDM', 'CM1', 'CM2', 'RW',
                       'ST', 'LW']
#druzyna przeciwna
opposing_team = {}
for position in base_team_positions:
    # Find the overall rating for the current position in the base team
    base_rating = [player['overall_rating'] for player in base_team if
                   player['team_position'] == position][0]
    # Filter the other players by position
    other_players_position = other_players[other_players['team_position'] == position]
    # Find the player with the closest overall rating to the current position's overall rating
    closest_player = other_players_position.iloc[(other_players_position['overall_rating']
                                                  - base_rating).abs().argsort()
    [:1]].iloc[0]
    # Add the player to the opposing team dictionary
    opposing_team[position] = closest_player
opposing_team_rating = sum([player['overall_rating'] for player in
                            opposing_team.values()])
print("Druzyna Bazowa:")
for position, player in zip(base_team_positions, base_team):
    print(position + ": " + player)
print("Statystyki: " + str(total_rating))

print("\nDrużyna Przeciwna:")
for position, player in opposing_team.items():
    print(position + ": " + player['name'])
print("Statystyki: " + str(opposing_team_rating))

print("Druzyna Bazowa", selected_club, "to:", ", ".join(base_team))
print("Statystyki dla Druzyny Bazowej:", total_rating)
print("\nDrużyna Przeciwna:")
for position, player in opposing_team.items():
    print(position + ": " + player['name'])
print("Statystyki: " + str(opposing_team_rating))
print("\nSymulacja Meczu...")
if total_rating > opposing_team_rating:
    print("Druzyna Bazowa Wygrywa!!!!")
elif total_rating < opposing_team_rating:
    print("Druzyna Przeciwna Wygrywa!")
else:
    print("Remis!!!.")
if __name__ == '__main__':
    app.run(debug=True)
'''
# opocionalnie gernerator druzyn na podstawie statystyk
def generate_team(play_style, num_players):
    if play_style == 'possession':
        # Select players with high passing, dribbling, and stamina
        selected_players = fifa_df.nlargest(num_players,
                                            ['passing', 'dribbling', 'stamina'])
    elif play_style == 'counter-attack':
        # Select players with high pace, dribbling, and vision
        selected_players = fifa_df.nlargest(num_players, ['pace', 'dribbling', 'vision'])
    else:
        print("Invalid play style selected.")
        return None

    # Sort the selected players by their overall rating
    sorted_players = selected_players.sort_values('overall_rating', ascending=False)

    # Create a list of the top 11 players based on their overall rating
    top_players = list(sorted_players.head(11)['name'])

    return top_players
play_style = input("Select a play style: possession or counter-attack\n")
num_players = 100

team = generate_team(play_style, num_players)
if team:
    print("The generated team for", play_style, "is:", ", ".join(team))


if random.random() < 0.2:
    print("But wait! The referee has awarded a penalty kick to the opposing team!")
    print("They have a chance to turn the match around...")
    if random.random() < 0.5:
        print("The penalty kick is missed! The base team retains their lead.")
    else:
        print("The penalty kick is scored! The opposing team equalizes!")
'''

