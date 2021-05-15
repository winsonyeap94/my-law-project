import numpy as np
import pandas as pd
from numpy import pi, sin, cos
import plotly.graph_objs as go


def viz_warehouse_selection(
    warehouses_df, townships_df, selected_warehouses_df, warehouse_township_assignment_df
):

    # ========== Data Pre-Processing ==========
    warehouses_df = warehouses_df.copy()
    warehouses_df = warehouses_df.merge(selected_warehouses_df[['Name', 'Selected']], how='outer', 
                                        left_on='Warehouse Location', right_on='Name')
    warehouse_township_assignment_df = warehouse_township_assignment_df.copy()
    warehouse_township_assignment_df = warehouse_township_assignment_df.rename(columns={'Unnamed: 0': 'Township'})\
        .set_index('Township').transpose().reset_index(drop=False)
    long_assignment_df = \
        pd.melt(warehouse_township_assignment_df, id_vars='index', value_name='Volume')\
        .rename(columns={'index': 'Warehouse'})
    long_assignment_df = long_assignment_df.query("Volume > 0")
    long_assignment_df = long_assignment_df.merge(
        warehouses_df[['Warehouse Location', 'Latitude', 'Longitude']], how='left',
        left_on='Warehouse', right_on='Warehouse Location'
    ).rename(columns={'Latitude': 'Start Latitude', 'Longitude': 'Start Longitude'})
    long_assignment_df = long_assignment_df.merge(
        townships_df[['Township', 'Latitude', 'Longitude']], how='left', left_on='Township', right_on='Township'
    ).rename(columns={'Latitude': 'End Latitude', 'Longitude': 'End Longitude'})

    # ========== Main Viz ==========
    fig = go.Figure()

    # Adding Warehouse Location markers
    fig.add_trace(go.Scattermapbox(
        name='Warehouse Locations',
        lat=warehouses_df['Latitude'],
        lon=warehouses_df['Longitude'],
        text="<b>" + warehouses_df['Warehouse Location'] + "</b><br>Capacity: " +
             warehouses_df['Area (sqft)'].map(lambda x: '{:,.0f}'.format(x)) + " sqft <br>Monthly Cost: RM " +
             warehouses_df['Cost (RM/month)'].map(lambda x: '{:,.2f}'.format(x)) + " /month",
        marker=go.scattermapbox.Marker(
            size=15, color='#00A19C', opacity=0.75, allowoverlap=True
        ),
        hovertemplate="%{text}"
    ))

    # Adding Township Location markers
    fig.add_trace(go.Scattermapbox(
        name='Townships',
        lat=townships_df['Latitude'],
        lon=townships_df['Longitude'],
        text="<b>" + townships_df['Township'] + "</b><br>Demand: " +
             townships_df['Demand'].map(lambda x: '{:,.0f}'.format(x)),
        marker=go.scattermapbox.Marker(
            size=10, color='#FF8C00', opacity=0.75, allowoverlap=True
        ),
        hovertemplate="%{text}"
    ))

    # Adding Path (Staff Lines)

    lons = np.empty(3 * len(long_assignment_df))
    lons[::3] = long_assignment_df['Start Longitude']
    lons[1::3] = long_assignment_df['End Longitude']
    lons[2::3] = None
    lats = np.empty(3 * len(long_assignment_df))
    lats[::3] = long_assignment_df['Start Latitude']
    lats[1::3] = long_assignment_df['End Latitude']
    lats[2::3] = None

    fig.add_trace(go.Scattermapbox(
        name='Path',
        lon=lons,
        lat=lats,
        mode='lines',
        line=dict(width=1, color='red'),
        opacity=0.5,
        hoverinfo='skip'
    ))

    # layers_list = []
    # for i in range(len(work_location_df)):
    #
    #     adj_radius = radius / 111
    #     center_lat = work_location_df['latitude'][i]
    #     center_lon = work_location_df['longitude'][i]
    #     t = np.linspace(0, 2 * pi, 100)
    #     circle_lon = center_lon + adj_radius * cos(t)
    #     circle_lat = center_lat + adj_radius * sin(t)
    #
    #     coords = []
    #     for lo, la in zip(list(circle_lon), list(circle_lat)):
    #         coords.append([lo, la])
    #
    #     layers = [
    #         dict(sourcetype='geojson',
    #              source={"type": "Feature",
    #                      "geometry": {"type": "LineString",
    #                                   "coordinates": coords}},
    #              color='#00A19C',
    #              type='fill',
    #              opacity=0.2,
    #              line=dict(width=1.5)
    #              )
    #     ]
    #
    #     layers_list += layers

    # Adding Map Layout
    fig.update_layout(
        mapbox=dict(
            style='open-street-map',
            center=dict(lat=3, lon=101.6),
            # layers=layers_list,
            bearing=0,
            pitch=0,
            zoom=9,
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        margin=dict(
            l=0, r=0, t=0, b=0, pad=0
        )
    )

    return fig


if __name__ == '__main__':

    import plotly.io as pio
    pio.renderers.default = "browser"

    from src.optimisation_model.input_handler import InputHandler
    warehouses_df = InputHandler.get_warehouse_options()
    townships_df = InputHandler.get_districts_data()

    from conf import Config
    from pathlib import Path
    from src.data_connectors import PandasFileConnector
    selected_warehouses_df = PandasFileConnector.load(Path(Config.FILES['MODEL_OUTPUT'], "Warehouse Selection.csv"))
    warehouse_township_assignment_df = PandasFileConnector.load(Path(Config.FILES['MODEL_OUTPUT'], "Warehouse Township Assignment.csv"))

    fig = viz_warehouse_selection(warehouses_df, townships_df, selected_warehouses_df, warehouse_township_assignment_df)
    fig.show()


