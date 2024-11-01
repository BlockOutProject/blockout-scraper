import requests

# Étape 1 : Négociation pour obtenir le ConnectionToken
url_negotiate = "https://dataprojectservicesignalr.azurewebsites.net/signalr/negotiate"
params_negotiate = {
    'clientProtocol': '1.5',
    'connectionData': '[{"name":"signalrlivehubfederations"}]',
    '_': '1729715787231'
}
headers = {
    'origin': 'https://lnv-web.dataproject.com',
}

response_negotiate = requests.get(url_negotiate, headers=headers, params=params_negotiate)
negotiation_data = response_negotiate.json()
connection_token = negotiation_data['ConnectionToken']

# Étape 2 : Établir la connexion via SSE
url_connect = "https://dataprojectservicesignalr.azurewebsites.net/signalr/connect"
params_connect = {
    'transport': 'serverSentEvents',
    'clientProtocol': '1.5',
    'connectionToken': connection_token,
    'connectionData': '[{"name":"signalrlivehubfederations"}]',
    'tid': '10'  # Ce paramètre tid est généralement aléatoire, tu peux ajuster si nécessaire
}

# Cette requête maintient la connexion ouverte
connect_response = requests.get(url_connect, headers=headers, params=params_connect, stream=True)

# Si la connexion est réussie
if connect_response.status_code == 200:
    print("Connexion SSE établie. En attente des événements...")
    
    # Lecture des événements en temps réel
    for line in connect_response.iter_lines():
        if line:
            print(f"Événement reçu : {line.decode('utf-8')}")
else:
    print(f"Erreur lors de la connexion SSE : {connect_response.status_code} - {connect_response.text}")

# Étape 3 : Envoi d'une requête "send" pour demander des informations spécifiques
url_send = "https://dataprojectservicesignalr.azurewebsites.net/signalr/send"
params_send = {
    'transport': 'serverSentEvents',
    'clientProtocol': '1.5',
    'connectionToken': connection_token,
    'connectionData': '[{"name":"signalrlivehubfederations"}]'
}
form_data = {
    "data": '{"H":"signalrlivehubfederations","M":"getLiveScoreListData_From_ES","A":["8087;8085;8086","lnv"],"I":0}'
}

send_response = requests.post(url_send, headers=headers, params=params_send, data=form_data)

if send_response.status_code == 200:
    print("Requête `send` envoyée avec succès.")
else:
    print(f"Erreur lors de l'envoi de la requête `send` : {send_response.status_code} - {send_response.text}")