import logging
from datetime import datetime

from spaceone.core.manager import BaseManager
from spaceone.cost_analysis.error import *
from spaceone.cost_analysis.connector.sse_billing_connector import SSEBillingConnector
from spaceone.cost_analysis.model.job_model import Tasks

_LOGGER = logging.getLogger(__name__)


class JobManager(BaseManager):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sse_connector: SSEBillingConnector = self.locator.get_connector('SSEBillingConnector')

    def get_tasks(self, options, secret_data, schema, start, end, last_synchronized_at):
        self.sse_connector.create_session(options, secret_data, schema)
        results = self.sse_connector.get_change_dates(start, end, last_synchronized_at)

        if len(results) > 0:
            first_year = results[0]['billing_year']
            first_month = results[0]['billing_month']

            last_changed_at = datetime.strptime(f'{first_year}-{first_month}', '%Y-%m')

        else:
            last_changed_at = None

        tasks = []
        for result in results:
            tasks.append({
                'task_options': {
                    'billing_year': int(result['billing_year']),
                    'billing_month': int(result['billing_month'])
                }
            })

        tasks = Tasks({'tasks': tasks, 'last_changed_at': last_changed_at})
        tasks.validate()
        return tasks.to_primitive()
