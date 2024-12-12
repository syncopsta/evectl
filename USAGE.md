## Usage

### evectl Commands

```sh
Usage: evectl [-h] [-v]
              {create,start,stop,force-stop,restart,status,delete,info,pid,vmcounter,listimages,list}
              ...

Virtual machine management tool

Positional Arguments:
  {create,start,stop,force-stop,restart,status,delete,info,pid,vmcounter,listimages,list}
                        Commands
    create              Create a new virtual machine
    start               Start a virtual machine
    stop                Stop a virtual machine (Power Button)
    force-stop          Force-stop a virtual machine (kill PID)
    restart             Restart a virtual machine
    status              Get virtual machine status
    delete              Delete a virtual machine
    info                Get detailed virtual machine informations
    pid                 Get pid of virtual machine
    vmcounter           Get virtual machine counter
    listimages          List all available cloud images
    list                List all configured virtual machines

Options:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
```

### Create Command

```sh
Usage: evectl create [-h] [--mac MAC] vm_name cpu ram hdd baseimage tap

Positional Arguments:
  vm_name     Name of the virtual machine
  cpu         Number of CPU cores
  ram         RAM size in MB
  hdd         HDD size in GB
  baseimage   Base image in the format distribution:version (e.g., ubuntu:2404 or debian:12)
  tap         TAP interface name

Options:
  -h, --help  show this help message and exit
  --mac MAC   MAC address (optional)
```

### Example Commands

- **Create a new virtual machine**:
- Description: Creating a virtual machine with the hostname myvm, 2 vCPUs, 4096 MB RAM, 50 GB Disk, using the Ubuntu 24.04 image and use the interface tap0
  ```sh
  evectl create myvm 2 4096 50 ubuntu:2404 tap0
  ```

- **Start a virtual machine**:
  ```sh
  evectl start myvm
  ```

- **Stop a virtual machine**:
  ```sh
  evectl stop myvm
  ```

- **Force-stop a virtual machine**:
  ```sh
  evectl force-stop myvm
  ```

- **Get virtual machine status**:
  ```sh
  evectl status myvm
  ```

- **Delete a virtual machine**:
  ```sh
  evectl delete myvm
  ```

- **Get detailed virtual machine information**:
  ```sh
  evectl info myvm
  ```

- **List all configured virtual machines**:
  ```sh
  evectl list
  ```

- **List all available cloud images**:
  ```sh
  evectl listimages
  ```
