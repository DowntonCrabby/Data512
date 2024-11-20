##################################
#
# IMPORTS
#
##################################

import os
import pandas as pd
from typing import Tuple, Dict
import xml.etree.ElementTree as ET


##################################
#
# CONSTANTS
#
##################################
QUESTION_COL_NAME_MAP = {
    'Question 2': 'age',
    'Question 3': 'gender',
    'Question 4': 'race',
    'Question 5': 'zip_code',
    'Question 6': 'education_level',
    'Question 7': 'income',
    'Question 8': 'general_health_status',
    'Question 9': 'outside_activity_engagement',
    'Question 10': 'outside_activity_frequency',
    'Question 11': 'air_quality_notification_received',
    'Question 12': 'seek_air_quality_info',
    'Question 13': 'info_source_for_smoke_notifications',
    'Question 14': 'days_checked_for_smoke_info',
    'Question 15': 'reduced_outdoor_activities_due_to_smoke',
    'Question 16': 'consecutive_days_reduced_outdoor_activity',
    'Question 17': 'min_aqi_reduce_activity',
    'Question 18': 'min_aqi_eliminate_activity',
    'Question 19': 'motivating_info_to_reduce_outdoor_activity',
    'Question 20': 'motivating_message_type_for_mitigation',
    'Question 21': 'motivating_message_content',
    'Question 22': 'preferred_warning_timing',
    'Question 23': 'future_mitigation_actions',
    'Question 24': 'perception_of_smoke_as_hazard',
    'Question 25': 'compare_smoke_with_other_disasters',
    'Question 26': 'consider_evacuating_due_to_smoke',
    'Question 27': 'smoke_related_health_experience',
    'Question 28': 'symptoms_during_smoke_event',
    'Question 29': 'mitigation_strategies_for_health_issues'
}

##################################
#
# DATA LOADING AND STRUCTURE
#
##################################
def load_and_structure_survey_csv(file_path: str) -> pd.DataFrame:
    """
    Loads a survey CSV file with multi-level headers, structures the data, 
    and renames the columns for easier analysis.

    Parameters
    ----------
    file_path : str
        Path to the CSV file containing the survey responses.

    Returns
    -------
    pd.DataFrame
        A structured DataFrame with renamed columns where question and option
        information are combined into a single column name. The participant 
        ID column is renamed to 'participant_id'.
    
    Notes
    -----
    - Assumes the CSV file contains two header rows.
    - Columns with 'Unnamed' in the second header row are treated as single-
      choice questions or options without explicit labels.
    """
    # Read the file, loading the first two rows as headers
    df = pd.read_csv(file_path, header=[0, 1])
    
    # Prepare new column names by combining question and option, excluding 'Unnamed'
    new_columns = []
    current_question = None  # Track the last question seen

    for col in df.columns:
        question, option = col
        
        if "Question" in question:
            # New question encountered; reset tracking
            current_question = question
            new_column_name = f"{current_question}_{option}" if "Unnamed" not in option else current_question
        else:
            # For unnamed columns, append as options to the current question
            new_column_name = f"{current_question}_{option}" if current_question else f"Unnamed_{option}"
        
        # Append to the new columns list
        new_columns.append(new_column_name)

    # Rename columns in the DataFrame
    df.columns = new_columns
    
    # Rename the participant ID column (assumed to be the first column)
    df.rename(columns={df.columns[0]: 'participant_id'}, inplace=True)
    
    return df

def apply_metadata_mapping(df: pd.DataFrame,
                           questions_map: Dict[str, str],
                           options_map: Dict[str, Dict[str, str]]
                           ) -> pd.DataFrame:
    """
    Applies metadata mappings to the DataFrame columns to replace question and 
    option identifiers with descriptive text.

    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame containing survey responses with column names in the 
        format 'Question_X_Option_Y'.
    questions_map : Dict[str, str]
        A dictionary mapping question identifiers (e.g., 'Question 3') to 
        descriptive question text.
    options_map : Dict[str, Dict[str, str]]
        A nested dictionary mapping question identifiers to option mappings,
        where each option is mapped to descriptive text.

    Returns
    -------
    pd.DataFrame
        The DataFrame with updated column names that include descriptive 
        question and option text.

    Notes
    -----
    - Columns 'participant_id' and 'survey_type' are preserved without changes.
    - If an option label is unavailable, only the question text is used in 
      the column name.
    - Assumes column names are in the format 'Question_X_Option_Y' or 
      'Question_X' for single-choice questions.
    """
    new_columns = []
    
    for col in df.columns:
        # Skip participant ID and survey type columns
        if col == 'participant_id' or col == 'survey_type':
            new_columns.append(col)
            continue

        # Parse the question and option from the column name
        parts = col.split('_')
        question_label = f"{parts[0]} {parts[1]}"  # e.g., 'Question 3'
        option_label = parts[2] if len(parts) > 2 else None  # e.g., 'Option 1'

        # Map the question label to the actual question text
        question_text = questions_map.get(question_label, question_label)

        # Map the option label if available
        if option_label and question_label in options_map:
            option_text = options_map[question_label].get(option_label, option_label)
            new_column_name = f"{question_text} - {option_text}"
        else:
            new_column_name = question_text  # No option text, single-choice question
        
        new_columns.append(new_column_name)
    
    # Update DataFrame columns
    df.columns = new_columns
    return df


def parse_survey_metadata(metadata_path: str
                          ) -> Tuple[Dict[str, str],
                                     Dict[str, Dict[str, str]]]:
    """
    Parses an XML metadata file to extract survey questions and their 
    corresponding answer options.

    Parameters
    ----------
    metadata_path : str
        The file path to the XML metadata file.

    Returns
    -------
    Tuple[Dict[str, str], Dict[str, Dict[str, str]]]
        A tuple containing two dictionaries:
        - metadata_questions: Maps question identifiers (e.g., 'Question 1') to 
          their text descriptions.
        - metadata_options: Maps question identifiers to dictionaries of 
          option identifiers (e.g., 'Option 1') and their text descriptions.

    Notes
    -----
    - Assumes the XML structure has 'Survey_Question' sections, each containing 
      'Question' elements with optional 'Answer' elements for answer options.
    - If a question or answer has no text, it is labeled as "No text provided".
    - Questions without options are excluded from the `metadata_options` dictionary.
    """
    # Parse the XML file
    tree = ET.parse(metadata_path)
    root = tree.getroot()

    # Initialize dictionaries to store the questions and options
    metadata_questions = {}
    metadata_options = {}

    # Iterate over the XML to extract question numbers and texts
    for section in root.findall('.//Survey_Question'):
        for question in section.findall('.//Question'):
            # Extract question number and text
            question_num = question.attrib.get('num')
            question_text_elem = question.find('question')
            question_text = (
                question_text_elem.text.strip() if question_text_elem is not None else "No text provided"
            )

            # Add question number and text to metadata_questions dictionary
            metadata_questions[f"Question {question_num}"] = question_text

            # Process each answer option for the question
            options = {}
            for answer in question.findall('.//Answer'):
                option_num = answer.attrib.get('num')
                option_text = (
                    answer.text.strip() if answer.text is not None else "No text provided"
                )
                options[f"Option {option_num}"] = option_text

            # Only add to metadata_options if options exist for the question
            if options:
                metadata_options[f"Question {question_num}"] = options

    return metadata_questions, metadata_options

##################################
#
# QUESTION PARSING
#
##################################

def split_by_question(df: pd.DataFrame,
                      question_prefix: str
                      ) -> pd.DataFrame:
    """
    Filters the dataframe to include only columns related to a specific question prefix.
    
    Parameters
    ----------
    df : pd.DataFrame
        The original dataframe containing multiple questions and participant data.
    question_prefix : str
        The prefix for the question columns (e.g., 'Question 3').
    
    Returns
    -------
    pd.DataFrame
        A dataframe containing only the columns related to the specified question prefix,
        along with `participant_id` and `survey_type` columns.
    """
    # Filter columns where the full question prefix matches
    question_columns = [col for col in df.columns if col.startswith(f"{question_prefix} ")]
    # Include participant_id and survey_type for context
    question_columns = ['participant_id', 'survey_type'] + question_columns
    # Create and return the subset dataframe
    return df[question_columns]

def split_all_questions(df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    """
    Splits the dataframe into separate dataframes for each question prefix.
    
    Parameters
    ----------
    df : pd.DataFrame
        The original dataframe containing participant responses for multiple questions.
    
    Returns
    -------
    Dict[str, pd.DataFrame]
        A dictionary where each key is a question prefix (e.g., 'Question 3'),
        and each value is a dataframe containing only the columns for that question.
    """
    # Extract unique question prefixes (e.g., 'Question 2', 'Question 3', etc.)
    question_prefixes = sorted(set(col.split(' Option')[0] for col in df.columns if col.startswith('Question')))
    # Create a dictionary of dataframes
    question_dataframes = {prefix: split_by_question(df, prefix) for prefix in question_prefixes}
    return question_dataframes


def rename_option_columns(question_dataframe: pd.DataFrame, 
                          question_options: pd.DataFrame
                          ) -> pd.DataFrame:
    """
    Rename columns in a question-specific dataframe based on the question options.

    Parameters
    ----------
    question_dataframe : pd.DataFrame
        The dataframe containing survey responses for a specific question.
        Column names include options like 'Question X Option 1'.
    question_options : pd.DataFrame
        A dataframe where each column corresponds to a question and
        contains the available options as rows.

    Returns
    -------
    pd.DataFrame
        A dataframe with renamed columns, replacing option placeholders
        with descriptive option names.
    """
    # Extract the question number from the dataframe columns
    question_identifier = [
        col for col in question_dataframe.columns if "Question" in col
    ][0].split("Option")[0].strip()

    # Check if the question exists in the question_options dataframe
    if question_identifier in question_options.columns:
        # Get the options for the question
        options = question_options[question_identifier].dropna().to_list()
        
        # Build a mapping of old column names to new descriptive names
        column_mapping = {
            f"{question_identifier} Option {i+1}": option
            for i, option in enumerate(options)
        }

        # Rename the columns in the dataframe
        renamed_dataframe = question_dataframe.rename(columns=column_mapping)
        return renamed_dataframe

    # Return original dataframe if no relevant options are found
    return question_dataframe


def collapse_binary_columns_to_single(df: pd.DataFrame,
                                      new_column_name: str
                                      ) -> pd.DataFrame:
    """
    Collapse binary columns into a single column with their titles as values.

    Parameters
    ----------
    df : pd.DataFrame
        The input dataframe containing binary columns.
    new_column_name : str
        Name of the new single column where binary column titles will be stored.

    Returns
    -------
    pd.DataFrame
        Dataframe with binary columns replaced by a single column containing
        their respective titles as values.
    """
    # Identify binary columns (columns with only 0 and 1 values)
    binary_columns = [
        column for column in df.columns
        if df[column].dropna().isin([0, 1]).all()
    ]
    
    # Ensure binary columns are correctly formatted
    collapsed_df = df.copy()

    # Create the new single column based on binary columns
    collapsed_df[new_column_name] = collapsed_df[binary_columns]\
        .idxmax(axis=1)  # idxmax gets the column name with max value (1)
    
    # Handle rows where no binary column is 1 (e.g., all 0s)
    collapsed_df.loc[
        collapsed_df[binary_columns].sum(axis=1) == 0, new_column_name
    ] = None

    # Drop the original binary columns
    collapsed_df = collapsed_df.drop(columns=binary_columns)

    return collapsed_df

def process_survey_data(
    df: pd.DataFrame,
    question_options: pd.DataFrame,
    question_to_column_name_mapping: Dict[str, str] = QUESTION_COL_NAME_MAP
    ) -> Dict[str, pd.DataFrame]:
    """
    Processes the survey dataframe by splitting it by question, renaming option
    columns, collapsing binary columns into a single column, and renaming the
    final column using the provided mapping.

    Parameters
    ----------
    df : pd.DataFrame
        The original dataframe containing participant responses for multiple
        questions.
    question_to_column_name_mapping : Dict[str, str]
        A mapping from question prefixes (e.g., 'Question 2') to the desired
        column names.
    question_options : pd.DataFrame
        Dataframe mapping question codes to option texts.

    Returns
    -------
    Dict[str, pd.DataFrame]
        A dictionary where each key is a question prefix, and each value is a
        processed dataframe for that question.
    """
    # Extract unique question prefixes
    question_prefixes = sorted(set(
        col.split(' ')[0] for col in df.columns if col.startswith('Question')
    ))

    processed_dataframes = {}
    
    for question_prefix in question_prefixes:
        # Split the dataframe by question
        question_df = split_by_question(df, question_prefix)
        
        # Rename option columns using question_options
        renamed_question_df = rename_option_columns(question_df, question_options)
        
        # Collapse binary columns into a single column if applicable
        if question_prefix in question_to_column_name_mapping:
            new_column_name = question_to_column_name_mapping[question_prefix]
            final_question_df = collapse_binary_columns_to_single(
                renamed_question_df, new_column_name
            )
        else:
            final_question_df = renamed_question_df
        
        # Add processed dataframe to the dictionary
        processed_dataframes[question_prefix] = final_question_df
    
    return processed_dataframes