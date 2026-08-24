"""DAG-related exceptions."""


class DAGError(Exception):
    pass


class CycleError(DAGError):
    """DAG contains a cycle."""
    pass


class NodeNotFoundError(DAGError):
    pass
