import os
import subprocess
import argparse

# check if adb is installed and added to PATH
try:
    subprocess.check_output("adb --help", shell=True)
except subprocess.CalledProcessError:
    print("adb must be installed and added to PATH")
    exit()

# check if emulator is installed and added to PATH
try:
    subprocess.check_output("emulator --help", shell=True)
except subprocess.CalledProcessError:
    print("emulator must be installed and added to PATH")
    exit()

# parse command line arguments
parser = argparse.ArgumentParser(description='Set up an android testing environment')
parser.add_argument('--device', type=str, help='name of the device made in avdmanager')
parser.add_argument('--certificate', type=str, help='path to the certificate')
args = parser.parse_args()

# interactive mode
if args.device is None:
    device_name = input("Enter device name: ")
    subprocess.Popen(f"emulator -avd {device_name} -writable-system &", shell=True)
    input("Press enter when emulator is running")
    devices = subprocess.check_output("adb devices", shell=True).decode().split("\n")[1:-2]
    if len(devices) == 0:
        input("Please start the device and press enter to continue")
        devices = subprocess.check_output("adb devices", shell=True).decode().split("\n")[1:-2]
    if len(devices) == 1:
        device_name = devices[0].split("\t")[0]
    else:
        print("Multiple devices found:")
        for i, device in enumerate(devices):
            print("{0}. {1}".format(i+1, device.split('\t')[0]))
        choice = int(input("Enter device number: "))
        device_name = devices[choice-1].split("\t")[0]
else:
    device_name = args.device

# certificate
if args.certificate is None:
    certificate_path = input("Enter certificate path: ")
else:
    certificate_path = args.certificate

if certificate_path.endswith(".crt") or certificate_path.endswith(".pem"):
    subject_hash = subprocess.check_output(f"openssl x509 -inform PEM -subject_hash_old -in {certificate_path} | head -n 1", shell=True).decode().strip()
    subprocess.Popen(f"openssl x509 -in {certificate_path} -inform PEM -outform DER -out {subject_hash}.0", shell=True)
elif certificate_path.endswith(".DER"):
    subject_hash = os.path.splitext(os.path.basename(certificate_path))[0]
    subprocess.Popen(f"openssl x509 -in {certificate_path} -inform DER -outform DER -out {subject_hash}.0.tmp", shell=True)
else:
    print("Invalid certificate file format")
    exit()

subprocess.check_output(f"adb -s {device_name} root", shell=True)
subprocess.check_output(f"adb -s {device_name} shell \"mkdir /data/misc/user/0/cacerts-added\"", shell=True)
subprocess.check_output(f"adb -s {device_name} push {subject_hash}.0 /data/misc/user/0/cacerts-added/", shell=True)
subprocess.check_output(f"adb -s {device_name} shell \"su 0 chmod 664 /data/misc/user/0/cacerts-added/{subject_hash}.0\"", shell=True)
subprocess.check_output(f"adb -s {device_name} remount", shell=True)

if "remount succeeded" in subprocess.check_output(f"adb -s {device_name} remount", shell=True).decode():
    subprocess.check_output(f"adb -s {device_name} shell \"mv /data/misc/user/0/cacerts-added/{subject_hash}.0 /system/etc/security/cacerts\"", shell=True)
    subprocess.check_output(f"adb -s {device_name} reverse tcp:8888 tcp:8888", shell=True)
    print("Please set your intercept proxy to listen on 127.0.0.1:8888 and set the proxy on the device to 127.0.0.1:8888")
else:
    subprocess.check_output(f"adb -s {device_name} reboot", shell=True)
    subprocess.check_output(f"adb -s {device_name} remount", shell=True)
    if "remount succeeded" in subprocess.check_output(f"adb -s {device_name} remount", shell=True).decode():
        subprocess.check_output(f"adb -s {device_name} shell \"mv /data/misc/user/0/cacerts-added/{subject_hash}.0 /system/etc/security/cacerts\"", shell=True)
        subprocess.check_output(f"adb -s {device_name} reverse tcp:8888 tcp:8888", shell=True)
        print("Please set your intercept proxy to listen on 127.0.0.1:8888 and set the proxy on the device to 127.0.0.1:8888")
