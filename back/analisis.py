
from flask import Flask, request

app = Flask(__name__)

@app.route('/receive_data', methods=['POST'])
def receive_data():
    if request.method == 'POST':
        json_data = request.json
        # Convert JSON date format
        date = json_data['Data']  # Assuming the date format is 'YYYY-MM-DD'
        formatted_date = '/'.join(reversed(date.split('-')))  # Convert to 'DD/MM/YYYY'

        # Define the file content
        file_content = f"{json_data['Tipus partit']}\n"
        file_content += f"{json_data['Rival']} \n"
        file_content += f"{formatted_date}\n"
        file_content += "Local\n\n"

        # Function to format actions
        def format_actions(actions):
            formatted_actions = ""
            for action in actions:
                formatted_actions += f"{action['minute']}:{action['second']} {action['action_type']} "
                participants = action.get('Participants', [])
                if isinstance(participants, list):
                    formatted_actions += " ".join(participants)
                else:
                    formatted_actions += participants
                formatted_actions += "\n"
            return formatted_actions

        # Format and add actions for the first part
        file_content += f"Titulars:{' '.join(json_data['Titulats_1aPart'])}\n"
        file_content += format_actions(json_data['Accions_1aPart'])
        file_content += "\n"

        # Format and add actions for the second part
        file_content += f"Titulars:{' '.join(json_data['Titulats_2aPart'])}\n"
        file_content += format_actions(json_data['Accions_2aPart'])

        # Save the formatted text to a .txt file
        with open('formatted_data.txt', 'w') as file:
            file.write(file_content)
        print("Received Data:", json_data)
        return "Data received successfully"
    
@app.route('/send_data', methods=['POST'])
def send_data():
    if request.method == 'POST':
        json_data = request.json

        
        # Process the received data as needed
        print("Received Data:", json_data)
        return "Data received successfully"

if __name__ == '__main__':
    app.run(debug=True, port=5000)

