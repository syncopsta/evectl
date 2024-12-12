#!/usr/bin/env python3

import argparse
from cli import setup_parser
from vm_manager import (
    create_vm, start_vm, stop_vm, force_stop_vm, restart_vm,
    get_vm_status, get_vm_info, get_vm_pid, get_vm_counter,
    delete_vm, list_images, list_vms
)

def main():
    parser = setup_parser()
    args = parser.parse_args()

    command_handlers = {
        'create': create_vm,
        'start': start_vm,
        'stop': stop_vm,
        'force-stop': force_stop_vm,
        'restart': restart_vm,
        'status': get_vm_status,
        'info': get_vm_info,
        'pid': get_vm_pid,
        'vmcounter': get_vm_counter,
        'delete': delete_vm,
        'listimages': list_images,
        'list': list_vms
    }

    handler = command_handlers.get(args.command)
    if handler:
        handler(args)
    else:
        print(f"Unknown command: {args.command}")

if __name__ == '__main__':
    main()
