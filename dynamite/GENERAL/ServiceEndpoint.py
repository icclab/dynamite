__author__ = 'bloe'


class ServiceEndpoint:
    def __init__(self, host_ip, port):
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
