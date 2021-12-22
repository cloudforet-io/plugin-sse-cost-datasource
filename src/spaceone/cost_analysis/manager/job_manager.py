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

        _LOGGER.debug(f'[get_tasks] tasks: {results}')
        tasks = []
        changed = []
        for result in results:
            year = result['billing_year']
            month = result['billing_month']
            tasks.append({
                'task_options': {
                    'billing_year': int(year),
                    'billing_month': int(month)
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
