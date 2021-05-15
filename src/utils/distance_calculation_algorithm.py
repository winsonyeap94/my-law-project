import numpy as np
import pandas as pd
from conf import Logger
from haversine import haversine
from scipy.spatial.distance import squareform, pdist

_logger = Logger


def calculate_lat_long_distance(data, radius=None):

    # store the original data into df
    df = data.copy()

    # select column name, latitude and longitude from dataset
    data = data[['name', 'latitude', 'longitude']]
    
    # set the dataset index using existing columns
    data.set_index('name', inplace=True)
    
    # create a matrix distance
    dm = pd.DataFrame(squareform(pdist(data, metric=haversine)), index=data.index, columns=data.index)
    
    # fill diagonal elements on matrix with infinity, so that the diagonal elements do not be one of the candidates
    # of selection
    np.fill_diagonal(dm.values, np.inf)  # Makes it easier to find minimums
    
    # group all elements of location in a group called "Locations"
    Locations = data[~data.index.str.startswith('staff')].copy()
    
    # group all elements of staff in a group called "Staffs"
    Staffs = data[data.index.str.startswith('staff')].copy()
    
    # Find the closest location between each staff and each location
    Staffs['Assigned Location'] = dm.loc[Locations.index, Staffs.index].idxmin()
    
    # Find the distance of the respective closest location between each staff and each location
    Staffs['Distance in KM'] = dm.loc[Locations.index, Staffs.index].min()

    # Filtering based on Radius
    if radius is not None:
        Staffs.loc[Staffs['Distance in KM'] > radius, 'Assigned Location'] = 'Unassigned'
    _logger.info(f"[distance_calculation] {(Staffs['Assigned Location'] == 'Unassigned').sum():.0f} staffs are "
                 f"Unassigned with radius of {radius}.")

    # create a dataframe with name, postal code, latitude. longitude, closest location, and distance (km)
    df_name_postal_code = df[[x for x in df.columns if x not in Staffs.columns]]
    concat_data = pd.concat([df_name_postal_code.reset_index(drop=True), Staffs.reset_index(drop=True)], axis=1)
    concat_data = concat_data.dropna(subset=['latitude'])
    
    return concat_data









