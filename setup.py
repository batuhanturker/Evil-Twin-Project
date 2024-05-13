import subprocess

def install_packages():
    try:
        subprocess.run(["apt-get", "install", "hostapd", "-y"], check=True)
        subprocess.run(["apt-get", "install", "dnsmasq", "-y"], check=True)
    except subprocess.CalledProcessError as e:
        print("Error occurred during package installation:", e)
        exit(1)

def setup_web_server():
    try:
        subprocess.run(["sudo", "rm", "-rf", "/var/www/html"], check=True)
        subprocess.run(["cp", "-r", "html", "/var/www/"], check=True)
    except subprocess.CalledProcessError as e:
        print("Error occurred during web server setup:", e)
        exit(1)

if __name__ == "__main__":
    print("Installing packages...")
    install_packages()
    print("Setting up web server...")
    setup_web_server()
    print("Setup completed successfully.")
