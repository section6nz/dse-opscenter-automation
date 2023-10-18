import common
from config import OpsCenterConfiguration


# Needs to be run after cluster installation
def enable_node_sync(session_id, config: OpsCenterConfiguration):
  common.update_nodesync(
      config,
      session_id,
      "/nodesync",
      config.cluster_name,
      {
        'enable': [table.pattern for table in config.node_sync]
      })
