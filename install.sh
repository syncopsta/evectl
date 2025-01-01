#!/bin/bash

set -e
withoutos=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --withoutos)
            withoutos=true
            shift
            ;;
        *)
            shift
            ;;
    esac
done

print_status() {
    echo -e "\e[1;34m[*]\e[0m $1"
}

check_status() {
    if [ $? -eq 0 ]; then
        echo -e "\e[1;32m[✓]\e[0m $1"
    else
        echo -e "\e[1;31m[✗]\e[0m $1"
        exit 1
    fi
}

print_status "Starting installation of evectl and evemds..."

# Create directories
print_status "Create directories..."
mkdir -p /var/run/evectl/
mkdir -p /var/lib/evectl/cloud_images/
check_status "Directories created"

# Clone repositories
print_status "Cloning repositories..."
git clone https://github.com/syncopsta/evectl /opt/evectl
git clone https://github.com/syncopsta/evemds /opt/evemds
check_status "Repositories cloned"

# Setup evectl virtual environment
print_status "Setting up evectl virtual environment..."
cd /opt/evectl
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
deactivate
check_status "evectl environment setup complete"

# Setup evemds virtual environment
print_status "Setting up evemds virtual environment..."
cd /opt/evemds
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
deactivate
check_status "evemds environment setup complete"

# Create system user
print_status "Creating system user evemds..."
useradd -r -s /bin/false evemds 2>/dev/null || true
check_status "System user created"

# Add to PATH
print_status "Moving evectl to /usr/local/bin"
mv /opt/evectl/evectl /usr/local/bin/evectl
chmod +x /usr/local/bin/evectl

# Set permissions
print_status "Setting correct permissions..."
chown -R evemds:evemds /opt/evemds
mv /opt/evemds/evemds.service /etc/systemd/system/evemds.service

# Download VMM and firmware
print_status "Download VMM and Firmware..."
wget https://github.com/cloud-hypervisor/cloud-hypervisor/releases/download/v42.0/cloud-hypervisor-static -O /opt/evectl/bin/chr
wget https://github.com/cloud-hypervisor/edk2/releases/download/ch-6624aa331f/CLOUDHV.fd -O /opt/evectl/bin/CLOUDHV.fd
chmod +x /opt/evectl/bin/chr
check_status "VMM and Firmware downloaded"

# Skip OS Download when --withoutos is set
if [ "$withoutos" = false ]; then
    print_status "Download Ubuntu Cloud Image..."
    wget https://cloud-images.ubuntu.com/noble/current/noble-server-cloudimg-amd64.img -O /var/lib/evectl/cloud_images/noble-server-cloudimg-amd64.img
    check_status "Download finished"

    print_status "Converting Cloud image..."
    qemu-img convert /var/lib/evectl/cloud_images/noble-server-cloudimg-amd64.img /var/lib/evectl/cloud_images/ubuntu-24.04.raw
    rm /var/lib/evectl/cloud_images/noble-server-cloudimg-amd64.img
    check_status "Converting finished"
fi

print_status "Installation completed successfully!"
echo "======================================================================"
check_status "You now can use evectl"
