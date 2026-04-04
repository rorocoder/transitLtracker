import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import requests, json
import src.config as config
    
def metra():
    pass
    


def main():
    print("Hello, World!")
    key = "HbHypyud39TjHdG3xRMzK323y"
    call = f"https://www.ctabustracker.com/bustime/api/v3/getroutes?key={key}&format=json"
    predictions = f"https://www.ctabustracker.com/bustime/api/v3/getpredictions"
    
    params = {
        'key': key,
        'format': 'json',
        'rt': '55',
        'stpid': '10575',
        'tmres': 's'
    }
    
    response = requests.get(predictions, params=params)
    print(response.status_code)  # Output: 200 (Success)
    print(response.json()) 
    
    prediction_results = response.json()
    
    with open(os.path.join(os.path.dirname(__file__), "data_pretty.json"), "w") as file:
        json.dump(prediction_results, file, indent=4, sort_keys=True)
    print("____")
    # print(len(prediction_results['bustime-response']['prd']))
    
    curr_vehicles = []
        
    # for prediction in prediction_results['bustime-response']['prd']:
    #     call_time = prediction['tmstmp']
    #     arrival_time = prediction['prdtm']
    #     vehicle_id = prediction['vid']
    #     distance_feet = prediction['dstp']
    #     minute_to_arrival = prediction['prdctdn']
    #     destionation = prediction['des']
        
    #     curr_vehicles.append(vehicle_id)
        
    #     print(f"Vehicle ID: {vehicle_id}, Call Time: {call_time}, Arrival Time: {arrival_time}, Distance (feet): {distance_feet}, Minutes to Arrival: {minute_to_arrival}, Destination: {destionation}")
        
        
    detourscall = "https://www.ctabustracker.com/bustime/api/v3/getdetours"
    
    detours_params = {
        'key': key,
        'format': 'json',
        'rt': '55'
    }
    
    detours_response = requests.get(detourscall, params=detours_params)
    print(detours_response.status_code)  # Output: 200 (Success)
    print(detours_response.json()) 
    
    
    
    
    vehicles_call = "https://www.ctabustracker.com/bustime/api/v3/getvehicles"
    
    vehicles_params = {
        'key': key,
        'format': 'json',
        'vid': ','.join(curr_vehicles)
    }
    
    
    vehicles_response = requests.get(vehicles_call, params=vehicles_params)
    print(vehicles_response.status_code)  # Output: 200 (Success)
    print(vehicles_response.json()) 
    
    with open(os.path.join(os.path.dirname(__file__), "vehicles_data.json"), "w") as file:
        json.dump(vehicles_response.json(), file, indent=4, sort_keys=True)
    
    
    time_call = "https://www.ctabustracker.com/bustime/api/v3/gettime"
    
    time_params = {
        'key': key,
        'format': 'json'
    }
    
    time_response = requests.get(time_call, params=time_params)
    print(time_response.status_code)  # Output: 200 (Success)
    print(time_response.json())
    
    
    
    
    trains_arrivals_call = "http://lapi.transitchicago.com/api/1.0/ttarrivals.aspx"
    trains_arrivals_params = {
        'key': config.CTA_TRAIN_API_KEY,
        'stpid': config.RL_GARFIELD_TRAIN_STOP_ID,
        'outputType': 'JSON'
    }
    
    trains_arrivals_response = requests.get(trains_arrivals_call, params=trains_arrivals_params)
    print(trains_arrivals_response.status_code)  # Output: 200 (Success)
    print(trains_arrivals_response.json())
    
    with open(os.path.join(os.path.dirname(__file__), "train_arrivals.json"), "w") as file:
        json.dump(trains_arrivals_response.json(), file, indent=4, sort_keys=True)
    
    relevant_train_numbers = []
    for arrival in trains_arrivals_response.json()['ctatt']['eta']:
        print(f"Train ETA: {arrival['arrT']}, Train Destination: {arrival['destNm']}, Train Line: {arrival['rt']}, Train Number: {arrival['rn']}")
        relevant_train_numbers.append(arrival['rn'])
        
    print("______")
    
    print(type(relevant_train_numbers[0]))
    
    train_route_call = "http://lapi.transitchicago.com/api/1.0/ttarrivals.aspx"
    train_route_params = {
        'key': config.CTA_TRAIN_API_KEY,
        'stpid': relevant_train_numbers[0],
        'outputType': 'JSON'
    }
    
    train_route_response = requests.get(train_route_call, params=train_route_params)
    print(train_route_response.status_code)  # Output: 200 (Success)
    print(train_route_response.json())
    


if __name__ == "__main__":
    main()