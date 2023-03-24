# spatial-indexes
Spatial indexes to maps and geodata @ UBC Library

## What does the included script do?
The 'geojsons_data_cleaning_OIM_spec' file is a Python-language Jupyter Notebook script which cleans and normalizes metadata in accordance with the Open Index Map (OIM) specification: https://openindexmaps.org/specification/1.0.0. These metadata come from a set of manually-created map-inventory spreadsheets, which are combined with digital map indexes to produce GeoJSON files. (See more at https://github.com/ubc-lib-geo/creating-index-maps.)

This script:
- Imports all GeoJSON files within each continent/region subdirectory in the 'spatial-indexes' repository of the 'ubc-lib-geo' GitHub organization: https://github.com/ubc-lib-geo/spatial-indexes
- Combines all files into a single object (a GeoPandas GeoDataFrame)
- Compares the column labels (element titles) against the OIM specification
    - These element titles were input into a spreadsheet and then imported into this script
    - For instances where the element title does not match the OIM specification *and* there exists a corresponding field to map the data to (e.g., 'notes' and 'note' fields)--meaning the relevant data is split between more than one column--data is transferred from the non-matching field to the OIM-compliant field
        - After completing this, all non-compliant fields are removed
    - For instances where the element title does not match the OIM specification, *but* all relevant data is located in that single column, the column label is changed to match the element title in the OIM specification
    - For instances where the element title not only does not match the OIM specification, *but* no corresponding element title exists within the specification (e.g., 'editionNotes'), data will be mapped to another selected field (e.g., 'edition' or 'note')
        - If data already exists in the selected field (e.g., 'edition' or 'note'), the data from the no-equivalent field (e.g., 'editionNotes') will be appended to it using the separator '; '
- Removes any extra white space at the beginning and end of all values
- For fields with an OIM-specified data type of boolean (i.e., 'available', 'contLines', 'bathLines'), existing values are mapped to the form 'true' or 'false', as outlined in the OIM specification
    - Files containing null values in these fields are identified
    - With the exception of the 'available' field, null values are left as null values (i.e., they are not converted to either 'true' or 'false')
- The combined data is separated into individual GeoJSONs and written-out as individual files to their respective continent/region subdirectory in the 'spatial-indexes' repository
    - Files' original names are maintained
    - Fields containing only null values within an individual file are removed before being written-out

### Requirements to run script
#### Jupyter Notebook

#### Virtual environment

## GitHub workflow: Integration with Dataverse