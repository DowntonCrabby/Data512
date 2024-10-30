#!/usr/bin/python3
# -*- coding: utf-8 -*-
# 
#   FILE: Reader.py
#   REVISION: August, 2023
#   CREATION DATE: August, 2023
#   Author: David W. McDonald
#
#   A simple streaming reader/loader that is designed to load GeoJSON files. This class is part of
#   the wildfire user module. This module is distributed for student use in solving the DATA 512
#   class project.
#
#   Copyright by Author. All rights reserved. Not for reuse without express permissions.
#

import json
import os
from typing import Optional, Dict, Any, TextIO

import json
import os
from typing import Optional, Dict, Any, TextIO

class Reader:
    """
    A streaming reader compatible with GeoJSON data formats for wildfire datasets provided by the USGS.
    
    Public Methods:
        - open(filename: str) -> None: Opens a GeoJSON file for reading.
        - header() -> Dict[str, Any]: Returns metadata from the GeoJSON file as a dictionary.
        - next() -> Optional[Dict[str, Any]]: Reads the next GeoJSON feature as a dictionary.
        - rewind() -> None: Resets the reader to the beginning of the GeoJSON feature list.
        - close() -> None: Closes the open GeoJSON file.
    
    Usage:
        reader = Reader("file_to_read.json")
        feature = reader.next()
    """

    def __init__(self, filename: Optional[str] = None) -> None:
        super().__init__()
        self.filename: str = ""
        self.file_handle: Optional[TextIO] = None
        self.is_open: bool = False
        self.header_dict: Optional[Dict[str, Any]] = None
        self.feature_start_offset: int = 0
        
        if filename:
            self.open(filename)

    def open(self, filename: str) -> None:
        """
        Opens a GeoJSON file, reads the header information, and prepares to read features.
        
        Args:
            filename (str): Path to the GeoJSON file to open.
        
        Raises:
            Exception: If the file is already open or the specified file cannot be found.
        """
        if not filename:
            raise ValueError("Filename must be provided to open a file for reading.")
        
        if self.is_open:
            raise Exception(f"Reader is already open with file '{self.filename}'.")

        self.filename = filename
        
        try:
            self.file_handle = open(filename, "r")
            self.is_open = True
            self.header_dict = self.__read_geojson_header__(self.file_handle)
        except FileNotFoundError:
            current_path = os.getcwd()
            raise FileNotFoundError(f"Could not find '{filename}' in directory '{current_path}'.")
    
    def header(self) -> Dict[str, Any]:
        """
        Returns the GeoJSON header information as a dictionary.

        Raises:
            Exception: If the file is not open.
        """
        if not self.is_open:
            raise Exception("File must be opened using 'open()' before accessing the header.")
        return self.header_dict or {}

    def next(self) -> Optional[Dict[str, Any]]:
        """
        Reads the next GeoJSON feature as a dictionary.
        
        Returns:
            Optional[Dict[str, Any]]: A dictionary representing the next feature, or None if no more features are available.
        
        Raises:
            Exception: If the file is not open.
        """
        if not self.is_open:
            raise Exception("File must be opened using 'open()' before reading features.")
        return self.__next_geojson_feature__(self.file_handle)

    def rewind(self) -> None:
        """
        Resets the file pointer to the beginning of the feature list, allowing `next()` to re-read features.
        
        Raises:
            Exception: If the file is not open or if an error occurs in seeking.
        """
        if self.is_open and self.file_handle:
            try:
                self.file_handle.seek(self.feature_start_offset)
            except IOError:
                self.close()
                raise Exception("Error rewinding the file. The file has been closed.")

    def close(self) -> None:
        """
        Closes the GeoJSON file and resets the Reader's state.
        """
        if self.is_open and self.file_handle:
            self.file_handle.close()
            self.file_handle = None
            self.filename = ""
            self.is_open = False
            self.header_dict = None
            self.feature_start_offset = 0

    def __read_geojson_header__(self, file: TextIO) -> Dict[str, Any]:
        """
        Reads the GeoJSON header from the file, stopping at the start of the features list.
        
        Args:
            file (TextIO): The file handle for the opened GeoJSON file.
        
        Returns:
            Dict[str, Any]: A dictionary of header metadata.
        """
        buffer = ""
        header_data = ""
        chunk = file.read(100)

        while chunk:
            buffer += chunk
            if '"features":' in buffer or "'features':" in buffer:
                index = buffer.find('"features"') if '"features"' in buffer else buffer.find("'features'")
                file.seek(0)
                header_data = file.read(index).strip()
                file.read(len("'features'"))
                self.feature_start_offset = file.tell()
                break
            chunk = file.read(100)

        if header_data.endswith(','):
            header_data = header_data[:-1]
        header_data += "}"

        return json.loads(header_data)

    def __next_geojson_feature__(self, file: TextIO) -> Optional[Dict[str, Any]]:
        """
        Reads one feature dictionary from the GeoJSON file.
        
        Args:
            file (TextIO): The file handle for the opened GeoJSON file.
        
        Returns:
            Optional[Dict[str, Any]]: The next feature as a dictionary, or None if no features remain.
        """
        feature_str = ""
        while (char := file.read(1)):
            if char == '{':
                feature_str = self.__recurse_geojson_feature_dict__(file, char)
                break
        
        return json.loads(feature_str) if feature_str else None

    def __recurse_geojson_feature_dict__(self, file: TextIO, buffer: str, depth: int = 0) -> str:
        """
        Recursively constructs a JSON string for a single feature dictionary.
        
        Args:
            file (TextIO): The file handle for the opened GeoJSON file.
            buffer (str): The current buffer of the JSON string.
            depth (int): The current recursion depth.
        
        Returns:
            str: The JSON string for a single feature.
        
        Raises:
            Exception: If recursion depth exceeds 10, indicating malformed JSON.
        """
        if depth > 10:
            raise Exception("Corrupted GeoJSON 'features' list. Exceeded maximum recursion depth.")

        json_obj = buffer
        while (char := file.read(1)):
            if char == '{':
                json_obj += self.__recurse_geojson_feature_dict__(file, char, depth + 1)
            else:
                json_obj += char
            if char == '}':
                return json_obj
        return json_obj

if __name__ == '__main__':
    print("Reader.py is a class with no main()")


    
ESTIMATED_NUM_FEATURES = 136000    
def load_wildfire_features(json_file_path:str, 
                           max_features=ESTIMATED_NUM_FEATURES):
    """
    Load features from a JSON file using the wildfire Reader object and show progress.
    
    Parameters:
    - json_file_path (str): Path to the JSON file containing wildfire data.
    - max_features (int): Maximum number of features to load.
    
    Returns:
    - feature_list (list): List of loaded features.
    """
    print(f"Attempting to open '{json_file_path}' with wildfire.Reader() object")
    
    # Initialize Reader
    wfreader = Reader(json_file_path)
    print()
    
    # Print header information
    header_dict = wfreader.header()
    print("The header contains the following keys:")
    print(list(header_dict.keys()))
    print("Header Dictionary:")
    print(json.dumps(header_dict, indent=4))
    print()
    
    # Initialize feature list and counters
    feature_list = []
    feature_count = 0
    
    # Ensure reader is at the start of the file
    wfreader.rewind()
    
    # Load features and track progress
    feature = wfreader.next()
    while feature:
        feature_list.append(feature)
        feature_count += 1
        
        # Print progress every 100 features
        if feature_count % 100 == 0:
            print(f"Loaded {feature_count} features")
        
        # Stop if maximum features reached
        if feature_count >= max_features:
            break
        
        # Load the next feature
        feature = wfreader.next()
    
    # Final output of feature count
    print(f"Loaded a total of {feature_count} features")
    print(f"Variable 'feature_list' contains {len(feature_list)} features")
    
    return feature_list