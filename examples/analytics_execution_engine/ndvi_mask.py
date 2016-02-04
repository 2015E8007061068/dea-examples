# ------------------------------------------------------------------------------
# Name:       ndvi_mask.py
# Purpose:    ndvi mask example for Analytics Engine & Execution Engine.
#             pre-integration with NDExpr.
#             post-integration with Data Access API.
#
# Author:     Peter Wang
#
# Created:    22 December 2015
# Copyright:  2015 Commonwealth Scientific and Industrial Research Organisation
#             (CSIRO)
# License:    This software is open source under the Apache v2.0 License
#             as provided in the accompanying LICENSE file or available from
#             https://github.com/data-cube/agdc-v2/blob/master/LICENSE
#             By continuing, you acknowledge that you have read and you accept
#             and will abide by the terms of the License.
#
# ------------------------------------------------------------------------------

from __future__ import absolute_import
from __future__ import print_function

if __name__ == '__main__' and __package__ is None:
    from os import sys, path
    sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))

from pprint import pprint
from datetime import datetime
from datacube.analytics.analytics_engine import AnalyticsEngine
from datacube.execution.execution_engine import ExecutionEngine
from datacube.analytics.utils.analytics_utils import plot

from glue.core import Data, DataCollection
from glue.qt.glue_application import GlueApplication


def main():
    a = AnalyticsEngine()
    e = ExecutionEngine()

    # Lake Burley Griffin
    dimensions = {'longitude': {'range': (149.07, 149.18)},
                  'latitude':  {'range': (-35.32, -35.28)},
                  'time':      {'range': (datetime(1990, 1, 1), datetime(1990, 12, 31))}}

    arrays = a.create_array(('LANDSAT 5', 'NBAR'), ['band_40', 'band_30'], dimensions, 'get_data')
    ndvi = a.apply_bandmath(arrays, '((array1 - array2) / (array1 + array2))', 'ndvi')
    pq = a.create_array(('LANDSAT 5', 'PQ'), ['band_pixelquality'], dimensions, 'pq')
    mask = a.apply_cloud_mask(ndvi, pq, 'mask')

    e.execute_plan(a.plan)

    plot(e.cache['mask'])

    b30_result = e.cache['get_data']['array_result']['band_30']
    b40_result = e.cache['get_data']['array_result']['band_40']
    ndvi_result = e.cache['ndvi']['array_result']['ndvi']
    pq_result = e.cache['pq']['array_result']['band_pixelquality']
    mask_result = e.cache['mask']['array_result']['mask']

    b30_data = Data(x=b30_result[:, ::-1, :], label='B30')
    b40_data = Data(x=b40_result[:, ::-1, :], label='B40')
    ndvi_data = Data(x=ndvi_result[:, ::-1, :], label='ndvi')
    pq_data = Data(x=pq_result[:, ::-1, :], label='pq')
    mask_data = Data(x=mask_result[:, ::-1, :], label='mask')

    long_data = Data(x=b40_result.coords['longitude'], label='long')
    lat_data = Data(x=b40_result.coords['latitude'], label='lat')
    time_data = Data(x=b40_result.coords['time'], label='time')

    collection = DataCollection([mask_data, pq_data, ndvi_data, b30_data, b40_data, long_data, lat_data, time_data, ])
    app = GlueApplication(collection)
    app.start()


if __name__ == '__main__':
    main()
