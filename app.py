import yaml
import os
import subprocess
import shutil
import random
import string
import docker

import colorama
from colorama import Fore, Back, Style
PathCodeEditor = "editor"
PathLSWSConf = "lswsconf"
repo_url = "https://github.com/SkyFetch0/cyberpanel-docker-app-setup"
colorama.init(autoreset=True)
def SetupFolder(folder_path):
    try:

        os.makedirs(folder_path + PathCodeEditor)
        os.makedirs(folder_path + PathLSWSConf)
        print(f"Klasör oluşturuldu: {folder_path}")
    except FileExistsError:
        print(f"Klasör zaten mevcut: {folder_path}")
    except OSError as e:
        print(f"Hata oluştu: {e}")



def find_services(yaml_file):
    with open(yaml_file, 'r') as stream:
        try:
            yaml_content = yaml.safe_load(stream)
            if 'services' in yaml_content:
                services = yaml_content['services']
                db_services = [service_name for service_name in services if service_name.endswith('-db')]
                non_db_services = [service_name for service_name in services if not service_name.endswith('-db')]
                for non_db_service in non_db_services:
                    db_service_name = non_db_service + "-db"
                    if db_service_name in db_services:
                        return non_db_service,db_service_name
            else:
                print("YAML file does not contain 'services' section.")
        except yaml.YAMLError as exc:
            print(f"Error while parsing YAML file: {exc}")
            
def get_ports(main_service, yaml_file):
    with open(yaml_file, 'r') as stream:
        try:
            yaml_content = yaml.safe_load(stream)
            if 'services' in yaml_content:
                services = yaml_content['services']
                if main_service in services:
                    ports = services[main_service].get('ports', [])
                    return ports
                else:
                    print(f"Service '{main_service}' not found in YAML file.")
            else:
                print("YAML file does not contain 'services' section.")
        except yaml.YAMLError as exc:
            print(f"Error while parsing YAML file: {exc}")
            
def get_volumes(main_service, yaml_file):
    with open(yaml_file, 'r') as stream:
        try:
            yaml_content = yaml.safe_load(stream)
            if 'services' in yaml_content:
                services = yaml_content['services']
                if main_service in services:
                    volumes = services[main_service].get('volumes', [])
                    return volumes
                else:
                    print(f"Service '{main_service}' not found in YAML file.")
            else:
                print("YAML file does not contain 'services' section.")
        except yaml.YAMLError as exc:
            print(f"Error while parsing YAML file: {exc}")


def get_mount_source(volume):
    parts = volume.split('data:')
    if len(parts) > 1:
        return parts[0]
    else:
        return None  
    
def update_map_values(conf_file, old_value, new_value):
    updated_lines = []
    status = False
    with open(conf_file, 'r') as f:
        lines = f.readlines()
        for line in lines:
            if line.strip().startswith("map") and old_value in line:
                updated_line = line.replace(old_value, new_value)
                updated_lines.append(updated_line)
                status = True
                
            else:
                updated_lines.append(line)
    
    with open(conf_file, 'w') as f:
        f.writelines(updated_lines)
    
    return status
    
def add_volume(main_service, yaml_file, new_volume):
    with open(yaml_file, 'r') as stream:
        try:
            yaml_content = yaml.safe_load(stream)
            if 'services' in yaml_content:
                services = yaml_content['services']
                if main_service in services:
                    volumes = services[main_service].get('volumes', [])
                    volumes.append(new_volume)
                    services[main_service]['volumes'] = volumes
                    with open(yaml_file, 'w') as f:
                        yaml.safe_dump(yaml_content, f)
                    print(f"Added volume '{new_volume}' to '{main_service}' service.")
                else:
                    print(f"Service '{main_service}' not found in YAML file.")
            else:
                print("YAML file does not contain 'services' section.")
        except yaml.YAMLError as exc:
            print(f"Error while parsing or writing YAML file: {exc}")


def add_port(main_service, yaml_file, new_port):
    with open(yaml_file, 'r') as stream:
        try:
            yaml_content = yaml.safe_load(stream)
            if 'services' in yaml_content:
                services = yaml_content['services']
                if main_service in services:
                    ports = services[main_service].get('ports', [])
                    ports.append(new_port)
                    services[main_service]['ports'] = ports
                    with open(yaml_file, 'w') as f:
                        yaml.safe_dump(yaml_content, f)
                    print(f"Added port '{new_port}' to '{main_service}' service.")
                else:
                    print(f"Service '{main_service}' not found in YAML file.")
            else:
                print("YAML file does not contain 'services' section.")
        except yaml.YAMLError as exc:
            print(f"Error while parsing or writing YAML file: {exc}")

def clone_repo(repo_url,folder):

    try:
        subprocess.run(["git", "clone", repo_url, folder], check=True)
        print(f"Repository cloned to {folder}")
    except subprocess.CalledProcessError as e:
        print(f"Failed to clone repository: {e}")


def move_files(source_folder, target_folder):
    try:
        if not os.path.exists(target_folder):
            os.makedirs(target_folder)
        for item in os.listdir(source_folder):
            source_path = os.path.join(source_folder, item)
            target_path = os.path.join(target_folder, item)
            if os.path.isdir(source_path):
                shutil.copytree(source_path, target_path)
            else:
                shutil.copy2(source_path, target_path)
        print(f"Files moved from {source_folder} to {target_folder}")
        return True
    except Exception as e:
        print(f"Failed to move files: {e}")
        return False

def print_service(yaml_file,website,CodeEditor):
    result = find_services(yaml_file)
    if result:
        main_service, corresponding_db_service = result
        print(main_service)
        print(corresponding_db_service)
        volumes = get_volumes(main_service,yaml_file)
        if volumes:
            volume = volumes[0]  
            mount_source = get_mount_source(volume)
            if mount_source:
                print(mount_source)
                path = mount_source
            else:
                print("Path Not Found!")
                path = input("Enter Path: ")
            
            if path:
                a1 = string.ascii_letters + string.digits
                folder = ''.join(random.choices(a1, k=16))

                clone_repo(repo_url, folder)
                source_folder = os.path.join(folder, "lswsconf")
                target_folder = path + "lswsconf/"  
                move_conf = move_files(source_folder, target_folder)
                if move_conf:
                    print(f"Files moved successfully to {path}")

                    source_folder = os.path.join(folder,"editor")
                    target_folder = path + "editor/"
                    move_editor = move_files(source_folder, target_folder)
                    if move_editor:
                        print(f"Files moved successfully to {path}")
                    else:
                        print(source_folder + " | >> |" + target_folder + " Dont Moved!")
                        exit
                else:
                    print(source_folder + " | >> |" + target_folder + " Dont Moved!")
                    exit




                print(f"Path: {path}")
                # Add docker-compose.yaml
                new_volume = path+"editor:/usr/local/lsws/CodeEditor/html"
                add_volume(main_service, yaml_file, new_volume)
                new_volume = path+"lswsconf:/usr/local/lsws/conf"
                add_volume(main_service, yaml_file, new_volume)
                lswsport = input("Lsws Port(Example: 9001,9002 ): ")
                new_port = lswsport+":7080"
                add_port(main_service, yaml_file, new_port)
                #Create Folders
                setup = SetupFolder(path)
                conf_file = path + "lswsconf/httpd_config.conf"  
                old_value = "CustomWebsite"      
                new_value = website   

                change1 = update_map_values(conf_file, old_value, new_value)
                if change1:
                    old_value = "CodeWebsite"
                    new_value = CodeEditor

                    change2 = update_map_values(conf_file, old_value, new_value)
                    if change2:

                        print(Fore.GREEN + "Process Success")
                    else:
                        print("httpd_config.conf Editing Error! Not Change CodeWebsite")
                else:
                    print("httpd_config.conf Editing Error! Not Change CustomWebsite")
            else:
                print("Path Not Found!!!!")
                exit

def change_litespeed_password(container_name, username, new_password):
    client = docker.from_env()

    try:
        container = client.containers.get(container_name)
        
        command = f"/usr/local/lsws/admin/misc/admpass.sh --username {username} --new-password {new_password}"
        
        exit_code, output = container.exec_run(command)
        
        if exit_code == 0:
            print("LiteSpeed password successfully changed.")
            return True
        else:
            print(f"Error occurred while changing password: {output.decode()}")
            return False
    except docker.errors.NotFound:
        print(f"Container '{container_name}' not found.")
        return False
    except docker.errors.APIError as e:
        print(f"API error: {e}")
        return False



if __name__ == "__main__":
    print(Fore.GREEN + "1- Setup Composer ")
    print(Fore.BLUE + "2- Set LiteSpeed Password" )
    select = input("Select:")
    if select == 2:
        container_name = input("Container Name: ")
        username = input("Username: ")
        new_password = input("Password")
        change_litespeed_password(container_name, username, new_password)
    else:
        yaml_file = "docker-compose.yml"
        website = input("Website Domain (example.com) : ")
        CodeEditor = input("Code Editor Domain(example2.com / code.example.com) : ")
        print_service(yaml_file,website,CodeEditor)   

    
    
