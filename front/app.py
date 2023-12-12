from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_wtf import FlaskForm
from wtforms import StringField, DateField, SubmitField, IntegerField, SelectField, SelectMultipleField, BooleanField
from wtforms.validators import DataRequired
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

# Define forms for different steps

class GlobalVariables:
    part: int = 0
    jugadors: list = [('1', 'Corts'), ('2', 'Coco'), ('3', 'Kule'), ('4', 'Kuman'), ('5', 'Arnau'), ('6', 'Aleix'), ('7', 'Piu'), ('8', 'Pit')]
    jugadors_selected: list = None
    jugadors_pista: list = None
    jugadors_banqueta: list = None
    dades_registre: dict = {}

class MatchDetailsForm(FlaskForm):
    match_type = SelectField('Match Type', validators=[DataRequired()])
    rival = StringField('Rival', validators=[DataRequired()])
    match_date = DateField('Match Date', validators=[DataRequired()])
    local_match = BooleanField('Local Match')
    next_step = SubmitField('Next')

class PlayerForm(FlaskForm):
    players = SelectMultipleField('Players', choices=[], coerce=int)
    next_step = SubmitField('Next')


class ActionsForm(FlaskForm):
    action_type = SelectField('Action Type', choices=[('goal', 'Goal'), ('rival_goal', 'Rival Goal'), ('canvi', 'Canvi')], validators=[DataRequired()])
    minute = IntegerField('Minute', validators=[DataRequired()]),
    second = IntegerField('Second', validators=[DataRequired()])
    scorer = SelectMultipleField('Marca', choices=[], coerce=int)
    assistant = SelectMultipleField('Assisteix', choices=[], coerce=int)
    entra = SelectMultipleField('Entra', choices=[], coerce=int)
    surt = SelectMultipleField('Surt', choices=[], coerce=int)
    submit_action = SubmitField('Registra acció')
    final_part = SubmitField('Final part')

@app.route('/', methods=['GET', 'POST'])
def index():
    match_form = MatchDetailsForm()

    match_form.match_type.choices = [('1', 'Lliga'), ('2', 'Copa'), ('3', 'Amistós')]
    if request.method == 'POST':
        print(request.form)
        if match_form.validate_on_submit():
            GlobalVariables.dades_registre = {"Tipus partit": request.form['match_type'],
                                            "Rival": request.form['rival'],
                                            "Data": request.form['match_date'],
                                            "Local": request.form['local_match'],
                                            "Partit": {}
            }
        return redirect(url_for('player_details'))

    return render_template('match_details.html', form=match_form)

@app.route('/player-details', methods=['GET', 'POST'])
def player_details():
    player_form = PlayerForm()

    # Sample list of players (replace this with your actual list of player names)
    player_list = GlobalVariables.jugadors  # Replace with actual player names and IDs
    
    player_form.players.choices = player_list

    if request.method == 'POST':
        print(request.form.getlist('players'))
        player_form.players.data = request.form.getlist('players')  # Assign submitted data to the form field
        print(request.form)
        if player_form.validate():  # Manually validate the form
            selected_player_ids = player_form.players.data
            GlobalVariables.jugadors_selected = [(id, name) for id, name in player_list if id in selected_player_ids]
            # Process the selected players as needed
            return redirect(url_for('titulars'))

    return render_template('player_details.html', form=player_form)

@app.route('/titulars', methods=['GET', 'POST'])
def titulars():
    player_form = PlayerForm()

    # Sample list of players (replace this with your actual list of player names)
    player_list = GlobalVariables.jugadors_selected  # Replace with actual player names and IDs
    
    player_form.players.choices = player_list

    if request.method == 'POST':
        player_form.players.data = request.form.getlist('players')  # Assign submitted data to the form field

        if player_form.validate():  # Manually validate the form
            selected_player_ids = player_form.players.data
            GlobalVariables.jugadors_pista = [(id, name) for id, name in player_list if id in selected_player_ids]
            GlobalVariables.jugadors_banqueta = [(id, name) for id, name in player_list if id not in selected_player_ids]

            if GlobalVariables.part == 0:
                GlobalVariables.dades_registre["Titulats_1aPart"] = [name for id, name in player_list if id in selected_player_ids]
                GlobalVariables.dades_registre["Accions_1aPart"] = []
            elif GlobalVariables.part == 1:
                GlobalVariables.dades_registre["Titulats_2aPart"] = [name for id, name in player_list if id in selected_player_ids]
                GlobalVariables.dades_registre["Accions_2aPart"] = []
            # Process the selected players as needed
            return redirect(url_for('actions'))

    return render_template('titulars.html', form=player_form)

@app.route('/actions', methods=['GET', 'POST'])
def actions():

    player_list = GlobalVariables.jugadors_selected
    actions_form = ActionsForm()

    actions_form.entra.choices = GlobalVariables.jugadors_banqueta
    actions_form.surt.choices = GlobalVariables.jugadors_pista
    actions_form.scorer.choices = GlobalVariables.jugadors_pista
    actions_form.assistant.choices = GlobalVariables.jugadors_pista

    if request.method == 'POST':
        print(GlobalVariables.part)
        if 'final_part' in request.form and GlobalVariables.part == 0:
            GlobalVariables.part = 1
            return redirect(url_for('titulars'))
        elif 'final_part' in request.form and GlobalVariables.part == 1:
            other_api_url = 'http://127.0.0.1:5000/receive_data'  # Replace this with the actual endpoint

            # Send data to the other API
            response = requests.post(other_api_url, json=GlobalVariables.dades_registre)
            print(GlobalVariables.dades_registre)

            return redirect(url_for('index'))
            
        print(request.form)
            
        if request.form['action_type'] == 'canvi':
            entra = request.form['entra']
            surt = request.form['surt']
            GlobalVariables.jugadors_pista = [(id, name) for id, name in GlobalVariables.jugadors_pista if id != surt] + [(id, name) for id, name in GlobalVariables.jugadors_selected if id == entra]
            GlobalVariables.jugadors_banqueta = [(id, name) for id, name in GlobalVariables.jugadors_banqueta if id != entra] + [(id, name) for id, name in GlobalVariables.jugadors_selected if id == surt]
            
        data_dict = dict(request.form)
        data_dict_without_first = dict(list(data_dict.items())[1:])
        if GlobalVariables.part == 0:
            print(GlobalVariables.dades_registre)
            GlobalVariables.dades_registre["Accions_1aPart"].append(data_dict_without_first)
        elif GlobalVariables.part == 1:
            GlobalVariables.dades_registre["Accions_2aPart"].append(data_dict_without_first)
        

    return render_template('actions.html', form=actions_form)

if __name__ == '__main__':
    app.run(debug=True, port=5001)