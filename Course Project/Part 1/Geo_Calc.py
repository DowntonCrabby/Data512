
##################################
#
# IMPORTS
#
##################################
import pandas as pd
from pyproj import Transformer, Geod
from typing import List, Tuple, Dict, Optional


##################################
#
# Distance functions
#
##################################


def shortest_distance_from_location_to_fire_perimeter(location: Tuple[float, float] = None, 
                                                      fire_perimeter: List[Tuple[float, float]] = None
                                                      ) -> Tuple[float, Tuple[float, float]]:
    """
    Calculate the shortest distance from a specified location to the nearest 
    point on a fire perimeter.

    Parameters
    ----------
    location : Tuple[float, float], optional
        A tuple representing the latitude and longitude (lat, lon) of the 
        location in decimal degrees (EPSG:4326).
    fire_perimeter : List[Tuple[float, float]], optional
        A list of (latitude, longitude) coordinates representing the fire 
        perimeter in EPSG:4326.

    Returns
    -------
    Tuple[float, Tuple[float, float]]
        A tuple containing:
            - The shortest distance from the location to the fire perimeter in miles.
            - The coordinates of the nearest point on the fire perimeter.
    """
    perimeter_converted = convert_ring_to_epsg4326(fire_perimeter)
    geodetic_calculator = Geod(ellps='WGS84')
    
    closest_distance_miles = float('inf')
    nearest_point = (0.0, 0.0)
    
    for point in perimeter_converted:
        distance = geodetic_calculator.inv(location[1], location[0], point[1], point[0])
        distance_miles = meters_to_miles(distance[2])
        
        if distance_miles < closest_distance_miles:
            closest_distance_miles = distance_miles
            nearest_point = point

    return closest_distance_miles, nearest_point


def average_distance_from_location_to_fire_perimeter(location: Tuple[float, float] = None, 
                                                     fire_perimeter: List[Tuple[float, float]] = None
                                                     ) -> float:
    """
    Calculate the average distance from a specified location to the points on 
    a fire perimeter.

    Parameters
    ----------
    location : Tuple[float, float], optional
        A tuple representing the latitude and longitude (lat, lon) of the 
        location in decimal degrees (EPSG:4326).
    fire_perimeter : List[Tuple[float, float]], optional
        A list of (latitude, longitude) coordinates representing the fire 
        perimeter in EPSG:4326.

    Returns
    -------
    float
        The average distance, in miles, from the location to the fire perimeter.
    """
    perimeter_converted = convert_ring_to_epsg4326(fire_perimeter)
    geodetic_calculator = Geod(ellps='WGS84')
    
    distances_in_meters: List[float] = []
    for point in perimeter_converted:
        distance = geodetic_calculator.inv(location[1], location[0], point[1], point[0])
        distances_in_meters.append(distance[2])
    
    distances_in_miles = [meters_to_miles(meters) for meters in distances_in_meters]
    unique_distances = distances_in_miles[1:]
    average_distance_miles = sum(unique_distances) / len(unique_distances)
    
    return average_distance_miles


def find_nearby_fires(place: Tuple[float, float], 
                      search_distance_miles: float, 
                      wildfire_features: List[Dict],
                      distance_type: str = "closest"
                      ) -> List[Dict[str, float]]:
    """
    Find wildfires within a specified distance from a given city, based on 
    either the closest or average distance from the fire perimeter.

    Parameters
    ----------
    place : Tuple[float, float]
        The latitude and longitude (lat, lon) of a city/place/location in decimal degrees.
    search_distance_miles : float
        The radius distance to search within, in miles.
    wildfire_features : List[Dict]
        A list of dictionaries representing wildfire data, each containing:
            - 'attributes': dictionary with fire metadata (e.g., 'Listed_Fire_Names')
            - 'geometry': dictionary with 'rings', a list of coordinates
    distance_type : str, optional
        The type of distance calculation to use. Options are "closest" for the 
        shortest distance to the fire perimeter or "average" for the average 
        distance to the fire perimeter. Defaults to "closest".

    Returns
    -------
    List[Dict[str, float]]
        A list of dictionaries for each fire within the search radius, 
        containing:
            - 'fire_name': Name of the fire.
            - 'distance_miles': Distance from the city to the fire perimeter.
    """
    fires_within_radius = []
    total_features = len(wildfire_features)
    processed_count = 0

    # Validate distance_type argument
    if distance_type not in ["closest", "average"]:
        raise ValueError("distance_type must be 'closest' or 'average'")

    # Loop through wildfire features and calculate the specified distance to city
    for feature in wildfire_features:
        # Track progress every 100 features
        processed_count += 1
        if processed_count % 100 == 0 or processed_count == total_features:
            print(f"Processed {processed_count}/{total_features} features...")

        # Ensure the feature has 'attributes' and 'geometry' keys
        if 'attributes' not in feature or 'geometry' not in feature:
            continue

        fire_name = feature['attributes'].get('Listed_Fire_Names', 'Unknown Fire')
        
        # Ensure geometry contains 'rings' with polygon data
        if 'rings' not in feature['geometry'] or not feature['geometry']['rings']:
            continue

        fire_perimeter = feature['geometry']['rings'][0]  # Assuming the first ring represents the perimeter

        # Calculate the specified type of distance
        if distance_type == "closest":
            distance_miles, _ = shortest_distance_from_location_to_fire_perimeter(
                location=place,
                fire_perimeter=fire_perimeter
            )
        elif distance_type == "average":
            distance_miles = average_distance_from_location_to_fire_perimeter(
                location=place,
                fire_perimeter=fire_perimeter
            )

        # Check if the calculated distance is within the search distance
        if distance_miles <= search_distance_miles:
            fires_within_radius.append({
                'fire_name': fire_name,
                'distance_miles': distance_miles
            })

    print(f"Total features processed: {processed_count}/{total_features}")
    return fires_within_radius


##################################
#
# Metadata functions
#
##################################

def nearby_fires_to_dataframe(fires_within_radius: List[Dict[str, float]]) -> pd.DataFrame:
    """
    Converts the output of the `find_nearby_fires` function into a DataFrame.
    
    Parameters
    ----------
    fires_within_radius : List[Dict[str, float]]
        A list of dictionaries with wildfire information, each containing:
            - 'fire_name': Name of the fire.
            - 'distance_miles': Distance from the specified city to the fire perimeter.
    
    Returns
    -------
    pd.DataFrame
        A DataFrame containing the fire name and distance in miles.
    """
    # Convert the list of dictionaries to a DataFrame
    df = pd.DataFrame(fires_within_radius)
    
    # Add optional sorting by distance if desired
    df = df.sort_values(by='distance_miles').reset_index(drop=True)
    
    return df

def extract_fire_metadata(
    fires_within_radius: List[Dict[str, float]], 
    wildfire_features: List[Dict]
) -> pd.DataFrame:
    """
    Extracts metadata for fires within range and converts it to a DataFrame.

    Parameters
    ----------
    fires_within_radius : List[Dict[str, float]]
        Output from `find_nearby_fires` function, containing:
            - 'fire_name': Name of the fire.
            - 'distance_miles': Distance from the specified city to the fire perimeter.
    wildfire_features : List[Dict]
        Original wildfire data list with metadata for each fire feature.

    Returns
    -------
    pd.DataFrame
        DataFrame with fire name, distance in miles, and metadata fields.
    """
    # Create a list to store fire metadata with distances
    enriched_fires_data = []

    # Extract metadata for each fire within the radius
    for fire in fires_within_radius:
        fire_name = fire['fire_name']
        distance_miles = fire['distance_miles']
        
        # Locate the corresponding feature in the original data
        for feature in wildfire_features:
            if feature.get('attributes', {}).get('Listed_Fire_Names', 'Unknown Fire') == fire_name:
                # Extract metadata and add distance
                fire_metadata = feature.get('attributes', {}).copy()
                fire_metadata['distance_miles'] = distance_miles  # Include the distance from the city
                enriched_fires_data.append(fire_metadata)
                break

    # Convert to DataFrame
    df = pd.DataFrame(enriched_fires_data)
    
    # Optional: Sort by distance
    df = df.sort_values(by='distance_miles').reset_index(drop=True)
    
    return df


##################################
#
# UTILITY FUNCTIONS
#
##################################

def convert_ring_to_epsg4326(ring_data: List[Tuple[float, float]] = None
                             ) -> List[Tuple[float, float]]:
    """
    Convert a list of coordinates from the ESRI:102008 projection to EPSG:4326 
    (decimal degrees).

    Parameters
    ----------
    ring_data : List[Tuple[float, float]], optional
        A list of (x, y) coordinates in the ESRI:102008 coordinate system, 
        by default None.

    Returns
    -------
    List[Tuple[float, float]]
        A list of converted (latitude, longitude) coordinates in EPSG:4326.
    """
    converted_ring: List[Tuple[float, float]] = []
    # Set up a transformer to convert from ESRI:102008 to EPSG:4326
    to_epsg4326 = Transformer.from_crs("ESRI:102008", "EPSG:4326")
    
    # Convert each coordinate from ESRI:102008 to EPSG:4326
    for coord in ring_data:
        lat, lon = to_epsg4326.transform(coord[0], coord[1])
        converted_ring.append((lat, lon))
        
    return converted_ring


def meters_to_miles(meters: float) -> float:
    """
    Convert a distance from meters to miles.

    Parameters
    ----------
    meters : float
        The distance in meters.

    Returns
    -------
    float
        The distance in miles.
    """
    METERS_TO_MILES_CONVERSION = 0.00062137
    return meters * METERS_TO_MILES_CONVERSION