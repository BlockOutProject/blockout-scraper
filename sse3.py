import requests
import json
import sseclient
import time
import threading

# Étape 1 : Négociation pour obtenir le ConnectionToken
negotiate_url = "https://dataprojectservicesignalr.azurewebsites.net/signalr/negotiate"
negotiate_params = {
    "clientProtocol": "1.5",
    "connectionData": '[{"name":"signalrlivehubfederations"}]',
    "_": str(int(time.time() * 1000))
}
headers = {
    "Origin": "https://lnv-web.dataproject.com",
}

# Effectuer la requête de négociation
response = requests.get(negotiate_url, params=negotiate_params, headers=headers)
negotiate_response = response.json()
connection_token = negotiate_response["ConnectionToken"]
connection_id = negotiate_response["ConnectionId"]

print("ConnectionToken :", connection_token)
print("ConnectionId :", connection_id)

# Fonction pour écouter les événements SSE
def listen_to_events():
    # Étape 2 : Se connecter au flux SSE
    connect_url = "https://dataprojectservicesignalr.azurewebsites.net/signalr/connect"
    connect_params = {
        "transport": "serverSentEvents",
        "clientProtocol": "1.5",
        "connectionToken": connection_token,
        "connectionData": '[{"name":"signalrlivehubfederations"}]',
        "tid": 2
    }

    connect_response = requests.get(connect_url, params=connect_params, headers=headers, stream=True)
    if connect_response.status_code != 200:
        print("Erreur lors de la connexion :", connect_response.status_code)
        return

    client = sseclient.SSEClient(connect_response)
    for event in client.events():
        print("Message reçu :", event.data)
        # Traitez l'événement selon vos besoins

# Démarrer l'écoute des événements dans un thread séparé
listener_thread = threading.Thread(target=listen_to_events)
listener_thread.start()

# Attendre un peu pour s'assurer que la connexion est établie
time.sleep(2)

# Étape 3 : Envoyer la requête 'start'
start_url = "https://dataprojectservicesignalr.azurewebsites.net/signalr/start"
start_params = {
    "transport": "serverSentEvents",
    "clientProtocol": "1.5",
    "connectionToken": connection_token,
    "connectionData": '[{"name":"signalrlivehubfederations"}]',
    "_": str(int(time.time() * 1000))
}

start_response = requests.get(start_url, params=start_params, headers=headers)
start_response_json = start_response.json()
print("Réponse de 'start' :", start_response_json)

# Étape 4 : Envoyer le payload nécessaire
url_send = "https://dataprojectservicesignalr.azurewebsites.net/signalr/send"
params_send = {
    'transport': 'serverSentEvents',
    'clientProtocol': '1.5',
    'connectionToken': connection_token,
    'connectionData': '[{"name":"signalrlivehubfederations"}]'
}

# Exemple de données que vous pourriez devoir envoyer, adaptées en fonction des spécificités du serveur
data = {
    "data": '{"H":"signalrlivehubfederations","M":"getLiveScoreListData_From_ES","A":["8260","lnv"],"I":0}'  # Remplacez "matchIdHere" par l'ID du match si requis
}

send_response = requests.post(url_send, params=params_send, headers=headers, data=data)
print("Réponse de 'send' :", send_response.status_code, send_response.text)

# Garder le programme actif pour écouter les messages
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Arrêt...")