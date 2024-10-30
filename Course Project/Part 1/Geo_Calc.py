
##################################
#
# IMPORTS
#
##################################
import pandas as pd
from pyproj import Transformer, Geod
from typing import List, Tuple, Dict, Union, Optional

##################################
#
# CONSTANTS
#
##################################

GEODESIC_CALCULATOR = Geod(ellps="WGS84")
to_epsg4326 = Transformer.from_crs("ESRI:102008", "EPSG:4326", always_xy=True)

##################################
#
# WORKING WITH COORDINATES
#
##################################

def convert_ring_to_epsg4326(ring_data: List[Union[List[float], Tuple[float, float]]]) -> List[Tuple[float, float]]:
    """
    Converts a ring of coordinates from ESRI:102008 projection to EPSG:4326 (latitude, longitude).
    
    Args:
        ring_data (List[Union[List[float], Tuple[float, float]]]): A list of coordinates representing a ring. 
            Each coordinate should be a list or tuple containing at least two floats [x, y].
    
    Returns:
        List[Tuple[float, float]]: A list of transformed coordinates in (latitude, longitude) format.
    
    Example:
        ring = [[1000000.0, 2000000.0], [1100000.0, 2100000.0]]
        converted_ring = convert_ring_to_epsg4326(ring)
    
    The function performs the following:
        1. Initializes a transformer to convert from ESRI:102008 to EPSG:4326.
        2. Iterates over each coordinate in `ring_data`.
        3. Attempts to transform valid coordinates to (latitude, longitude) and appends them to `converted_ring`.
        4. Skips and logs any invalid or improperly structured coordinates.
    """
    converted_ring: List[Tuple[float, float]] = []
    transformer_to_epsg4326 = Transformer.from_crs("ESRI:102008", "EPSG:4326", always_xy=True)

    for coordinate in ring_data:
        if isinstance(coordinate, (list, tuple)) and len(coordinate) >= 2:
            try:
                lon, lat = transformer_to_epsg4326.transform(coordinate[0], coordinate[1])
                converted_ring.append((lat, lon))
            except Exception as e:
                print(f"Error transforming coordinates {coordinate}: {e}")
        else:
            print(f"Skipping invalid coordinate data: {coordinate}")

    return converted_ring


##################################
#
# Distance functions
#
##################################
geodesic_calculator = Geod(ellps="WGS84")
to_epsg4326 = Transformer.from_crs("ESRI:102008", "EPSG:4326", always_xy=True)

def shortest_distance_from_location_to_fire_perimeter(
        location: Optional[Tuple[float, float]] = None,
        ring_data: Optional[List[Tuple[float, float]]] = None
        ) -> Tuple[float, Optional[Tuple[float, float]]]:
    """
    Calculate the shortest distance from a specified location to the 
    nearest point on a fire perimeter.

    Parameters
    ----------
    location : tuple of float, optional
        The latitude and longitude of the reference location as 
        (latitude, longitude). Default is None.
    ring_data : list of tuple of float, optional
        A list of coordinates representing the fire perimeter 
        in (latitude, longitude) format. Coordinates are expected 
        in ESRI:102008 projection, and will be converted to EPSG:4326.
        Default is None.

    Returns
    -------
    tuple of (float, tuple of float or None)
        A tuple containing:
            - The shortest distance from `location` to the fire perimeter 
              in miles.
            - The coordinates of the closest point on the perimeter as 
              (latitude, longitude), or None if no valid perimeter 
              points were found.

    Raises
    ------
    ValueError
        If either `location` or `ring_data` is not provided.
    """
    if location is None or ring_data is None:
        raise ValueError("Both 'location' and 'ring_data' must be provided.")
    
    transformed_ring: List[Tuple[float, float]] = convert_ring_to_epsg4326(ring_data)
    closest_distance: float = float('inf')
    closest_point: Optional[Tuple[float, float]] = None

    for perimeter_point in transformed_ring:
        dist_in_meters = geodesic_calculator.inv(location[1],
                                                 location[0],
                                                 perimeter_point[1],
                                                 perimeter_point[0])[2]
        distance_in_miles = meters_to_miles(dist_in_meters)

        if distance_in_miles < closest_distance:
            closest_distance = distance_in_miles
            closest_point = perimeter_point

    return closest_distance, closest_point


def average_distance_from_location_to_fire_perimeter(
        location: Tuple[float, float] = None,
        fire_perimeter: List[Tuple[float, float]] = None
        ) -> float:
    """
    Calculate the average distance from a specified location to points on 
    a fire perimeter.

    Parameters
    ----------
    location : tuple of float, optional
        A tuple representing the latitude and longitude (lat, lon) of the 
        location in decimal degrees (EPSG:4326).
    fire_perimeter : list of tuple of float, optional
        A list of (latitude, longitude) coordinates representing the fire 
        perimeter in EPSG:4326 projection.

    Returns
    -------
    float
        The average distance, in miles, from the location to the fire 
        perimeter.

    Raises
    ------
    ValueError
        If either `location` or `fire_perimeter` is not provided.
    """
    if location is None or fire_perimeter is None:
        raise ValueError("Both 'location' and 'fire_perimeter' must be provided.")

    perimeter_converted = convert_ring_to_epsg4326(fire_perimeter)
    
    distances_in_meters: List[float] = []
    for point in perimeter_converted:
        distance = GEODESIC_CALCULATOR.inv(location[1],
                                           location[0],
                                           point[1],
                                           point[0])
        distances_in_meters.append(distance[2])
    
    distances_in_miles = [meters_to_miles(meters) for meters in distances_in_meters]
    unique_distances = distances_in_miles[1:]  # Remove any duplicates or outliers if needed
    average_distance_miles = sum(unique_distances) / len(unique_distances)
    
    return average_distance_miles


def find_fires_within_range(
        location: Tuple[float, float],
        max_distance_miles: float,
        feature_list: List[Dict],
        distance_type: str = "closest",
        debug: bool = False
        ) -> List[Dict[str, Union[str, float, int, Tuple[float, float]]]]:
    """
    Find fires within a specified distance range from a given location.

    Parameters
    ----------
    location : tuple of float
        A tuple representing the latitude and longitude (lat, lon) of the 
        location in decimal degrees (EPSG:4326).
    max_distance_miles : float
        The maximum distance in miles to search for fires.
    feature_list : list of dict
        A list of features representing fire data, where each feature 
        contains 'attributes' and 'geometry' keys.
    distance_type : {'closest', 'average'}, optional
        The type of distance calculation to use:
        - 'closest': Uses the shortest distance from `location` to the 
          fire perimeter.
        - 'average': Uses the average distance from `location` to the 
          fire perimeter.
        Default is 'closest'.
    debug : bool, optional
        If True, print debugging statements during processing. Default 
        is False.

    Returns
    -------
    list of dict
        A list of dictionaries for fires within the specified range, 
        each containing:
        - 'fire_name': Name of the fire.
        - 'fire_year': Year of the fire.
        - 'fire_size_acres': Area of the fire in acres.
        - 'distance_miles': The calculated distance to the fire perimeter.
        - 'perimeter_points_count': Number of points in the perimeter.
        - 'closest_point' or 'average_point': The closest or representative
          point on the fire perimeter.

    Raises
    ------
    ValueError
        If `distance_type` is not 'closest' or 'average'.

    Examples
    --------
    >>> location = (34.0522, -118.2437)  # Los Angeles coordinates
    >>> max_distance_miles = 50
    >>> fires = find_fires_within_range(location, max_distance_miles, fire_features)
    """
    if distance_type not in {"closest", "average"}:
        raise ValueError("distance_type must be 'closest' or 'average'.")

    fires_within_range = []
    total_features = len(feature_list)

    for feature_index, fire_feature in enumerate(feature_list):
        if debug and feature_index % 100 == 0:
            print(f"Processing feature {feature_index + 1} of {total_features}...")

        fire_attributes = fire_feature.get('attributes', {})
        fire_geometry = fire_feature.get('geometry', {})

        if 'rings' in fire_geometry:
            ring_data = fire_geometry['rings'][0]
        elif 'curveRings' in fire_geometry:
            ring_data = fire_geometry['curveRings'][0]
        else:
            continue

        if distance_type == "closest":
            distance, point = shortest_distance_from_location_to_fire_perimeter(location, ring_data)
        else:
            distance = average_distance_from_location_to_fire_perimeter(location, ring_data)
            point = None  # Average distance does not yield a specific point

        if debug:
            print(f"Feature {feature_index + 1}: Distance to perimeter = {distance:.2f} miles")

        if distance <= max_distance_miles:
            fires_within_range.append({
                'fire_name': fire_attributes.get('Listed_Fire_Names', 'Unknown Fire').split(',')[0],
                'fire_year': fire_attributes.get('Fire_Year', 'Unknown Year'),
                'fire_size_acres': fire_attributes.get('GIS_Acres', 0),
                'distance_miles': distance,
                'perimeter_points_count': len(ring_data),
                'closest_point' if distance_type == "closest" else 'average_point': point
            })

    if debug and not fires_within_range:
        print(f"No fires found within {max_distance_miles} miles of location {location}.")

    if debug:
        print(f"Finished processing {total_features} features.")

    return fires_within_range


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