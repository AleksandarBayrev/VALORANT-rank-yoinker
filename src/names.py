import requests

class Names:
    def __init__(self, Requests, log):
        self.Requests = Requests
        self.log = log

    def get_name_from_puuid(self, puuid):
        # Reuse the multiple names function to avoid duplicating the token refresh logic
        names_dict = self.get_multiple_names_from_puuid([puuid])
        return names_dict.get(puuid, "Unknown#Player")

    def get_multiple_names_from_puuid(self, puuids):
        if not puuids:
            return {}

        response = requests.put(
            self.Requests.pd_url + "/name-service/v2/players", 
            headers=self.Requests.get_headers(), 
            json=puuids, 
            verify=False
        )
        
        data = response.json()

        # If the API fails, it usually returns a dict with an error, 
        # whereas a success returns a list of player dictionaries.
        if isinstance(data, dict) and 'errorCode' in data:
            self.log(f'{data["errorCode"]}, new token retrieved')
            
            # Retry with refreshed headers
            response = requests.put(
                self.Requests.pd_url + "/name-service/v2/players", 
                headers=self.Requests.get_headers(refresh=True), 
                json=puuids, 
                verify=False
            )
            data = response.json()

        # Handle the case where the refresh also fails or returns unexpected data
        if not isinstance(data, list):
            self.log(f"Unexpected response format: {data}")
            return {}

        return {
            player["Subject"]: f"{player['GameName']}#{player['TagLine']}"
            for player in data if "Subject" in player
        }

    def get_names_from_puuids(self, players):
        # Simplified using list comprehension
        players_puuid = [player["Subject"] for player in players if "Subject" in player]
        return self.get_multiple_names_from_puuid(players_puuid)

    def get_players_puuid(self, players):
        # Standardized parameter casing (players instead of Players)
        return [player["Subject"] for player in players if "Subject" in player]