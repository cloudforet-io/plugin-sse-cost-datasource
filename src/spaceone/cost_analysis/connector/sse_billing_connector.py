import logging
import time
import requests
import pandas as pd
import numpy as np
from io import StringIO
import zlib

from datetime import datetime
from spaceone.core import utils
from spaceone.core.transaction import Transaction
from spaceone.core.connector import BaseConnector
from typing import List

from spaceone.cost_analysis.error import *

__all__ = ['SSEBillingConnector']

_LOGGER = logging.getLogger(__name__)

_DEFAULT_HEADERS = {
    'Content-Type': 'application/json',
    'accept': 'application/json'
}
_PAGE_SIZE = 1000


class SSEBillingConnector(BaseConnector):

    def __init__(self, transaction: Transaction, config: dict):
        super().__init__(transaction, config)
        self.endpoint = None
        self.headers = _DEFAULT_HEADERS

    def create_session(self, options: dict, secret_data: dict, schema: str = None) -> None:
        self._check_secret_data(secret_data)

        self.headers['cid'] = secret_data['cid']
        self.headers['secret'] = secret_data['secret']
        self.endpoint = secret_data['endpoint']

    @staticmethod
    def _check_secret_data(secret_data: dict) -> None:
        if 'cid' not in secret_data:
            raise ERROR_REQUIRED_PARAMETER(key='secret_data.cid')

        if 'secret' not in secret_data:
            raise ERROR_REQUIRED_PARAMETER(key='secret_data.secret')

        if 'endpoint' not in secret_data:
            raise ERROR_REQUIRED_PARAMETER(key='secret_data.endpoint')

    def get_change_dates(self, start: datetime = None, last_synchronized_at: datetime = None) -> List[dict]:
        url = f'{self.endpoint}/v1/cost/change_date'

        if start:
            last_sync_time = time.mktime(start.timetuple())
        elif last_synchronized_at:
            last_sync_time = time.mktime(last_synchronized_at.timetuple())
        else:
            last_sync_time = 0

        data = {
            'last_sync_timestamp': last_sync_time
        }

        _LOGGER.debug(f'[get_change_dates] {url} => {data}')

        response = requests.post(url, json=data, headers=self.headers)

        if response.status_code == 200:
            return response.json().get('results', [])
        else:
            raise ERROR_CONNECTOR_CALL_API(reason=response.json())

    def get_download_urls(self, billing_year: int, billing_month: int, granularity: str = 'DAILY') -> List[str]:
        url = f'{self.endpoint}/v1/cost/summary/download'

        data = {
            'billing_year': billing_year,
            'billing_month': billing_month,
            'granularity': granularity
        }

        _LOGGER.debug(f'[get_download_urls] {url} => {data}')

        response = requests.post(url, json=data, headers=self.headers)
        if response.status_code == 200:
            return response.json().get('signed_urls', [])
        else:
            raise ERROR_CONNECTOR_CALL_API(reason=response.json())

    def get_cost_data(self, signed_url):
        _LOGGER.debug(f'[get_cost_data] download url: {signed_url}')

        cost_csv = self._download_cost_data(signed_url)
        df = pd.read_csv(StringIO(cost_csv))
        df = df.replace({np.nan: None})

        costs_data = df.to_dict('records')

        # Paginate
        page_count = int(len(costs_data) / _PAGE_SIZE) + 1

        for page_num in range(page_count):
            offset = _PAGE_SIZE * page_num
            yield costs_data[offset:offset + _PAGE_SIZE]

    @staticmethod
    def _download_cost_data(signed_url: str) -> str:
        response = requests.get(signed_url)
        cost_bytes = zlib.decompress(response.content, zlib.MAX_WBITS | 32)
        return cost_bytes.decode('utf-8')
