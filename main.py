"""Stwórz fantazyjną drużynę równą rzeczywistej (Flask/CLI)
 Aplikacja używa bazy danych z tabeli
 https://www.kaggle.com/aayushmishra1512/fifa-2021-complete-player-data
 Uzytkownik wybiera jeden z realnych klubów piłkarskich, aplikacja generuje dla niego
 fikcyjną drużynę przeciwną z którą mecz byłby najbardziej wyrównany
 (każda pozycja jest obsadzona, poszczególne formacje mają jak najbliższe sobie
  sumy overall rating)"""
import os
import pickle
import pandas as pd
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask import render_template

# Flask app
app = Flask(__name__, template_folder='C:\\Users\\Sniezyn\\PycharmProjects\\Druzyna\\'
                                      'venv\\templates')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fifa.db'
db = SQLAlchemy(app)

#Klasa Player
class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    club = db.Column(db.String(80))
    position = db.Column(db.String(10))
    overall_rating = db.Column(db.Integer)


with app.app_context():
    db.create_all()
#metoda do wyboru druzyny
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
            player = Player.query.filter_by(position=position).\
                filter(Player.club == club) \
                .order_by(Player.overall_rating.desc()).first()

            if player:
                team[position] = player.name
                players.remove(
                    player)  # usuwa puste pola i duplikaty zawodnikow
            else:
                team[position] = None

        return render_template('team.html', team=team, club=club)

    else:
        return jsonify({'error': 'Klub Nie Wybrany'})


def save_to_db():
    with app.app_context():
        fifa_df = pd.read_csv('C:/Users/Sniezyn/PycharmProjects/Druzyna/FIFA-21'
                              'Complete.csv', sep=';')
        for index, row in fifa_df.iterrows():
            player_name = row['name']
            club = row['club'].replace('"', '').strip()
            position = row['position']
            overall_rating = row['overall']
            player_positions = position.split('|')
            for             pos in player_positions:
                player = Player(name=player_name, club=club, position=pos,
                                overall_rating=overall_rating)
                db.session.add(player)
                db.session.commit()


save_to_db()

BASE_TEAMS_DIR = 'base_teams/'

if not os.path.exists(BASE_TEAMS_DIR):
    os.mkdir(BASE_TEAMS_DIR)

#zapis druzyny bazowej
def save_base_team(base_team, team_name):
    filename = BASE_TEAMS_DIR + team_name + '.pkl'
    with open(filename, 'wb') as f:
        pickle.dump(base_team, f)


def load_base_team(team_name):
    filename = BASE_TEAMS_DIR + team_name + '.pkl'
    with open(filename, 'rb') as f:
        return pickle.load(f)
def get_base_team(selected_club):
    players = Player.query.filter_by(club=selected_club).all()
    team_positions = ['GK', 'RB', 'CB', 'LB', 'CDM', 'CM', 'RW', 'ST', 'LW']
    base_team = {}

    for position in team_positions:
        player = Player.query.filter_by(position=position, club=selected_club) \
            .order_by(Player.overall_rating.desc()).first()

        if player:
            base_team[position] = player

    return base_team
# get druzyny przeciwnej
def get_opposing_team(base_team):
    base_team_positions = list(base_team.keys())
    opposing_team = {}

    for position in base_team_positions:
        base_player = base_team[position]
        base_rating = base_player.overall_rating

        other_players_position = Player.query.filter(Player.position == position,
                                                     Player.club != base_player.club)
        closest_player = None
        closest_diff = float('inf')

        for player in other_players_position:
            diff = abs(player.overall_rating - base_rating)
            if diff < closest_diff:
                closest_player = player
                closest_diff = diff

        opposing_team[position] = closest_player

    return opposing_team
#symulator meczu
@app.route('/match_simulation', methods=['POST'])
def match_simulation():
    selected_club = request.form.get('selected_club')

    if selected_club:
        base_team = get_base_team(selected_club)
        opposing_team = get_opposing_team(base_team)

        base_team_rating = sum([player.overall_rating for player in base_team.values()])
        opposing_team_rating = sum([player.overall_rating for player in
                                    opposing_team.values()])

        if base_team_rating > opposing_team_rating:
            match_result = "Druzyna Bazowa Wygrywa!!!!"
        elif base_team_rating < opposing_team_rating:
            match_result = "Druzyna Przeciwna Wygrywa!"
        else:
            match_result = "Remis!!!."

        # Dodajemy tu nazwę drużyny przeciwnej
        opposing_club = list(opposing_team.values())[0].club

        return render_template('match_results.html',
                               base_team=base_team,
                               base_team_name=selected_club,  # przekazujemy nazwę drużyny bazowej
                               base_team_rating=base_team_rating,
                               opposing_team=opposing_team,
                               opposing_team_name=opposing_club,  # przekazujemy nazwę drużyny przeciwnej
                               opposing_team_rating=opposing_team_rating,
                               match_result=match_result)
    else:
        return jsonify({'error': 'Klub Nie Wybrany'})


#index poczatkowy
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

