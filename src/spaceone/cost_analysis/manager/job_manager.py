import logging
from datetime import datetime
from dateutil.relativedelta import relativedelta

from spaceone.core.manager import BaseManager
from spaceone.cost_analysis.error import *
from spaceone.cost_analysis.connector.sse_billing_connector import SSEBillingConnector
from spaceone.cost_analysis.model.job_model import Tasks

_LOGGER = logging.getLogger(__name__)


class JobManager(BaseManager):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sse_connector: SSEBillingConnector = self.locator.get_connector('SSEBillingConnector')

    def get_tasks(self, options, secret_data, schema, start, last_synchronized_at):
        self.sse_connector.create_session(options, secret_data, schema)
        results = self.sse_connector.get_change_dates(start, last_synchronized_at)

        _LOGGER.debug(f'[get_tasks] billing months: {results}')
        tasks = []
        changed = []
        for result in results:
            year = int(result['billing_year'])
            month = int(result['billing_month'])
            signed_urls = self.sse_connector.get_download_urls(year, month)

            for signed_url in signed_urls:
                tasks.append({
                    'task_options': {
                        'billing_year': year,
                        'billing_month': month,
                        'signed_url': signed_url
                    }
                })

            start = datetime.strptime(f'{year}-{month}', '%Y-%m')
            end = start + relativedelta(months=1)

            changed.append({
                'start': start,
                'end': end
            })

        _LOGGER.debug(f'[get_tasks] tasks: {tasks}')
        _LOGGER.debug(f'[get_tasks] changed: {changed}')

        tasks = Tasks({'tasks': tasks, 'changed': changed})

        tasks.validate()
        return tasks.to_primitive()
