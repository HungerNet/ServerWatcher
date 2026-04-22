def validateAll(panel, server):
    """
    Validate panel connectivity, API access, and server running state.
    """
    return (
        panel.ping() is True and
        panel.validateAPI() is True and
        server.getStatus() == "running"
    )