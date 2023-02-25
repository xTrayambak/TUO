class AlreadyRunningServer(Exception):
    """
    Raised when the play button is clicked, but an integrated server is still running.
    """

class InvalidPacketDecodeError(Exception):
    """
    Raised when the server gives us an erroneous packet.
    """
