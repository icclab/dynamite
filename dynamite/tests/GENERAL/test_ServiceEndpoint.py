__author__ = 'bloe'

from dynamite.GENERAL.ServiceEndpoint import ServiceEndpoint
import pytest

class TestServiceEndpoint:

    MIN_ALLOWED_PORT = 1
    MAX_ALLOWED_PORT = 65535
    VALID_IP = "127.0.0.1"

    def test_init(self):
        host_ip = self.VALID_IP
        port = self.MAX_ALLOWED_PORT
        endpoint = ServiceEndpoint(host_ip, port)
        assert endpoint.host_ip == host_ip
        assert endpoint.port == port

        port = self.MIN_ALLOWED_PORT
        endpoint = ServiceEndpoint(host_ip, port)
        assert endpoint.host_ip == host_ip
        assert endpoint.port == port

    def test_init_with_zero_port(self):
        with pytest.raises(ValueError):
            host_ip = self.VALID_IP
            port = 0
            endpoint = ServiceEndpoint(host_ip, port)
            assert False

    def test_init_with_minus_port(self):
        with pytest.raises(ValueError):
            host_ip = self.VALID_IP
            port = -1
            endpoint = ServiceEndpoint(host_ip, port)
            assert False

    def test_init_with_too_large_port(self):
        with pytest.raises(ValueError):
            host_ip = self.VALID_IP
            port = self.MAX_ALLOWED_PORT + 1
            endpoint = ServiceEndpoint(host_ip, port)
            assert False

    def test_init_with_invalid_ip(self):
        with pytest.raises(ValueError):
            host_ip = ""
            port = self.MAX_ALLOWED_PORT
            endpoint = ServiceEndpoint(host_ip, port)
            assert False

    def test_from_string(self):
        endpoint = ServiceEndpoint.from_string(self.VALID_IP + ":" + str(self.MIN_ALLOWED_PORT))
        assert endpoint.host_ip == self.VALID_IP
        assert endpoint.port == self.MIN_ALLOWED_PORT

    def test_from_string_empty(self):
        with pytest.raises(ValueError):
            ServiceEndpoint.from_string("")
            assert False

    def test_from_string_missing_ip(self):
        with pytest.raises(ValueError):
            ServiceEndpoint.from_string(":" + str(self.MAX_ALLOWED_PORT))
            assert False

    def test_from_string_missing_port(self):
        with pytest.raises(ValueError):
            ServiceEndpoint.from_string(self.VALID_IP)
            assert False
