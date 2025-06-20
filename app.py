from flask import Flask, request, jsonify, render_template
import requests
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    data = request.get_json()
    date_input = data['date']
    from_station = data['from'].upper()
    to_station = data['to'].upper()
    departure_time = data['departureTime']
    max_connections = int(data['maxConnections'])
    any_connections = data['anyConnections']
    any_time = data['anyTime']
    nearby_arrival = data['nearbyArrival']

    try:
        date_obj = datetime.strptime(date_input, '%d/%m/%Y')
        date_str = date_obj.strftime('%Y-%m-%d')
    except ValueError:
        return jsonify({'error': 'Format de date invalide. Utilisez jj/mm/aaaa.'})

    api_url = f"https://data.sncf.com/api/records/1.0/search/?dataset=tgvmax&q=&rows=1000&refine.date={date_str}"
    response = requests.get(api_url)
    if response.status_code != 200:
        return jsonify({'error': 'Erreur lors de la récupération des données.'})

    records = response.json().get('records', [])
    trains = [record['fields'] for record in records]

    filtered_trains = []
    for train in trains:
        if train['origine'] == from_station and train['destination'] == to_station:
            if not any_time and 'departure_time' in train:
                try:
                    train_time = datetime.strptime(train['departure_time'], '%H:%M')
                    user_time = datetime.strptime(departure_time, '%H:%M')
                    if train_time < user_time:
                        continue
                except:
                    continue
            filtered_trains.append(train)

    itineraries = []
    for train in filtered_trains:
        itineraries.append([train])

    if not itineraries:
        return jsonify({'error': 'Aucun itinéraire trouvé avec les critères spécifiés.'})

    return jsonify({'itineraries': itineraries})

if __name__ == '__main__':
    app.run(debug=True)
