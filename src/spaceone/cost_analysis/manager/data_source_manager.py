import logging

from spaceone.core.manager import BaseManager
from spaceone.cost_analysis.model.data_source_model import PluginMetadata

_LOGGER = logging.getLogger(__name__)


class DataSourceManager(BaseManager):

    @staticmethod
    def init_response(options):
        plugin_metadata = PluginMetadata()
        plugin_metadata.validate()

        return {
            'metadata': plugin_metadata.to_primitive()
        }
