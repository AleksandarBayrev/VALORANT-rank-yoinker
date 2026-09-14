import requests

class Names:
    # Renamed 'Requests' to 'requests_manager' to avoid shadowing the 'requests' library
    def __init__(self, requests_manager, log):
        self.Requests = requests_manager
        self.log = log

    def get_name_from_puuid(self, puuid):
        names_dict = self.get_multiple_names_from_puuid([puuid])
        return names_dict.get(puuid, "Unknown#Player")

    def get_multiple_names_from_puuid(self, puuids):
        # Remove duplicates and empty strings from the request list
        puuids = list(filter(None, set(puuids)))
        if not puuids:
            return {}

        url = f"{self.Requests.pd_url}/name-service/v2/players"
        
        try:
            response = requests.put(
                url, 
                headers=self.Requests.get_headers(), 
                json=puuids, 
                verify=False
            )
            
            # Safely attempt to parse JSON; will throw ValueError if the API returns raw HTML/Errors
            data = response.json()

            # If the API returns a standard Riot error dictionary (e.g., token expired)
            if isinstance(data, dict) and 'errorCode' in data:
                self.log(f"API Error: {data.get('errorCode')}. Refreshing token...")
                
                # Retry with refreshed headers
                response = requests.put(
                    url, 
                    headers=self.Requests.get_headers(refresh=True), 
                    json=puuids, 
                    verify=False
                )
                data = response.json()

            # Handle edge cases where the API returns something other than a list of players
            if not isinstance(data, list):
                self.log(f"Unexpected response format: {data}")
                return {}

            # Safely build the dictionary, ensuring keys actually exist before combining them
            return {
                player["Subject"]: f"{player['GameName']}#{player['TagLine']}"
                for player in data 
                if all(k in player for k in ("Subject", "GameName", "TagLine"))
            }

        except requests.exceptions.RequestException as e:
            self.log(f"Network request failed: {e}")
            return {}
        except ValueError:
            self.log(f"Failed to parse JSON. HTTP Status: {response.status_code}, Response: {response.text}")
            return {}

    def get_names_from_puuids(self, players):
        # Used .get() to prevent KeyError if "Subject" is missing from a malformed player dict
        players_puuid = [player.get("Subject") for player in players if player.get("Subject")]
        return self.get_multiple_names_from_puuid(players_puuid)

    def get_players_puuid(self, players):
        return [player.get("Subject") for player in players if player.get("Subject")]