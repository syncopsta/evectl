import requests_unixsocket
import urllib.parse

class CloudHypervisorClient:
    def __init__(self, socket_path='/tmp/cloud-hypervisor.sock', base_url='http+unix://{}/api/v1'):
        encoded_socket_path = urllib.parse.quote(socket_path, safe='')
        self.session = requests_unixsocket.Session()
        self.base_url = base_url.format(encoded_socket_path)

    def _make_request(self, method, endpoint):
        resp = getattr(self.session, method)(f'{self.base_url}/{endpoint}')
        if resp.status_code in [200, 204]:
            return resp
        else:
            print(f'Error {resp.status_code}: {resp.reason}')
            return None

    def version(self):
        resp = self._make_request('get', 'vmm.ping')
        return resp.json()['version'] if resp else None

    def pid(self):
        resp = self._make_request('get', 'vmm.ping')
        return resp.json()['pid'] if resp else None

    def ping(self):
        return self._make_request('get', 'vmm.ping')

    def shutdown_vmm(self):
        return self._make_request('put', 'vmm.shutdown')

    def get_vm_info(self):
        return self._make_request('get', 'vm.info')

    def get_vm_counters(self):
        return self._make_request('get', 'vm.counters')

    def pause_vm(self):
        return self._make_request('put', 'vm.pause')

    def resume_vm(self):
        return self._make_request('put', 'vm.resume')

    def shutdown_vm(self):
        return self._make_request('put', 'vm.shutdown')

    def reboot_vm(self):
        return self._make_request('put', 'vm.reboot')

    def power_button(self):
        return self._make_request('put', 'vm.power-button')
