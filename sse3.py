from signalr import Connection
import requests
from urllib.parse import quote

# URL du service SignalR
url = "https://dataprojectservicesignalr.azurewebsites.net/signalr"

# Étape 1 : Effectuer la négociation pour obtenir le ConnectionToken
def negotiate():
    negotiate_url = f"{url}/negotiate"
    params = {
        'clientProtocol': '1.5',
        'connectionData': '[{"name":"signalrlivehubfederations"}]',
        '_': 'timestamp'
    }
    headers = {
        "Accept": "application/json",
        "Origin": "https://lnv-web.dataproject.com",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
        "Cookie": "ARRAffinitySameSite=your_cookie_value_here",
        "Authorization": "Bearer your_token_here"  # Remplacez par le token si nécessaire
    }
    response = requests.get(negotiate_url, params=params, headers=headers)
    response.raise_for_status()  # Vérifie que la réponse est OK
    return response.json()

# Étape 2 : Obtenir et encoder le token de connexion
negotiation_data = negotiate()
raw_token = negotiation_data['ConnectionToken']
encoded_token = quote(raw_token, safe="")

# Créer une session pour la connexion persistante
session = requests.Session()
session.headers.update({
    "Accept": "application/json",
    "Origin": "https://lnv-web.dataproject.com",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    "Cookie": "ARRAffinitySameSite=your_cookie_value_here",
    "Authorization": "Bearer your_token_here"
})

# Créer la connexion avec le token encodé
connection_url = f"{url}/connect?transport=serverSentEvents&clientProtocol=1.5&connectionToken={encoded_token}&connectionData=[{{\"name\":\"signalrlivehubfederations\"}}]&tid=3"
connection = Connection(connection_url, session)

# Enregistrer le hub
hub = connection.register_hub('signalrlivehubfederations')

# Callback générique pour capturer tous les messages
def on_message_received(message):
    print("Message reçu :", message)

# Définir les callbacks spécifiques pour les événements
def on_update_match_set_data_es(data):
    print("Données ES reçues :", data)

def on_update_match_set_data_dv(data):
    print("Données DV reçues :", data)

# Associer les événements à leurs callbacks
hub.client.on("updateMatchSetData_ES", on_update_match_set_data_es)
hub.client.on("updateMatchSetData_DV", on_update_match_set_data_dv)

# Associer le callback générique pour déboguer tous les messages reçus
connection.received += on_message_received

# Démarrer la connexion
connection.start()

# Envoyer la commande spécifique `getLiveScoreListData_From_ES`
hub.server.invoke("getLiveScoreListData_From_ES", "8094", "lnv")

# Garder la connexion ouverte pour recevoir les événements
try:
    while True:
        pass
except KeyboardInterrupt:
    connection.close()