import os

def read_config_file():
    # Path to the SSH config file
    config_path = os.path.expanduser("~/.ssh/config")
    hosts = {}
    with open(config_path, "r") as f:
        lines = f.readlines()
        current_host = None
        for line in lines:
            line = line.strip()
            if line.startswith("#") or not line:
                continue
            if line.startswith("Host") and not line.startswith("HostName"):
                current_host = line.split()[1]
                hosts[current_host] = {}
            else:
                key, value = line.split(maxsplit=1)
                hosts[current_host][key] = value
    return hosts

def print_menu(hosts):
    print("SSH Config Hosts:")
    for i, host in enumerate(hosts.keys()):
        print(f"{i+1}. {host}")
    print(f"{len(hosts)+1}. Quit")

def select_host(hosts):
    while True:
        choice = input("Enter choice: ")
        try:
            choice = int(choice)
            if choice == len(hosts)+1:
                return None
            if choice < 1 or choice > len(hosts):
                raise ValueError
            break
        except ValueError:
            print("Invalid choice. Please try again.")
    return list(hosts.keys())[choice-1]

def main():
    hosts = read_config_file()
    while True:
        print_menu(hosts)
        selected_host = select_host(hosts)
        if selected_host is None:
            break
        print(f"\nConnecting to {selected_host}...")
        os.system(f"ssh {selected_host}")

if __name__ == "__main__":
    main()
