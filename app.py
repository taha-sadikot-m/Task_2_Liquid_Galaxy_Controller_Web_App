import subprocess  
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import paramiko
import asyncio
import gunicorn

MASTER_KML = '/var/www/html/kml/master_1.kml'  # Path to the master KML file
SLAVE_KML_TEMPLATE = '/var/www/html/kml/slave_{}.kml'
QUERY_FILE_PATH = "/tmp/query.txt"  # Path to the query file



# KML Template for Displaying an Image
DISPLAY_KML_TEMPLATE = """<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
    <ScreenOverlay>
      <name>Dynamic Image</name>
      <Icon>
        <href>{image_url}</href>
      </Icon>
      <overlayXY x="0.5" y="0.5" xunits="fraction" yunits="fraction"/>
      <screenXY x="0.5" y="0.5" xunits="fraction" yunits="fraction"/>
      <rotationXY x="0" y="0" xunits="fraction" yunits="fraction"/>
      <size x="0.5" y="0.5" xunits="fraction" yunits="fraction"/>
    </ScreenOverlay>
</kml>
"""



# KML Template for Clearing the Screen
CLEAR_KML_TEMPLATE = """<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <name>Clear Screen</name>
  </Document>
</kml>
"""

# Function to Update KML File on Master Node
def update_kml_file(client, kml_content, kml_path):
    try:
        sftp = client.open_sftp()
        
        with sftp.file(kml_path, 'w') as remote_file:
            remote_file.write(kml_content)
        
        sftp.close()
        print(f"KML file updated: {kml_path}")
    except Exception as e:
        print(f"Error updating KML file: {e}")
        

def ssh_connect(host, username, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(host, username=username, password=password)
    return client

async def send_command(ip, username, password, command):
    """Send a command to the Liquid Galaxy master node via SSH."""
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip, username=username, password=password)

        stdin, stdout, stderr = ssh.exec_command(command)
        output = stdout.read().decode()
        error = stderr.read().decode()
        ssh.close()

        if error:
            print(f"Error: {error}")
        return output
    except Exception as e:
        print(f"SSH Connection Failed: {e}")
        return None

def refresh_slaves(ssh,ip,username,password,slave_id):
    try:
        for i in range(2, 4):   
            if i==slave_id:
                search = "<href>##LG_PHPIFACE##kml/slave_{i}.kml</href>".format(i=i)
                replace = (
                    "<href>##LG_PHPIFACE##kml/slave_{i}.kml</href>"
                    "<refreshMode>onInterval</refreshMode>"
                    "<refreshInterval>2</refreshInterval>"
                ).format(i=i)
                
                # Construct the sed command
                sed_command = f"sed -i 's|{search.format(i=i)}|{replace.format(i=i)}|' ~/earth/kml/slave/myplaces.kml"
                clear_command_new = f"sed -i 's|{replace.format(i=i)}|{search.format(i=i)}|' ~/earth/kml/slave/myplaces.kml"

                # Construct the ssh commands to execute on the slave node
                ssh_clear_command = f'sshpass -p {password} ssh -t lg{i} "echo {password} | sudo -S {clear_command_new}"'
                ssh_set_command = f'sshpass -p {password} ssh -t lg{i} "echo {password} | sudo -S {sed_command}"'

               
                command = f'sshpass -p {password} ssh -t lg{i} "echo {password} | sudo -S {ssh_clear_command}"'
                stdin, stdout, stderr = ssh.exec_command(command, get_pty=True)
                stdin.write(f"{password}\n")
                stdin.flush()
                output = stdout.read().decode()
                error = stderr.read().decode()
                print("CLEAR  OUTPUT :- ",output)
                print("CLEAR ERROR :- ",error)

                # Construct the ssh command to execute on the slave node
                command = f'sshpass -p {password} ssh -t lg{i} "echo {password} | sudo -S {ssh_set_command}"'
                stdin, stdout, stderr = ssh.exec_command(command, get_pty=True)
                stdin.write(f"{password}\n")
                stdin.flush()
                output = stdout.read().decode()
                error = stderr.read().decode()
                print("set  OUTPUT :- ",output)
                print("set ERROR :- ",error)
                
                if error:
                    print(f"Error setting refresh for screen {i}: {error}")
                else:
                    print(f"Refresh set for screen {i}: {output}")   
    except Exception as e:
        print(f"Exception while setting refresh: {e}")

    


app = Flask(__name__)
CORS(app)  


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/check-connection', methods=['POST'])
def check_connection():
    data = request.json
    ip = data.get('ip')
    username = data.get('username')
    password = data.get('password')

    if not all([ip, username, password]):
        return jsonify({"success": False, "error": "Missing required fields"}), 400
    try:
        ssh = ssh_connect(ip, username, password)
        stdin, stdout, stderr = ssh.exec_command('echo "Connected"')
        output = stdout.read().decode().strip()
        ssh.close()

        if "Connected" in output:
            return jsonify({"success": True})
        else:
            return jsonify({"success": False, "error": "Unexpected output from master node"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/execute-command', methods=['POST'])
def execute_command():
    data = request.json
    ip = data.get('ip')
    username = data.get('username')
    password = data.get('password')
    command = data.get('command')
    machine_count = data.get('machine_count')

    if command == "show_logo":
        return show_logo(ip, username, password, 'https://i.imgur.com/j3hL9Ka.png',machine_count)
    elif command == "clear_logo":
        return clear_logo(ip, username, password,machine_count)
    elif command == "lg_relaunch":
        return relaunch(ip, username, password)
    elif command == "show_kml":
        return asyncio.run(show_kml(ip, username, password))
    elif command == "power_off__lg":
        return power_off_lg(ip,username,password)
    elif command == "reboot_lg":
        return reboot_lg(ip,username,password)
    elif command == "clear_kml":
        return clear_kml(ip,username,password)
    else:
        return jsonify({"success": False, "error": "No command Found"}), 500




def clear_kml(ip, username, password):
    try:
        ssh = ssh_connect(ip, username, password)
        clear_kml = ""
        
        #clear KML command
        command = f"echo ' ' > /tmp/query.txt"
        stdin, stdout, stderr = ssh.exec_command(command)
        output = stdout.read().decode() 
        error = stderr.read().decode()
        print("OUTPUT CLEAR KML :- ",output)
        print("ERROR CLEAR KML :- ",error)

        return jsonify({"success": True, "message": "KML cleared successfully"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500



def reboot_lg(ip,username,password):
    try:
        ssh = ssh_connect(ip, username, password)
        for i in range(3,0,-1):
            command = f'sshpass -p {password} ssh -t lg{i} "echo {password} | sudo -S reboot"'
            stdin, stdout, stderr = ssh.exec_command(command)
            output = stdout.read().decode().strip()    
        ssh.close()
        return jsonify({"success": True, "message": "Relaunched successfully"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


def power_off_lg(ip,username,password):
    try:
        ssh = ssh_connect(ip, username, password)
        for i in range(3,0,-1):
            command = f'sshpass -p {password} ssh -t lg{i} "echo {password} | sudo -S poweroff"'
            stdin, stdout, stderr = ssh.exec_command(command) 
            output = stdout.read().decode().strip()    
        ssh.close()
        
        return jsonify({"success": True, "message": "Relaunched successfully"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500



def relaunch(ip, username, password):
    try:
        asyncio.run(relaunch_screens(3,ip, username, password))
        return jsonify({"success": True, "message": "Relaunched successfully"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500



def show_logo(ip, username, password, image_url,machine_count):
    try:
        print("Show LOGO Function CALLED !!!!")
        ssh = ssh_connect(ip, username, password)

        # Create KML to display the image
        display_kml = DISPLAY_KML_TEMPLATE.format(image_url=image_url)
        print("##############",machine_count)
        slave_id = int((int(machine_count)/2))+2
        
        
        slave_kml_path = SLAVE_KML_TEMPLATE.format(slave_id)
        update_kml_file(ssh, display_kml, slave_kml_path)
            
        result = refresh_slaves(ssh,ip,username,password,slave_id)
        #print("SHOW LOGO RESULT : -  ",result)
        print(f"Image displayed on Slave {slave_id}.")
        return jsonify({"success": True, "message": "Logo displayed on all nodes successfully"})
    
    except subprocess.CalledProcessError as e:
        return jsonify({"success": False, "error": f"Command failed: {e}"}), 500
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

def clear_logo(ip, username, password,machine_count):
    try:
        ssh = ssh_connect(ip, username, password)
        clear_kml = CLEAR_KML_TEMPLATE
        print("##############",machine_count)
        slave_id = int((int(machine_count)/2))+2
        
        #Displaying Logo on Left Most Screen
        slave_kml_path = SLAVE_KML_TEMPLATE.format(slave_id)
        update_kml_file(ssh, clear_kml, slave_kml_path)
        result = refresh_slaves(ssh,ip,username,password,slave_id)
        print(f"Logo cleared from Slave {slave_id}.")

        return jsonify({"success": True, "message": "Logo cleared from all nodes successfully"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500



async def show_kml(ip, username, password):
    
    try:
        # Send the command to update the KML file on the master node
        command = f"echo 'search=india' > {QUERY_FILE_PATH}"
        output =  await send_command(ip, username, password, command)
        print("##########")
        print(output)
        print("########")
        

        if output is not None:
            print(f"KML successfully updated. Output: {output}")
            return jsonify({"success": True, "message": "KML displayed successfully"})
        else:
            return jsonify({"success": False, "error": "Failed to send the command to the master node"})

    except FileNotFoundError:
        return jsonify({"success": False, "error": f"KML file not found: "}), 404
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


async def relaunch_screens(screen_amount, ip, username, password):
    for i in range(3, 0,-1):  # Loop through all screens
        try:
            # Command to execute the lg-relaunch script
            lg_relaunch_command = f"/home/{username}/bin/lg-relaunch > /home/{username}/log.txt"

            # Command to determine the display manager and restart it
            relaunch_command = """
if [ -f /etc/init/lxdm.conf ]; then
    export SERVICE=lxdm
elif [ -f /etc/init/lightdm.conf ]; then
    export SERVICE=lightdm
else
    exit 1
fi
if [[ $(service $SERVICE status) =~ 'stop' ]]; then
    echo {} | sudo -S service $SERVICE start
else
    echo {} | sudo -S service $SERVICE restart
fi
""".format(password, password)

            # Combine the commands
            full_command = f"{lg_relaunch_command}; {relaunch_command}"

            # Execute the command on the remote screen
            ssh = ssh_connect(f"lg{i}", username, password)
            stdin, stdout, stderr = ssh.exec_command(full_command, get_pty=True)
            stdin.write(f"{password}\n")  # Send the password to sudo
            stdin.flush()

            output = stdout.read().decode()
            error = stderr.read().decode()

            if error:
                print(f"Error relaunching screen {i}: {error}")
            else:
                print(f"Screen {i} relaunched successfully: {output}")

            ssh.close()
        except Exception as e:
            print(f"Exception while relaunching screen {i}: {e}")

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=7000)
