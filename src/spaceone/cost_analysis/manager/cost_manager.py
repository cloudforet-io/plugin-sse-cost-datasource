import logging
from datetime import datetime

from spaceone.core import utils
from spaceone.core.manager import BaseManager
from spaceone.cost_analysis.error import *
from spaceone.cost_analysis.connector.sse_billing_connector import SSEBillingConnector
from spaceone.cost_analysis.model.cost_model import Cost

_LOGGER = logging.getLogger(__name__)


class CostManager(BaseManager):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sse_connector: SSEBillingConnector = self.locator.get_connector('SSEBillingConnector')

    def get_data(self, options, secret_data, schema, task_options):
        self.sse_connector.create_session(options, secret_data, schema)
        self._check_task_options(task_options)

        billing_year = task_options['billing_year']
        billing_month = task_options['billing_month']

        signed_urls = self.sse_connector.get_download_urls(billing_year, billing_month)
        if len(signed_urls) > 0:
            for signed_url in signed_urls:
                response_stream = self.sse_connector.get_cost_data(signed_url)
                for results in response_stream:
                    yield self._make_cost_data(results)
        else:
            yield []

    @staticmethod
    def _make_cost_data(results):
        costs_data = []

        for result in results:
            data = {
                'cost': result['resource_cost'],
                'provider': result['infra_type'],
                'region_code': result.get('product_region'),
                'product': result.get('product_name'),
                'account': str(result['account_id']),
                'resource': result.get('resource_id'),
                'billed_at': datetime.strptime(result['usage_date'], '%Y-%m-%d'),
                'additional_info': {}
            }

            if 'currency' in result:
                data['currency'] = result['currency']

            if 'category_name' in result:
                data['additional_info']['category_name'] = result['category_name']

            if 'service_id' in result:
                data['additional_info']['service_id'] = result['service_id']

            cost_data = Cost(data)
            cost_data.validate()

            costs_data.append(cost_data.to_primitive())

        return costs_data

    @staticmethod
    def _check_task_options(task_options):
        if 'billing_year' not in task_options:
            raise ERROR_REQUIRED_PARAMETER(key='task_options.billing_year')

        if 'billing_month' not in task_options:
            raise ERROR_REQUIRED_PARAMETER(key='task_options.billing_month')
