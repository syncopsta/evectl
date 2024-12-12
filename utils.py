import os
import sys
import yaml
import subprocess
import random
import re
from pytun import TunTapDevice, IFF_TAP
from config import eve_cfg

class VMNameExistsError(Exception):
    def __init__(self, vm_name, message="A virtual machine with this name already exists"):
        self.vm_name = vm_name
        self.message = f"{message}: '{vm_name}'"
        super().__init__(self.message)

def load_config(vm_name):
    config_path = os.path.join(eve_cfg['directories']['vm_config'], f"{vm_name}.yaml")
    if not os.path.exists(config_path):
        print(f"Configuration file {config_path} not found.")
        sys.exit(1)
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)

def resize_qemu_disk(data_dir, image_name, disk_size):
    try:
        image_path = f"{data_dir}/{image_name}.raw"
        resize_command = ["qemu-img", "resize", image_path, f"{disk_size}G"]
        result = subprocess.run(
            resize_command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        return True, "Disk resize successful"
    except subprocess.CalledProcessError as e:
        return False, f"Error resizing disk: {e.stderr}"
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"

def start_process(command):
    try:
        subprocess.Popen(
            command,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL,
            start_new_session=True,
            shell=True
        )
    except Exception as e:
        print(f"Error starting process: {str(e)}")

def create_tun_device(net_tap):
    tap = TunTapDevice(flags=IFF_TAP, name=net_tap)
    tap.persist(True)
    tap.up()
    tap.close()
    return tap.name

def load_images():
    with open(f'{eve_cfg["directories"]["config"]}cloud_images.yaml', 'r') as file:
        return yaml.safe_load(file)['images']

def get_image_path(image_spec):
    try:
        os_name, version = image_spec.split(':')
        images = load_images()
        if os_name in images and version in images[os_name]:
            return images[os_name][version]
        else:
            return f"Error: Image {image_spec} not found"
    except ValueError:
        return "Error: Invalid format. Use 'os:version' (e.g., ubuntu:2404)"

def generate_mac_address():
    return f"52:54:00:{random.randint(0, 255):02x}:{random.randint(0, 255):02x}:{random.randint(0, 255):02x}"

def validate_inputs(vm_name, boot_vcpus, memory_size, disk_size, net_mac):
    if os.path.exists(eve_cfg['directories']['vm_config']+vm_name+".yaml"):
        raise VMNameExistsError(vm_name)
    if not isinstance(boot_vcpus, int) or boot_vcpus < 1:
        raise ValueError("boot_vcpus must be a positive integer")
    if not isinstance(memory_size, int) or memory_size < 1:
        raise ValueError("memory_size must be a positive integer")
    if not isinstance(disk_size, int) or disk_size < 1:
        raise ValueError("disk_size must be a positive integer")
    mac_pattern = re.compile(r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$')
    if not mac_pattern.match(net_mac):
        raise ValueError("Invalid MAC address format")

def create_vm_config(name, boot_vcpus, memory_size, disk_size, net_tap, net_mac):
    config = {
        'cpus': {'boot_vcpus': boot_vcpus},
        'memory': {'size': memory_size},
        'payload': {'kernel': eve_cfg['directories']['bin']+"CLOUDHV.fd"},
        'disks': [{'path': eve_cfg['directories']['data']+name+".raw", 'size': str(disk_size)+"G"}],
        'net': [{'tap': net_tap, 'mac': net_mac}],
        'rng': {'src': "/dev/urandom"},
        'balloon': {'size': 0},
        'serial': {'mode': 'tty'},
        'console': {'mode': 'off'},
        'watchdog': True
    }
    with open(f'{eve_cfg["directories"]["vm_config"]}{name}.yaml', 'w') as f:
        yaml.dump(config, f, default_flow_style=False)
    return config
