import subprocess
import sys

def run_command(command, description):
    print(f"Starting: {description}...")
    try:
        subprocess.run(command, check=True)
        print(f"Completed: {description}.")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred during {description}: {e}")
        sys.exit(1)

def install_packages():
    run_command(["apt-get", "update"], "updating package lists")
    run_command(["apt-get", "install", "hostapd", "-y"], "installing hostapd")
    run_command(["apt-get", "install", "dnsmasq", "-y"], "installing dnsmasq")

def setup_web_server():
    run_command(["sudo", "rm", "-rf", "/var/www/html"], "removing existing web files")
    run_command(["cp", "-r", "html", "/var/www/"], "copying new web files")

def show_banner():
    banner1 = """
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
   EVIL TWIN PROJECT
   By https://github.com/batuhanturker, 
      https://github.com/aykutemreyalcin, 
      https://github.com/fdemirhisar 
"""
    print(banner1)
    print(banner2)

def main():
    show_banner()
    print("Script started.")
    
    print("\033[1;34;40mInstalling necessary packages...\033[0m")
    install_packages()
    
    print("\033[1;34;40mSetting up web server...\033[0m")
    setup_web_server()
    
    print("\033[1;32mSetup completed successfully.\033[0m")

if __name__ == "__main__":
    main()
