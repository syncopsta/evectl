# evectl

evectl is a command-line virtualization management tool designed to work with the cloud-hypervisor VMM, providing essential VM lifecycle management capabilities. When used in conjunction with [evemds](https://github.com/syncopsta/evemds) (eve Metadata Server), it offers a streamlined way to deploy fully configured Linux virtual machines within minutes.

⚠️ **Work In Progress Notice**

Please note that this project is currently under active development and should be considered a Work In Progress (WIP). As such:

- Features may be incomplete or subject to change
- Stability is not guaranteed
- Some functionality might not work as expected

## Security Warning

Some default configurations are currently not optimized for security and should be reviewed before using in a production environment. For example:

- evemds defaults to listening on `0.0.0.0:9001` using HTTP
- Cloud-init data is transmitted without encryption
- Other security features may need hardening

It is recommended to evaluate and adjust these settings according to your security requirements before deploying in a production environment.

## Overview

evectl aims to streamline the [Cloud-Hypervisor](https://github.com/cloud-hypervisor/cloud-hypervisor/) workflow, making it accessible to both developers and system administrators. By abstracting away the complexities of low-level VM management, evectl allows users to focus on their workloads rather than the underlying infrastructure. The integration with [evemds](https://github.com/syncopsta/evemds/) further simplifies the process by providing dynamic metadata to newly created VMs, enabling automated configuration and initialization using cloud-init.

Key features:

*   **Simplified VM Management:** Create, start, stop, delete, and list VMs with simple commands.
*   **Cloud-Init Integration:** Seamless integration with evemds for automated VM configuration.
*   **Fast Deployment:** Launch fully initialized Linux VMs in under a minute.
*   **CLI-centric:** Designed for efficient command-line interaction and scripting.

## Components

evectl relies on several key components to provide its functionality:

*   **evectl (CLI):** The core command-line tool that provides the user interface for interacting with Cloud-Hypervisor. It handles parsing commands, communicating with the Cloud-Hypervisor API, and displaying output to the user.
*   **Cloud-Hypervisor:** The underlying virtualization technology that provides the hypervisor and virtual machine execution environment. evectl interacts directly with the Cloud-Hypervisor API to manage VMs.
*   **evemds (Metadata Server):** A minimal metadata server that provides instance-specific data to VMs during boot. This data is used by cloud-init to automate tasks such as setting hostnames, configuring networking, and installing software. evemds serves metadata in the standard cloud-init format.
*   **Cloud-Init:** A widely used industry standard multi-distribution package that handles early initialization of a cloud instance. It reads metadata provided by evemds and performs the necessary configuration steps.
*   **VM Images:** Disk images containing the operating system and necessary software for the virtual machines. These images are used as the basis for creating new VMs. Typically, these are cloud images that are pre-configured for cloud-init.

The interaction between these components is as follows:

1.  The user uses `evectl create` to create a new VM, specifying parameters such as the image, memory, and vCPUs.
2.  evectl instructs Cloud-Hypervisor to create the VM instance.
3.  The newly booted VM requests metadata from the configured metadata server (evemds).
4.  evemds provides the metadata, including network configuration, SSH keys, and user data.
5.  cloud-init within the VM processes the metadata, configuring the system accordingly.
6.  The VM is now fully initialized and ready for use.

## Quickstart
### Requirements
- python3-venv
- python3-pip
- bridge-utils
- qemu-utils (for qemu-img)
- A DHCP server somewhere in your network

## Automated Installation

The automated installation script handles all essential components:
- UEFI Firmware (compatible version)
- Cloud-hypervisor
- Ubuntu Server LTS (latest version)

Run this command to start the installation:
```bash
curl -s https://raw.githubusercontent.com/syncopsta/evectl/refs/heads/main/install.sh | bash
```

## Post-Installation Configuration

### Network Setup

1. Configure the network bridge:
   - Create a new bridge interface
   - Either bridge it with your physical network interface
   - Or set up Host-to-VM connectivity with a dedicated IP address

Example for Host-to-VM connectivity:
```bash
brctl addbr vmbr0
ip link set up dev vmbr0
ip addr add 192.168.27.254/24 dev vmbr0
```

### Configure evectl

Edit the configuration file at `/opt/evectl/etc/evectl.yaml`:

```yaml
directories:
  bin: /opt/evectl/bin/
  data: /var/lib/evectl/
  config: /opt/evectl/etc/
  socket: /var/run/evectl/
  vm_config: /etc/evectl/vmcfg/

network:
  metadata_server: http://192.168.27.254:9001/  # Modify as needed
  default_bridge: vmbr0                         # Change if using different bridge
```

Key configuration points:
- The metadata server (`evemds`) defaults to 0.0.0.0:9001
- Adjust the metadata_server address according to your setup
- Modify default_bridge if using a different bridge interface name

#### evemds configuration
- /etc/evectl/hosts_config.yaml
  - metadata service evemds configuration file
  - The `fallback.evectl` key is a default key that gets deployed if the needed hostname is not present in the configuration.

```yaml
hosts:
  dbserver.example.com:
    ssh_keys:
      - "ssh-rsa AAAAB3NzaC1yc2E... admin@company.com"
      - "ssh-rsa AAAAB3N5aD1eaFE... admin2@company.com"

  fallback.evectl:
    ssh_keys:
      - "ssh-rsa AAAAB3NzaC1yc2E... admin@company.com"
```

### Cloud image database
- /opt/evectl/etc/cloud_images.yaml (Image database)
  - after the image conversion move the .raw file to `/var/lib/evectl/cloud_images/`

```yaml
images:
  ubuntu:
    "2404": "/var/lib/evectl/cloud_images/ubuntu-24.04.raw"
    "2204": "/var/lib/evectl/cloud_images/ubuntu-22.04.raw"
  debian:
    "12": "/var/lib/evectl/cloud_images/debian12.raw"
    "13": "/var/lib/evectl/cloud_images/debian13.raw"
```
To view the image database, use the following command:

```sh
evectl listimages
```

### Image Conversion

Images need to be converted using `qemu-img convert` from qcow2 into raw. For example:

```sh
qemu-img convert noble-server-cloudimg-amd64.img noble-server-cloudimg-amd64.raw
```


## Images

### Supported Images

All Generic Cloud Images with cloud-init preinstalled should be working.

Currently only tested with Ubuntu images.


| Linux Distribution | Download | Version | Tested |
| -------- | -------| -------| -------|
| Alpine Linux | [Download](https://alpinelinux.org/cloud/) | Cloud / UEFI | Yes |
| AlmaLinux  | [Download](https://almalinux.org/get-almalinux/#Cloud_Images) | / | No |
| Arch Linux | [Download](https://gitlab.archlinux.org/archlinux/arch-boxes/) | / | No |
| CentOS | [Download](https://cloud.centos.org/centos/9-stream/) | / | No |
| Debian | [Download](https://cdimage.debian.org/images/cloud/) | Generic Cloud | Yes |
| Fedora | [Download](https://alt.fedoraproject.org/cloud/) | Cloud Base Generic | Yes |
| Kali Linux | [Download](https://www.kali.org/get-kali/#kali-cloud) | / | No |
| openSUSE | [Download](https://get.opensuse.org/leap) | NoCloud / Cloud | Yes |
| RHEL | [Download](https://access.redhat.com/downloads/content/479/ver=/rhel---9/x86_64/product-downloads) | / | No |
| Rocky Linux | [Download](https://rockylinux.org/download) | / | No |
| SLES | [Download](https://www.suse.com/download/sles/) | / | No |
| Ubuntu | [Download](https://cloud-images.ubuntu.com/) | 24.04 | Yes |


## Metadata Server (evemds)

The metadata server is required for cloud-init, specifically for automatic SSH key provisioning on boot of virtual machines.

### Default Configuration

The metadata server listens on `http://0.0.0.0:9001` by default. The IP/port configuration can be modified in the systemd service file located at `/etc/systemd/system/evemds.service`.

### evemds Configuration

- **Edit Configuration**:
  ```sh
  sudo nano /etc/evectl/hosts_config.yaml
  ```

- **Restart Service**:
  ```sh
  sudo systemctl restart evemds
  ```

## License

Please see the file called `LICENSE`.
