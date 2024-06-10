#!/usr/bin/python3
import os
import argparse
import subprocess

def create_secret_from_env(secret_name, namespace, env_file):
    # Initialize the command string
    command = f"kubectl create secret generic {secret_name} -n {namespace}"

    # Read the .env file and append each environment variable to the command string
    with open(env_file, "r") as file:
        for line in file:
            line = line.strip()
            # Ignore empty lines and comments
            if not line or line.startswith("#"):
                continue
            # Extract the variable name and value
            var, val = line.split("=", 1)
            # Append to the command string
            command += f" --from-literal={var}={val}"

    # Print the command to the terminal
    # print("Generated command:")
    print()
    print(command)
    print()
    # Execute the command
    result = subprocess.run(command, shell=True, capture_output=True) # , check=True)
    if result.returncode != 0:
        # print(">>", result.stderr.decode())
        if "already exists" in result.stderr.decode():
            print("WARNING: that secret already exists - will remove it & rerun")
            subprocess.run(f"kubectl delete secret {secret_name} -n {namespace}", shell=True, check=True)
            print("WARNING: please run this command again") # we could recurse, but..
    else:
        print("SUCCESS!")

if __name__ == "__main__":
    # Setup argparse
    parser = argparse.ArgumentParser(description='Create a Kubernetes secret from a .env file.')
    parser.add_argument('--secret-name', required=True, help='The name of the Kubernetes secret.')
    parser.add_argument('--namespace', required=False, help='The namespace for the Kubernetes secret.', default="default")
    parser.add_argument('--env-file', required=True, help='The path to the .env file.')
    # Parse arguments
    args = parser.parse_args()
    # Create the secret from the .env file
    create_secret_from_env(args.secret_name, args.namespace, args.env_file)
