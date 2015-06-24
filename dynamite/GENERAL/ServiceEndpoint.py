__author__ = 'bloe'


class ServiceEndpoint:
    def __init__(self, host_ip, port):
        if port < 1 or port > 65535:
            raise ValueError("Port must be > 0 and < 65536. It was {}".format(str(port)))
        if len(host_ip) < 1:
            raise ValueError("Host IP address must be specified!")

        self.host_ip = host_ip
        self.port = port

    @classmethod
    def from_string(cls, connection_string):
        if not ":" in connection_string:
            ServiceEndpoint.raise_wrong_connection_string_error(connection_string)

        connection_string_parts = connection_string.split(":")
        if len(connection_string_parts) < 2:
            ServiceEndpoint.raise_wrong_connection_string_error(connection_string)

        host_ip = connection_string_parts[0]
        port_as_string = connection_string_parts[1]
        if not port_as_string.isdigit():
            ServiceEndpoint.raise_wrong_connection_string_error(connection_string, error_info="Port is not a number")

        port = int(port_as_string)
        return ServiceEndpoint(host_ip, port)

    @classmethod
    def raise_wrong_connection_string_error(cls, connection_string, error_info=""):
        raise ValueError("""
                Please provide a valid connection string <ip>:<port>!
                Connection string was {}
            """.format(connection_string)
        )

    def __repr__(self):
        return "ServiceEndpoint(host_ip={}, port={})".format(self.host_ip, self.port)
