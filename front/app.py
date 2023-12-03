from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit_match_details', methods=['POST'])
def submit_match_details():
    match_type = request.form['matchType']
    rival = request.form['rival']
    match_date = request.form['matchDate']

    # Save match details to use later
    app.match_details = {
        'matchType': match_type,
        'rival': rival,
        'matchDate': match_date
    }

    return render_template('players.html')

@app.route('/submit_players', methods=['POST'])
def submit_players():
    players = request.form['players']
    players_list = [player.strip() for player in players.split(',')]

    # Save player list to use later
    app.players_list = players_list

    return render_template('actions.html', players=players_list)

@app.route('/submit_actions', methods=['POST'])
def submit_actions():
    actions = request.form.getlist('actions[]')

    # Process the received actions here
    # For demonstration, just printing the received actions
    print(actions)

    return jsonify({'message': 'Actions received successfully'})

if __name__ == '__main__':
    app.run(debug=True)
