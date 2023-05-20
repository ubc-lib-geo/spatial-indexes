# %%
# # Install pandas and geopandas libraries, if required
# ! pip install pandas, geopandas

# %%
# Import required libraries
import os
import pickle
import pandas as pd
import geopandas as gpd

# %%
# Define list with element names from OIM specification
oim_specification_element_names = [
    'available',
    'bathInterv',
    'bathLines',
    'color',
    'contInterv',
    'contLines',
    'date',
    'datePhoto',
    'datePub',
    'dateReprnt',
    'dateSurvey',
    'digHold',
    'download',
    'edition',
    'fileName',
    'geometry',
    'iiifUrl',
    'inst',
    'instCallNo',
    'label',
    'labelAlt',
    'labelAlt2',
    'lcCallNo',
    'location',
    'note',
    'overlays',
    'overprint',
    'physHold',
    'primeMer',
    'projection',
    'publisher',
    'recId',
    'scale',
    'sheetId',
    'thumbUrl',
    'title',
    'titleAlt',
    'websiteUrl'
 ]

# %%
# This list contains fields with a boolean data type, and is used later to check whether these fields contain null values
# Update, as needed
boolean_field_names = [
    'available',
    'bathInterv',
    'contInterv'
]

# %%
# Define mapping for incorrect element names
# These key-value pairs represent incorrect title names encountered to date; they are not exhaustive
# Add pairs, as they arise, to incorporate into script for future executions
# Incorrect names are on the left (dictionary keys); correct names are on the right (dictionary values)
element_name_mappings = dict(
    # incorrectName = 'correctName'
    notes = 'note',
    lcCall = 'lcCallNo',
    instCall = 'instCallNo',
    iiifURL = 'iiifUrl',
    year = 'date',
    sheetID = 'sheetId',
    digHolding = 'digHold',
    avaliable = 'available',
    contInt = 'contInterv',
    bathInt ='bathInterv',
    dateReprint = 'dateReprnt',
    editionNotes = 'note_ed' # This is a temporary name that is needed to differentiate the field from the 'note' field to combine the two later
)

# %%
# Define function for reading GeoJSON file
# Returns a GeoDataFrame
def read_geojson_file(geojson_file):
    return gpd.read_file(geojson_file)

# %%
# Define function to replace default null values (np.nan) with pd.NA
# Changes dtype of columns with nulls from 'float' to 'object'
# Assists with string operations for entire dataframe (e.g., removing white space)
def fill_nulls_with_pandas_NA(geodataframe):
    return geodataframe.fillna(pd.NA)

# %%
# Define function that returns element names that do not match OIM specification
def get_incorrect_element_names(geodataframe):
    element_names_matching_specification = pd.Series(geodataframe.columns).isin(oim_specification_element_names)
    return pd.Series(geodataframe.columns)[~element_names_matching_specification]

# %%
# Define function that returns incorrect element names not already included in the element_name_mappings dictionary
def incorrect_element_names_unaccounted_for(series):
    element_names_accounted_for = series.isin(element_name_mappings.keys())
    return series[~element_names_accounted_for]

# %%
# Define function which returns incorrect element names not already included in element_name_mappings dictionary
# and asks the user to input correct names
# These incorrect name: correct name key-value pairs are added to the element_name_mappings dictionary
def update_element_name_mappings_dictionary(series_of_element_names_unaccounted_for, dictionary_mapping):
    if len(series_of_element_names_unaccounted_for) > 0:
        for element in series_of_element_names_unaccounted_for:
            user_inputted_element_name = input(f'\nThe following element name does not match the OIM specification:\n\n{element}\n\nWhat would you like to replace it with? ')
            dictionary_mapping[element] = user_inputted_element_name
        with open(os.path.join(os.path.dirname(os.getcwd()), 'element_name_mappings_python_dictionary.txt'), 'wb') as file:
            pickle.dump(dictionary_mapping, file)
        with open(os.path.join(os.path.dirname(os.getcwd()), 'element_name_mappings_python_dictionary.txt'), 'rb') as file:
            dictionary_mapping = pickle.load(file)
        return dictionary_mapping
    return dictionary_mapping

# %%
# Define function that replaces incorrect element names with correct ones
def replace_incorrect_element_names(geodataframe, dictionary_mapping):
    geodataframe.columns = [dictionary_mapping[element_name] if element_name in dictionary_mapping.keys() else element_name for element_name in geodataframe.columns]
    return geodataframe

# %%
# Define function which handles 'note' fields
def handle_note_fields(geodataframe):
    if 'note' in geodataframe.columns and 'note_ed' in geodataframe.columns:
        geodataframe['note'] = geodataframe['note'].fillna('') + '; ' + geodataframe['note_ed'].fillna('')
        geodataframe['note'] = geodataframe['note'].str.strip('; ')
        geodataframe['note'] = geodataframe['note'].replace('', pd.NA)
        geodataframe = geodataframe.drop(columns = 'note_ed')
    elif 'note' not in geodataframe.columns and 'note_ed' in geodataframe.columns:
        geodataframe = geodataframe.rename(columns = {'note_ed': 'note'})
    return geodataframe

# %%
# Define function to combine values of duplicate fields into single field
def combine_values_of_fields_with_same_name(geodataframe):
    boolean_series_of_fields_with_multiple_columns = pd.Series(geodataframe.columns).value_counts() > 1
    fields_with_multiple_columns = boolean_series_of_fields_with_multiple_columns[boolean_series_of_fields_with_multiple_columns].index
    for name in fields_with_multiple_columns:
        multiple_columns_df = geodataframe[name]
        multiple_columns_df.columns = list(range(0, len(geodataframe[name].columns)))
        multiple_columns_df = multiple_columns_df.apply(lambda x: x.fillna(''))
        combined_column = multiple_columns_df.apply(lambda row: ''.join(row.values.astype(str)), axis = 1)
        combined_column = combined_column.replace('', pd.NA)
        geodataframe = geodataframe.drop(columns = name)
        geodataframe[name] = combined_column
    return geodataframe

# %%
# Define function to check whether boolean fields contain null values
def nulls_in_boolean_fields(geodataframe, file_name):
    for field_name in boolean_field_names:
        if field_name in geodataframe.columns and geodataframe[field_name].isnull().any():
            user_input = input(f"\nThe following boolean field in {file_name} contains null values:\n\n{field_name}\n\nWould you like to convert these to 'false'? ('y' or 'n'; 'n' will leave values as null) ").lower()
            if user_input in ['y', 'yes']:
                geodataframe[field_name] = geodataframe[field_name].fillna('false')
            elif user_input in ['n', 'no']:
                geodataframe[field_name] = geodataframe[field_name]
            else:
                second_input = input("\nYou entered an invalid option. Please enter either 'y' for 'yes' or 'n' for 'no'. ")
                if second_input in ['y', 'yes']:
                    geodataframe[field_name] = geodataframe[field_name].fillna('false')
                else:
                    geodataframe[field_name] = geodataframe[field_name]
    return geodataframe

# %%
# Define function to convert values of boolean fields to 'true'/'false' strings
def convert_boolean_values_to_true_false_strings(geodataframe):
    for field_name in boolean_field_names:
        if field_name in geodataframe.columns:
            geodataframe[field_name] = geodataframe[field_name].astype('string').str.lower()
    return geodataframe

# %%
# Define function to remove extra white space
def remove_extra_white_space(geodataframe):
    return geodataframe.applymap(lambda x: x.strip() if isinstance(x, str) else x)

# %%
# Define function to remove invalid data structures (e.g., lists)
# This is necessary for geopandas to write to GeoJSON
def remove_invalid_data_structures(geodataframe):
    for field_name in geodataframe.columns:
        if geodataframe[field_name].apply(lambda x: isinstance(x, list)).any():
            geodataframe = geodataframe.explode(field_name)
    return geodataframe

# %%
# Define function to write processed GeoJSON file back to original directory
def write_geojson_file(geodataframe, file_name):
    geodataframe = geodataframe.set_geometry(col = 'geometry')
    geodataframe.to_file(file_name, driver = 'GeoJSON')
    return print(f'Writing {file_name}')

# %%
# Apply functions to process GeoJSONs within all directories
list_of_continent_directories = [item for item in os.listdir() if '.' not in item]

for directory in list_of_continent_directories:
    os.chdir(directory)
    for file in os.listdir():
        if file.endswith('.geojson'):
            print(f'Processing {file}')
            gdf = read_geojson_file(file)
            gdf = fill_nulls_with_pandas_NA(gdf)
            incorrect_element_names = get_incorrect_element_names(gdf)
            element_names_unaccounted_for = incorrect_element_names_unaccounted_for(incorrect_element_names)
            element_name_mappings = update_element_name_mappings_dictionary(element_names_unaccounted_for, element_name_mappings)
            gdf = replace_incorrect_element_names(gdf, element_name_mappings)
            gdf = handle_note_fields(gdf)
            gdf = combine_values_of_fields_with_same_name(gdf)
            gdf = nulls_in_boolean_fields(gdf, file)
            gdf = convert_boolean_values_to_true_false_strings(gdf)
            gdf = remove_extra_white_space(gdf)
            gdf = remove_invalid_data_structures(gdf)
            write_geojson_file(gdf, file)
    os.chdir('..')

print('\nPROCESSING COMPLETE')


