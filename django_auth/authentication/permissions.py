from ipaddress import ip_address, ip_network
from typing import Any

from rest_framework import permissions
from rest_framework.request import Request


class LocalhostOnly(permissions.BasePermission):
    message: str = "Access restricted to localhost only."

    def get_client_ip(self, request: Request) -> str:
        # First check X-Forwarded-For header since we're behind nginx
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR", "")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0].strip()
        else:
            ip = request.META.get("REMOTE_ADDR", "")
        return ip

    def is_localhost(self, ip: str) -> bool:
        try:
            # Check if IP is localhost (127.0.0.1) or in local network (127.0.0.0/8)
            return ip_address(ip) in ip_network("127.0.0.0/8")
        except ValueError:
            return False

    def has_permission(self, request: Request, view: Any) -> bool:
        client_ip = self.get_client_ip(request)
        return self.is_localhost(client_ip)
