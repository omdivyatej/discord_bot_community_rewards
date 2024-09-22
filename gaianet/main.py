import paramiko
import re
import json

# -----------------------------------------
# Step 1: Extract the required information
# -----------------------------------------

# The provided text


def update_knowledge_base(text):
    # Extract the JSON string from the text
    json_match = re.search(r'\{[\s\S]*?\}', text)
    if json_match:
        json_str = json_match.group()
        try:
            config_data = json.loads(json_str)
            snapshot_link = config_data.get('snapshot')
            embedding_ctx_size = config_data.get('embedding_ctx_size')
            if not snapshot_link or not embedding_ctx_size:
                raise ValueError("Required data not found in JSON.")
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            exit(1)
        except ValueError as e:
            print(f"Error: {e}")
            exit(1)
    else:
        print("No JSON found in the provided text.")
        exit(1)

    print("Extracted snapshot link:", snapshot_link)
    print("Extracted embedding_ctx_size:", embedding_ctx_size)

    # -----------------------------------------
    # Step 2: SSH into the server and execute commands
    # -----------------------------------------

    # SSH connection details
    hostname = 'ec2-13-56-58-191.us-west-1.compute.amazonaws.com'
    username = 'ubuntu'
    # Update with the correct path to your key
    private_key_path = "D:\KayaPay\gaia-v4.pem"

    print(f"Snapshot link: {snapshot_link}")
    print(f"Embedding context size: {embedding_ctx_size}")
    # Commands to execute
    command = f'bash -l -c "cd gaianet && gaianet config --snapshot \'{snapshot_link}\' --embedding-ctx-size {embedding_ctx_size} && gaianet stop && gaianet init && gaianet start"'

    # Initialize SSH client
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        # Load the private key
        key = paramiko.RSAKey.from_private_key_file(private_key_path)

        print(f"Connecting to {hostname}...")
        ssh.connect(hostname=hostname, username=username, pkey=key)
        print("Connected.")

        print(f"Executing command: {command}")
        stdin, stdout, stderr = ssh.exec_command(command)

        # Read output and errors
        output = stdout.read().decode()
        errors = stderr.read().decode()

        if output:
            print("Output:")
            print(output)
        if errors:
            print("Errors:")
            print(errors)

    except paramiko.ssh_exception.AuthenticationException as auth_err:
        print(f"Authentication failed: {auth_err}")
    except paramiko.SSHException as ssh_err:
        print(f"SSH error: {ssh_err}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        ssh.close()
