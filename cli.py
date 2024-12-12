import argparse
from rich_argparse import RichHelpFormatter

def setup_parser():
    parser = argparse.ArgumentParser(
        prog='evectl',
        description='Virtual machine management tool',
        formatter_class=RichHelpFormatter
    )

    parser.add_argument("-v", "--version", action="version", version="{} v0.1.0".format(parser.prog))

    subparsers = parser.add_subparsers(dest='command', help='Commands')
    subparsers.required = True

    create_parser = subparsers.add_parser('create', help='Create a new virtual machine', formatter_class=parser.formatter_class)
    create_parser.add_argument('vm_name', type=str, help='Name of the virtual machine')
    create_parser.add_argument('cpu', type=int, help='Number of CPU cores')
    create_parser.add_argument('ram', type=int, help='RAM size in MB')
    create_parser.add_argument('hdd', type=int, help='HDD size in GB')
    create_parser.add_argument('baseimage', type=str, help='Base image path')
    create_parser.add_argument('tap', type=str, help='TAP interface name')
    create_parser.add_argument('--mac', type=str, help='MAC address (optional)')

    _add_vm_command(subparsers, 'start', 'Start a virtual machine')
    _add_vm_command(subparsers, 'stop', 'Stop a virtual machine (Power Button)')
    _add_vm_command(subparsers, 'force-stop', 'Force-stop a virtual machine (kill PID)')
    _add_vm_command(subparsers, 'restart', 'Restart a virtual machine')
    _add_vm_command(subparsers, 'status', 'Get virtual machine status')
    _add_vm_command(subparsers, 'delete', 'Delete a virtual machine')
    _add_vm_command(subparsers, 'info', 'Get detailed virtual machine informations')
    _add_vm_command(subparsers, 'pid', 'Get pid of virtual machine')
    _add_vm_command(subparsers, 'vmcounter', 'Get virtual machine counter')

    subparsers.add_parser('listimages', help='List all available cloud images',
                         formatter_class=parser.formatter_class)
    subparsers.add_parser('list', help='List all configured virtual machines',
                         formatter_class=parser.formatter_class)

    return parser

def _add_vm_command(subparsers, command, help_text):
    parser = subparsers.add_parser(command, help=help_text,
                                  formatter_class=RichHelpFormatter)
    parser.add_argument('vm_name', type=str, help='Name of the virtual machine')
