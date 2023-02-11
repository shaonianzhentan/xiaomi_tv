from zeroconf import ServiceBrowser, ServiceListener, Zeroconf, ZeroconfServiceTypes
from typing import Any, Optional, cast

class MyListener(ServiceListener):

    def update_service(self, zc: Zeroconf, type_: str, name: str) -> None:
        print(f"Service {name} updated")

    def remove_service(self, zc: Zeroconf, type_: str, name: str) -> None:
        print(f"Service {name} removed")

    def add_service(self, zc: Zeroconf, type_: str, name: str) -> None:
        info = zc.get_service_info(type_, name)
        print(f"Service {name} added, service info: {info}")
        addresses = ["%s:%d" % (addr, cast(int, info.port)) for addr in info.parsed_addresses()]
        print("  Addresses: %s" % ", ".join(addresses))
        print("  Weight: %d, priority: %d" % (info.weight, info.priority))
        print(f"  Server: {info.server}")
        if info.properties:
            print("  Properties are:")
            for key, value in info.properties.items():
                print(f"    {key}: {value}")
        else:
            print("  No properties")


zeroconf = Zeroconf()
listener = MyListener()

types = ZeroconfServiceTypes.find()
for service in types:
  print(service)
  ServiceBrowser(zeroconf, service, listener)

input('test')