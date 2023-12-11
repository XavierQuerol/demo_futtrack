from flask import Flask, render_template, request, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, DateField, SubmitField, IntegerField, SelectField, SelectMultipleField, BooleanField
from wtforms.validators import DataRequired
from flask import session

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

# Define forms for different steps

class GlobalVariables:
    part: int = 0

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
    action_type = SelectField('Action Type', choices=[('goal', 'Goal'), ('rival_goal', 'Rival Goal'), ('player_change', 'Player Change')], validators=[DataRequired()])
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

    if match_form.validate_on_submit():
        # Process match details
        # Redirect to the next step
        return redirect(url_for('player_details'))

    return render_template('match_details.html', form=match_form)

@app.route('/player-details', methods=['GET', 'POST'])
def player_details():
    player_form = PlayerForm()

    # Sample list of players (replace this with your actual list of player names)
    player_list = [('1', 'Player 1'), ('2', 'Player 2'), ('3', 'Player 3')]  # Replace with actual player names and IDs
    
    player_form.players.choices = player_list

    if request.method == 'POST':
        player_form.players.data = request.form.getlist('players')  # Assign submitted data to the form field

        if player_form.validate():  # Manually validate the form
            selected_player_ids = player_form.players.data
            selected_players = [name for id, name in player_list if id in selected_player_ids]
            # Process the selected players as needed
            return redirect(url_for('titulars'))

    return render_template('player_details.html', form=player_form)

@app.route('/titulars', methods=['GET', 'POST'])
def titulars():
    player_form = PlayerForm()

    # Sample list of players (replace this with your actual list of player names)
    player_list = [('1', 'Player 1'), ('2', 'Player 2'), ('3', 'Player 3')]  # Replace with actual player names and IDs
    
    player_form.players.choices = player_list

    if request.method == 'POST':
        player_form.players.data = request.form.getlist('players')  # Assign submitted data to the form field

        if player_form.validate():  # Manually validate the form
            selected_player_ids = player_form.players.data
            selected_players = [name for id, name in player_list if id in selected_player_ids]
            # Process the selected players as needed
            return redirect(url_for('actions'))

    return render_template('titulars.html', form=player_form)

@app.route('/actions', methods=['GET', 'POST'])
def actions():
    actions_form = ActionsForm()

    player_list = [('1', 'Player 1'), ('2', 'Player 2'), ('3', 'Player 3')]  # Replace with actual player names and IDs
    
    actions_form.entra.choices = player_list
    actions_form.surt.choices = player_list
    actions_form.scorer.choices = player_list
    actions_form.assistant.choices = player_list

    
    if actions_form.validate_on_submit():
        print("P")
        print(GlobalVariables.part)
        if 'final_part' in request.form and GlobalVariables.part == 0:
            GlobalVariables.part = 1
            return redirect(url_for('titulars'))
        elif 'final_part' in request.form and GlobalVariables.part == 1:
            return redirect(url_for('index'))

    return render_template('actions.html', form=actions_form)

if __name__ == '__main__':
    app.run(debug=True)