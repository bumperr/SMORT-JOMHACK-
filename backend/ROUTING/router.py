import json
import requests
from itertools import permutations
from dotenv import load_dotenv
import os
from pathlib import Path
class router:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://www.google.com/maps/dir/?api=1"
        self.matrix_api_url = "https://maps.googleapis.com/maps/api/distancematrix/json"

    def get_distance_matrix(self, origins, destinations):
        origin_str = "|".join(origins)
        destination_str = "|".join(destinations)
        params = {
            "origins": origin_str,
            "destinations": destination_str,
            "key": self.api_key
        }
        response = requests.get(self.matrix_api_url, params=params)



        data = response.json()

        #------------testing ----------------------
        # print ("Distance Matrix API response:", data)
        # if response.status_code != 200:
        #     print("Error: Failed to fetch distance matrix.")
        #     return None


        return data

    def generate_multi_stop_url(self, coordinates_json: str, origin: str) -> str:
        try:
            coordinates = json.loads(coordinates_json)
            if not isinstance(coordinates, list) or not all(
                isinstance(coord, dict) and 'latitude' in coord and 'longitude' in coord for coord in coordinates):
                print("Error: Invalid JSON format.")
                return None

            if len(coordinates) < 1:
                print("Error: At least one coordinate is required.")
                return None

            points = [f"{coord['latitude']},{coord['longitude']}" for coord in coordinates]
            destination = points[-1]
            waypoints = "|".join(points[:-1])
            # if waypoints:
            #     waypoints = f"optimize:true|{waypoints}"

            url = f"{self.base_url}&origin={origin}&destination={destination}"

            if waypoints:
                url += f"&waypoints={waypoints}"

            return url
        except json.JSONDecodeError:
            print("Error: Provided string is not valid JSON.")
            return None

    def sorting_waypoints(self, coordinates_json: str, origin: str,
                          EmissionRatePerKM: float, FuelConsumptionRatePerKM: float) -> str:

        # emission rate per KM is kg /km       
        # # fuel consumption rate per KM is L/km
        try:
            coordinates = json.loads(coordinates_json)
            if not coordinates:
                return coordinates_json

            all_points = [origin] + [f"{c['latitude']},{c['longitude']}" for c in coordinates]

            # Get distance matrix from Google API
            matrix = self.get_distance_matrix(all_points, all_points)
            if matrix['status'] != 'OK':
                print("Error: Distance Matrix API failed.")
                return coordinates_json

            distance_matrix = [
                [elem['distance']['value'] for elem in row['elements']]
                for row in matrix['rows']
            ]

            n = len(all_points)
            visited = [False] * n
            visited[0] = True  # origin
            order = []
            current = 0

            for _ in range(1, n):
                next_point = min(
                    ((i, distance_matrix[current][i]) for i in range(1, n) if not visited[i]),
                    key=lambda x: x[1],
                    default=(None, None)
                )[0]
                if next_point is None:
                    break
                order.append(next_point)
                visited[next_point] = True
                current = next_point

            sorted_coordinates = [coordinates[i - 1] for i in order]  # skip origin
            return json.dumps(sorted_coordinates)

        except Exception as e:
            print(f"Error during sorting: {e}")
            return coordinates_json



def test_generate_multi_stop_url():
    env_path = Path(__file__).resolve().parents[2] / '.env'
    load_dotenv(dotenv_path=env_path)

    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    router_instance = router(api_key)

    coordinates_json = json.dumps([  
    {"latitude": 4.366649, "longitude": 100.979163},  # Lotus
    {"latitude": 4.366175, "longitude": 100.978008},  # bayan mamak
    {"latitude": 4.376637, "longitude": 100.980260}   # longwan
        ])

    origin = "4.382281,100.970367"  # Chancellor Hall

    sorted_json = router_instance.sorting_waypoints(
        coordinates_json, origin, EmissionRatePerKM=0.2, FuelConsumptionRatePerKM=0.1
    )
    print("Sorted JSON:", sorted_json)

    url = router_instance.generate_multi_stop_url(sorted_json, origin)
    print("Google Maps URL:", url)



test_generate_multi_stop_url()
