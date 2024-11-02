import requests
import time

# Initialiser la session
session = requests.Session()

# Étape 1 : Négocier pour obtenir le ConnectionToken
url_negotiate = "https://dataprojectservicesignalr.azurewebsites.net/signalr/negotiate"
params_negotiate = {
    'clientProtocol': '1.5',
    'connectionData': '[{"name":"signalrlivehubfederations"}]',
    '_': str(int(time.time() * 1000))
}

headers = {
    "Accept": "text/plain, */*; q=0.01",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
    "Connection": "keep-alive",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "Host": "dataprojectservicesignalr.azurewebsites.net",
    "Origin": "https://lnv-web.dataproject.com",
    "Cookie": "ARRAffinitySameSite=63fa60194151df348daca1d2679c8546e7c627decbaf3b5c0382e09339f81965"
}

negotiate_response = session.get(url_negotiate, headers=headers, params=params_negotiate)

if negotiate_response.status_code == 200:
    negotiation_data = negotiate_response.json()
    connection_token = negotiation_data['ConnectionToken']
    
    # Étape 2 : Appel à l'endpoint `start`
    url_start = "https://dataprojectservicesignalr.azurewebsites.net/signalr/start"
    params_start = {
        'transport': 'serverSentEvents',
        'clientProtocol': '1.5',
        'connectionToken': connection_token,
        'connectionData': '[{"name":"signalrlivehubfederations"}]',
        '_': str(int(time.time() * 1000))
    }

    start_response = session.get(url_start, headers=headers, params=params_start)
    if start_response.status_code == 200:
        print("Session démarrée avec succès :", start_response.json())

        # Étape 3 : Appel à l'endpoint `send` pour initier les données
        url_send = "https://dataprojectservicesignalr.azurewebsites.net/signalr/send"
        params_send = {
            'transport': 'serverSentEvents',
            'clientProtocol': '1.5',
            'connectionToken': connection_token,
            'connectionData': '[{"name":"signalrlivehubfederations"}]'
        }

        # Exemple de données que vous pourriez devoir envoyer, adaptées en fonction des spécificités du serveur
        data = {
            "data": '{"H":"signalrlivehubfederations","M":"getLiveScoreListData_From_ES","A":["8094","lnv"],"I":0}'  # Remplacez "matchIdHere" par l'ID du match si requis
        }
        
        send_response = session.post(url_send, headers=headers, params=params_send, data=data)
        if send_response.status_code == 200:
            print("Données envoyées avec succès :", send_response.json())

            # Étape 4 : Établir la connexion SSE pour recevoir les événements
            url_connect = "https://dataprojectservicesignalr.azurewebsites.net/signalr/connect"
            params_connect = {
                'transport': 'serverSentEvents',
                'clientProtocol': '1.5',
                'connectionToken': connection_token,
                'connectionData': '[{"name":"signalrlivehubfederations"}]',
                'tid': '1'
            }

            connect_response = session.get(url_connect, headers=headers, params=params_connect, stream=True)
            if connect_response.status_code == 200:
                print("Connexion SSE établie. En attente des événements...")

                # Lire les événements en continu
                for line in connect_response.iter_lines(decode_unicode=True):
                    if line:
                        print(f"Événement reçu : {line}")
            else:
                print(f"Erreur de connexion SSE : {connect_response.status_code} - {connect_response.text}")
        else:
            print(f"Erreur lors de l'envoi des données : {send_response.status_code} - {send_response.text}")
    else:
        print(f"Erreur lors du démarrage de la session : {start_response.status_code} - {start_response.text}")
else:
    print(f"Erreur de négociation : {negotiate_response.status_code} - {negotiate_response.text}")