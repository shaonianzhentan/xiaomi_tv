from zeroconf import ServiceBrowser, ServiceListener, ZeroconfServiceTypes
import time, asyncio

class XiaomiTVListener(ServiceListener):

    devices=[]

    def update_service(self, zc, type_: str, name: str) -> None:
        print(f"Service {name} updated")

    def remove_service(self, zc, type_: str, name: str) -> None:
        print(f"Service {name} removed")

    def add_service(self, zc, type_: str, name: str) -> None:
        print(f"Service {name} add")
        self.parse_service(zc, type_, name)

    def parse_service(self, zc, type_, name):
        info = zc.get_service_info(type_, name)

        addresses = info.parsed_addresses()
        for ip in info.parsed_addresses():
          # 判断是否存在
          if len(list(filter(lambda item: item['name'] == name and item['ip'] == ip, self.devices))) == 0:
            self.devices.append({ 'name': name, 'ip': ip })

def XiaomiTVScanner(zeroconf):
  listener = XiaomiTVListener()

  browser = ServiceBrowser(zeroconf, "_leboremote._tcp.local.", listener)
  time.sleep(5)
  zeroconf.close()

  return listener.devices


async def AsyncXiaomiTVScanner(zeroconf):
  listener = XiaomiTVListener()

  browser = ServiceBrowser(zeroconf, "_leboremote._tcp.local.", listener)
  await asyncio.sleep(5)
  zeroconf.close()

  return listener.devices