import os
import shutil
import signal
from pyroute2 import IPRoute
import pybrctl
from config import eve_cfg
from utils import (
    load_config, resize_qemu_disk, start_process, create_tun_device,
    load_images, get_image_path, generate_mac_address, validate_inputs,
    create_vm_config
)
from cloud_hypervisor_client import CloudHypervisorClient

def create_vm(args):
    if not args.mac:
        args.mac = generate_mac_address()
    validate_inputs(args.vm_name, args.cpu, args.ram, args.hdd, args.mac)
    config = create_vm_config(
        name=args.vm_name,
        boot_vcpus=args.cpu,
        memory_size=args.ram*1024*1024,
        disk_size=args.hdd,
        net_tap=args.tap,
        net_mac=args.mac,
    )
    image = get_image_path(args.baseimage)
    shutil.copy(image, f"{eve_cfg['directories']['data']}{args.vm_name}.raw")
    success, message = resize_qemu_disk(eve_cfg['directories']['data'], args.vm_name, args.hdd)
    print("VM created successfully")

def start_vm(args):
    print(f"Starting VM: {args.vm_name}")
    config = load_config(args.vm_name)
    tapdevice = create_tun_device(config["net"][0]["tap"])
    brctl = pybrctl.BridgeController()
    b = brctl.getbr(eve_cfg['network']['default_bridge'])
    b.addif(tapdevice)
    mds = eve_cfg['network']['metadata_server']
    mac = config["net"][0]["mac"]
    cmd = f'{eve_cfg["directories"]["bin"]}chr ' \
          f'--kernel {config["payload"]["kernel"]} ' \
          f'--disk path={config["disks"][0]["path"]} ' \
          f'--cpus boot={config["cpus"]["boot_vcpus"]} ' \
          f'--memory size={config["memory"]["size"]} ' \
          f'--net "tap={tapdevice},mac={mac},ip=,mask=" ' \
          f'--serial null ' \
          f'--console null ' \
          f'--platform serial_number="ds=nocloud;s={mds}{args.vm_name}/" ' \
          f'--api-socket path={eve_cfg["directories"]["socket"]}{args.vm_name}.socket'
    start_process(cmd)

def stop_vm(args):
    client = CloudHypervisorClient(socket_path=f'{eve_cfg["directories"]["socket"]}{args.vm_name}.socket')
    response = client.power_button()
    if response and response.status_code == 204:
        config = load_config(args.vm_name)
        ip = IPRoute()
        ip.link("delete", ifname=config["net"][0]["tap"])
        print(f"VM {args.vm_name} shutdown")
    else:
        print(f"VM {args.vm_name} is not running")

def force_stop_vm(args):
    client = CloudHypervisorClient(socket_path=f'{eve_cfg["directories"]["socket"]}{args.vm_name}.socket')
    pid = client.pid()
    if pid:
        os.kill(pid, signal.SIGTERM)
        config = load_config(args.vm_name)
        ip = IPRoute()
        ip.link("delete", ifname=config["net"][0]["tap"])
        print(f"Force-Stopped VM: {args.vm_name}")
    else:
        print(f"VM {args.vm_name} is not running")

def restart_vm(args):
    client = CloudHypervisorClient(socket_path=f'{eve_cfg["directories"]["socket"]}{args.vm_name}.socket')
    response = client.reboot_vm()
    if response and response.status_code == 204:
        print(f"VM {args.vm_name} is restarting")
    else:
        print("Error restarting VM")

def get_vm_status(args):
    client = CloudHypervisorClient(socket_path=f'{eve_cfg["directories"]["socket"]}{args.vm_name}.socket')
    response = client.ping()
    if response and response.ok:
        print(f"VM {args.vm_name} is running")
    else:
        print(f"VM {args.vm_name} is not running")

def get_vm_info(args):
    client = CloudHypervisorClient(socket_path=f'{eve_cfg["directories"]["socket"]}{args.vm_name}.socket')
    response = client.get_vm_info()
    if response and response.ok:
        print(response.json())
    else:
        print(f"VM {args.vm_name} is not running")

def get_vm_pid(args):
    client = CloudHypervisorClient(socket_path=f'{eve_cfg["directories"]["socket"]}{args.vm_name}.socket')
    pid = client.pid()
    if pid:
        print(pid)
    else:
        print(f"VM {args.vm_name} is not running")

def get_vm_counter(args):
    client = CloudHypervisorClient(socket_path=f'{eve_cfg["directories"]["socket"]}{args.vm_name}.socket')
    response = client.get_vm_counters()
    if response and response.ok:
        print(response.json())
    else:
        print(f"VM {args.vm_name} is not running")

def delete_vm(args):
    config = load_config(args.vm_name)
    os.remove(config["disks"][0]["path"])
    os.remove(f"{eve_cfg['directories']['vm_config']}{args.vm_name}.yaml")
    print(f"Deleted VM: {args.vm_name}")

def list_images(args):
    images = load_images()
    print("\nAvailable Images:")
    print("-" * 60)
    print(f"{'OS':<15}{'Version':<15}{'Path'}")
    print("-" * 60)
    for os_name, versions in images.items():
        for version, path in versions.items():
            print(f"{os_name:<15}{version:<15}{path}")

def list_vms(args):
    vm_configs = os.listdir(eve_cfg['directories']['vm_config'])
    vm_names = [x.split('.yaml')[0] for x in vm_configs if not x.startswith('.')]
    print(*vm_names, sep='\n')
