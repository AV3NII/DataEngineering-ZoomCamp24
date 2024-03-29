import dlt
import numpy as np
import pandas as pd
from dlt.sources.helpers import requests
import time


@dlt.resource(write_disposition='replace')
def fetch_data_resource(trip_obj):
    """
    Fetch data from the source
    :param trip_obj: dict containing the type of trip as string and the years to fetch as a list
    :return: response containing the fetched data
    """
    trip_type = trip_obj['type']
    for year in trip_obj['years']:
        for month in range(1, 13):
            url = f'https://d37ci6vzurychx.cloudfront.net/trip-data/{trip_type}_tripdata_{year}-{month:02d}.parquet'
            print(f"Downloading {trip_type} trip data for {year}-{month:02d}")
            response = requests.get(url)
            response.raise_for_status()
            df = pd.read_parquet(url, engine='pyarrow')
            # in case of yellow taxi and fhv trip data, extra columns need to handled
            if trip_type == 'yellow':
                if 'airport_fee' in df.columns:
                    df['airport_fee'] = df['airport_fee'].astype(float)
                else:
                    df['airport_fee'] = np.nan
            if trip_type == 'fhv':
                if 'PUlocationID' in df.columns:
                    df['PUlocationID'] = df['PUlocationID'].astype(float)
                else:
                    df['PUlocationID'] = np.nan
                if 'DOlocationID' in df.columns:
                    df['DOlocationID'] = df['DOlocationID'].astype(float)
                else:
                    df['DOlocationID'] = np.nan
            yield df
        print(f"Downloaded {trip_type} trip data for {year}")
    print(f"Downloaded {trip_type} trip data for all years")


if __name__ == "__main__":
    # define the needed data
    needed_data = [
        {'type': 'green', 'years': [2019, 2020]},
        {'type': 'yellow', 'years': [2019, 2020]},
        {'type': 'fhv', 'years': [2019]}
    ]
    # configure the pipeline with your destination details
    start = time.time()
    for collection in needed_data:
        pipeline = dlt.pipeline(
            pipeline_name=f'tlc_{collection["type"]}_data',
            destination='filesystem',
            dataset_name=f'tlc_{collection["type"]}_data'
        )
        print(f'Running pipeline for {collection["type"]} trip data')
        run = pipeline.run(data=fetch_data_resource(collection))
        print(run)
        print(f'Pipeline for {collection["type"]} trip data completed')
        print('--')
    end = time.time()
    print('All done! in' + str(end - start) + ' seconds')