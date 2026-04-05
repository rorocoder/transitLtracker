
import json
import struct

import requests
from datetime import datetime, timedelta
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import src.config as config
from src.utils import to_datetime, to_datetime_iso, format_timedelta, format_datetime, to_iso, to_seconds


def get_trips():
    
    # ___ TIME SYNCHRONIZATION ___
    
    current_time = time_synchronization()
    print(f"CURRENT TIME: {current_time}")
    
    # ___ BUS TIMES ___ 
    
    ellis_bus_predictions = bus_timings(config.ELLIS_BUS_STOP_ID)
    # print(ellis_bus_predictions)
    print("ELLIS BUS ARRIVAL PREDICTIONS:")
    for vehicle_id, details in ellis_bus_predictions.items():
        print(f"ID: {vehicle_id}, Arrival Time: {details['arrival_time']}")
    print("\n")
    
    relevant_vehicles = set(ellis_bus_predictions.keys())
    
    print(f"{len(relevant_vehicles)} RELEVANT BUSES: {relevant_vehicles}\n")
    
    gl_bus_predictions = bus_timings(config.GL_BUS_STOP_ID, relevant_vehicles)
    
    print("\nGL BUS ARRIVAL PREDICTIONS:")
    for vehicle_id, details in gl_bus_predictions.items():
        print(f"Bus ID: {vehicle_id}, Arrival Time: {details['arrival_time']}")

    rl_bus_predictions = bus_timings(config.RL_BUS_STOP_ID, relevant_vehicles)
    
    print("\nRL BUS ARRIVAL PREDICTIONS:")
    for vehicle_id, details in rl_bus_predictions.items():
        print(f"Bus ID: {vehicle_id}, Arrival Time: {details['arrival_time']}")
    
    earliest_gl_arrival = min((pred['arrival_time'] for pred in gl_bus_predictions.values()), default=None)
    earliest_rl_arrival = min((pred['arrival_time'] for pred in rl_bus_predictions.values()), default=None)
    print(f"\nEarliest GL Arrival: {earliest_gl_arrival}, Earliest RL Arrival: {earliest_rl_arrival}\n")
    
    # ___ TRAIN TIMES ___ 
    print("TRAINS: \n")
    
    gl_train_predictions = train_timings(config.GL_GARFIELD_TRAIN_STOP_ID)
    
    print("GL Train Predictions:")
    for train_id, details in gl_train_predictions.items():
        print(f"Train ID: {train_id}, Arrival Time: {details['arrival_time']}")

    rl_train_predictions = train_timings(config.RL_GARFIELD_TRAIN_STOP_ID)
    
    print("\nRL Train Predictions:")
    for train_id, details in rl_train_predictions.items():
        print(f"Train ID: {train_id}, Arrival Time: {details['arrival_time']}")
    
    # ___ BUILD WAIT TIMES ___ 
    print("\nWAIT TIMES: \n")
    
    trip_options = build_trips(ellis_bus_predictions, gl_bus_predictions, rl_bus_predictions, gl_train_predictions, rl_train_predictions, relevant_vehicles, current_time)

    trip_options.sort(key=lambda trip: trip.ellis_time_to_arrival)
    for trip in trip_options:
        print(f"Vehicle ID: {trip.vehicle_id}, Ellis Time To Arrival: {trip.ellis_time_to_arrival}, GL Train Deltas: {trip.gl_train_deltas}, RL Train Deltas: {trip.rl_train_deltas}")
        
        # decision = Decision(**entry)
        # print(decision)
    
    # ___ MAKE DECISION ___ 
    print("\nDECISIONS: \n")
    
    for trip in trip_options:
        print(json.dumps(trip.output(), indent=4))
        
    return {"trips": [trip.output() for trip in trip_options]}
    
    
    # make_decision(trip_options)
    
class TripOption:
    def __init__(self, vehicle_id, ellis_time_to_arrival, ellis_arrival_time, gl_train_deltas, rl_train_deltas, gl_train_arrivals, rl_train_arrivals, gl_bus_arrival, rl_bus_arrival):
        self.vehicle_id = vehicle_id
        self.ellis_time_to_arrival = ellis_time_to_arrival
        self.ellis_arrival_time = ellis_arrival_time
        
        self.gl_train_deltas = gl_train_deltas
        self.rl_train_deltas = rl_train_deltas 
        
        self.gl_train_arrivals = gl_train_arrivals
        self.rl_train_arrivals = rl_train_arrivals
        
        self.gl_bus_arrival = gl_bus_arrival
        self.rl_bus_arrival = rl_bus_arrival
        
        self.gl_good_option = None
        self.rl_good_option = None
        
        self.next_gl_delta = None
        self.next_rl_delta = None
        
        self.next_gl_time = None
        self.next_rl_time = None
        
        self.evaluate()
        
    def evaluate(self):
        self.gl_good_option = any(delta <= timedelta(minutes=config.GOOD_GL_WAIT) for delta in self.gl_train_deltas)
        self.rl_good_option = any(delta <= timedelta(minutes=config.GOOD_RL_WAIT) for delta in self.rl_train_deltas)
        
        self.next_gl_delta = min(self.gl_train_deltas) if self.gl_train_deltas else None 
        self.next_rl_delta = min(self.rl_train_deltas) if self.rl_train_deltas else None
        
        self.next_gl_time = self.gl_bus_arrival + self.next_gl_delta if self.next_gl_delta is not None else None
        self.next_rl_time = self.rl_bus_arrival + self.next_rl_delta if self.next_rl_delta is not None else None

    def __repr__(self):
        pass

    def output(self):
        return {
            "vehicle_id": self.vehicle_id,
            "ellis_time_to_arrival_sec": to_seconds(self.ellis_time_to_arrival),
            "ellis_arrival_iso": to_iso(self.ellis_arrival_time),
            "gl_good_option": self.gl_good_option,
            "rl_good_option": self.rl_good_option,
            "gl_connection_delta_sec": to_seconds(self.next_gl_delta),
            "gl_connection_time_iso": to_iso(self.next_gl_time),
            "rl_connection_delta_sec": to_seconds(self.next_rl_delta),
            "rl_connection_time_iso": to_iso(self.next_rl_time),
        }
    
    def __str__(self):
        return f"Vehicle ID: {self.vehicle_id}, Ellis Time To Arrival: {format_timedelta(self.ellis_time_to_arrival)}, GL Train Deltas: {[format_timedelta(delta) for delta in self.gl_train_deltas]}, RL Train Deltas: {[format_timedelta(delta) for delta in self.rl_train_deltas]}, GL Train Arrivals: {[format_datetime(arrival) for arrival in self.gl_train_arrivals]}, RL Train Arrivals: {[format_datetime(arrival) for arrival in self.rl_train_arrivals]}, GL Bus Arrival: {format_datetime(self.gl_bus_arrival)}, RL Bus Arrival: {format_datetime(self.rl_bus_arrival)}"

def make_decision(trip_options):
    # for each bus, if there is a train arriving within some minutes of the bus arrival, consider it a good option
    for trip in trip_options:
        vehicle_id = trip.vehicle_id
        ellis_time_to_arrival = trip.ellis_time_to_arrival
        gl_train_deltas = trip.gl_train_deltas
        rl_train_deltas = trip.rl_train_deltas
        
        gl_good_option = any(delta <= timedelta(minutes=config.GOOD_GL_WAIT) for delta in gl_train_deltas)
        rl_good_option = any(delta <= timedelta(minutes=config.GOOD_RL_WAIT) for delta in rl_train_deltas)
        
        best_gl_option = min(gl_train_deltas) if gl_train_deltas else None 
        best_rl_option = min(rl_train_deltas) if rl_train_deltas else None
        
        if gl_good_option and rl_good_option:
            print(f"Vehicle ID: {vehicle_id} (in {format_timedelta(ellis_time_to_arrival)} mins) is a good option for both GL ({format_timedelta(min(gl_train_deltas))} min wait) and RL ({format_timedelta(min(rl_train_deltas))} min wait).")
        elif gl_good_option:
            print(f"Vehicle ID: {vehicle_id} (in {format_timedelta(ellis_time_to_arrival)} mins) is a good option for GL ({format_timedelta(min(gl_train_deltas))} min wait). RL has a wait of {format_timedelta(best_rl_option)} mins.")
        elif rl_good_option:
            print(f"Vehicle ID: {vehicle_id} (in {format_timedelta(ellis_time_to_arrival)} mins) is a good option for RL ({format_timedelta(min(rl_train_deltas))} min wait). GL has a wait of {format_timedelta(best_gl_option)} mins.")
        else:
            print(f"Vehicle ID: {vehicle_id} (in {format_timedelta(ellis_time_to_arrival)} mins) does not have a good train connection (GL: {format_timedelta(best_gl_option)}, RL: {format_timedelta(best_rl_option)}).")


def build_trips(ellis_bus_predictions, gl_bus_predictions, rl_bus_predictions, gl_train_predictions, rl_train_predictions, relevant_vehicles, current_time):
    # for each bus, store time to arrival at ellis, time to arrival at gl and rl, time to arrival of next trains at gl and rl
    trips = []
     
    for vehicle_id in relevant_vehicles:
        wait_time_entry = {}
        ellis_arrival_time = ellis_bus_predictions[vehicle_id]['arrival_time']
        rl_bus_arrival_time = rl_bus_predictions.get(vehicle_id, {}).get('arrival_time', None)
        gl_bus_arrival_time = gl_bus_predictions.get(vehicle_id, {}).get('arrival_time', None)
        
        gl_train_arrivals_times = [
            pred['arrival_time']
            for pred in gl_train_predictions.values()
            if gl_bus_arrival_time is not None and pred['arrival_time'] >= gl_bus_arrival_time
        ]
        
        rl_train_arrivals_times = [
            pred['arrival_time']
            for pred in rl_train_predictions.values()
            if rl_bus_arrival_time is not None and pred['arrival_time'] >= rl_bus_arrival_time
        ]
        
        # print(f"Vehicle ID: {vehicle_id}, Ellis Arrival: {ellis_arrival_time}, GL Bus Arrival: {gl_bus_arrival_time}, RL Bus Arrival: {rl_bus_arrival_time}, GL Train Arrivals: {gl_train_arrivals_times}, RL Train Arrivals: {rl_train_arrivals_times}")
        
        ellis_delta = ellis_arrival_time - current_time
        gl_deltas = [train_time - gl_bus_arrival_time for train_time in gl_train_arrivals_times]
        rl_deltas = [train_time - rl_bus_arrival_time for train_time in rl_train_arrivals_times]
        
        # print(f"Vehicle ID: {vehicle_id}, Ellis Time To Arrival: {ellis_delta}, GL Train Deltas: {gl_deltas}, RL Train Deltas: {rl_deltas}")
        
        # wait_time_entry = {
        #     'vehicle_id': vehicle_id,
        #     'ellis_time_to_arrival': ellis_delta,
        #     'gl_train_deltas': gl_deltas,
        #     'rl_train_deltas': rl_deltas
        # }
        
        decision = TripOption(
            vehicle_id=vehicle_id,
            ellis_time_to_arrival=ellis_delta,
            ellis_arrival_time=ellis_arrival_time,
            gl_train_deltas=gl_deltas, # only after
            rl_train_deltas=rl_deltas, # only after
            gl_train_arrivals=gl_train_arrivals_times, # these are only ones arriving after the bus arrival time
            rl_train_arrivals=rl_train_arrivals_times, # these are only ones arriving after the bus arrival time
            gl_bus_arrival=gl_bus_arrival_time,
            rl_bus_arrival=rl_bus_arrival_time
        )
        
        trips.append(decision)
    return trips
        
       

def bus_timings(stop_id, relevant_vehicles=None):
    key = config.CTA_BUS_API_KEY
    prediction_call = f"https://www.ctabustracker.com/bustime/api/v3/getpredictions"
    
    params = {
        'key': key,
        'format': 'json',
        'rt': '55',
        'stpid': stop_id,
        'tmres': 's'
    }
    
    response = requests.get(prediction_call, params=params)
    # print(response.status_code)  # Output: 200 (Success)
    # print(response.json())
    data_json = response.json()
    
    prediction_results = {}
    
    for prediction in data_json['bustime-response'].get('prd', []):
        vehicle_id = prediction['vid']
        if relevant_vehicles is None or vehicle_id in relevant_vehicles:
            prediction_results[prediction['vid']] = {
                'call_time': to_datetime(prediction['tmstmp']),
                'arrival_time': to_datetime(prediction['prdtm']),
                'distance_feet': prediction['dstp'],
                'minute_to_arrival': prediction['prdctdn'],
                'destination': prediction['des'],
                'stop_id': prediction['stpid'],
                'stop_name': prediction['stpnm'],
            }

    # for vehicle_id, details in prediction_results.items():
        # print(f"Vehicle ID: {vehicle_id}, Call Time: {details['call_time']}, Arrival Time: {details['arrival_time']}, Distance (feet): {details['distance_feet']}, Minutes to Arrival: {details['minute_to_arrival']}, Destination: {details['destination']}, Stop: {details['stop_name']}")
    
    return prediction_results

def time_synchronization():
    time_call = "https://www.ctabustracker.com/bustime/api/v3/gettime"
    
    time_params = {
        'key': config.CTA_BUS_API_KEY,
        'format': 'json'
    }
    
    time_response = requests.get(time_call, params=time_params)
    # print(time_response.status_code)  # Output: 200 (Success)
    return to_datetime(time_response.json()['bustime-response']['tm'])

def train_timings(stop_id):
    prediction_call = f"https://lapi.transitchicago.com/api/1.0/ttarrivals.aspx"
    
    params = {
        'key': config.CTA_TRAIN_API_KEY,
        'stpid': stop_id,
        'outputType': 'JSON'
    }
    
    response = requests.get(prediction_call, params=params)
    # print(response.status_code)  # Output: 200 (Success)
    data_json = response.json()
    
    train_predictions = {}
    
    for prediction in data_json['ctatt'].get('eta', []):
        train_predictions[prediction['rn']] = {
            'arrival_time': to_datetime_iso(prediction['arrT']),
            'stop_id': prediction['stpId'],
            'stop_name': prediction['staNm'] + ' ' + prediction['stpDe'],
            'line': prediction['rt'],
        }
    
    return train_predictions
        




if __name__ == "__main__":
    print(get_trips())
