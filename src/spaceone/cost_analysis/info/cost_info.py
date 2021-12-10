import functools
from spaceone.api.cost_analysis.plugin import cost_pb2
from spaceone.core.pygrpc.message_type import *
from spaceone.core import utils

__all__ = ['CostInfo', 'CostsInfo']


def CostInfo(cost_data):
    info = {
        'cost_key': cost_data.get('cost_key'),
        'cost': cost_data['cost'],
        'currency': cost_data['currency'],
        'usage_quantity': cost_data.get('usage_quantity'),
        'provider': cost_data.get('provider'),
        'region_code': cost_data.get('region_code'),
        'product': cost_data.get('product'),
        'account': cost_data.get('account'),
        'instance_type': cost_data.get('instance_type'),
        'resource_group': cost_data.get('resource_group'),
        'resource': cost_data.get('resource'),
        'tags': change_struct_type(cost_data['tags']) if 'tags' in cost_data else None,
        'additional_info': change_struct_type(cost_data['additional_info']) if 'additional_info' in cost_data else None,
        'billed_at': utils.datetime_to_iso8601(cost_data['billed_at'])
    }

    return cost_pb2.CostInfo(**info)


def CostsInfo(costs_data, **kwargs):
    return cost_pb2.CostsInfo(results=list(map(functools.partial(CostInfo, **kwargs), costs_data)))
