#!/usr/bin/python3
import os, sys, shlex
import argparse
import subprocess
"""This script deploys your docker-compose file as an azure webapp

Remember that the image names in your docker-compose file must include the complete acr registry path

Pull image rights to the ACR are included three times (!) with three different methods
This is thanks to micro$ofts confusing and contradicting documentation on the subject.

- acr passwd and username are given to "az webapp create"
- the webapp is given a system assigned identity and that identity has rights to do AcrPull on the ACR
- finally, environmental variables having the ACR credentials are also included to the webapps env vars (!)

Script does this:

1. Gets the ACR password
2. Creates the webapp (acr credentials are passed as args) [this stage can be skipped]
3. Creates system administered identity to the webapp
4. Gives AcrPull rights to (3)
5. Sets webapps env variables based on your provided env file (again acr credentials are added)
6. Restarts the webapp
7. Writes tailogs.bash convenience script

Good luck!
"""
parser = argparse.ArgumentParser(description="Deploys a webapp.  Please read source code for mode info")
parser.add_argument("--env_file", help="Path to the env file", required=True)
parser.add_argument("--name", help="Name of the Azure Web App", required=True)
parser.add_argument("--group", help="Name of the Azure Resource Group", required=True)
parser.add_argument("--plan", help="Name of the webapp plan", required=True)
parser.add_argument("--reg", help="Name of the ACR registry", required=True)
parser.add_argument("--docker_compose_file", help="Docker compose .yml file", required=True)
parser.add_argument("--skip_create", action="store_true", help="Skips creating the webapp, but does everything else", default=False)

def runComm(comm):
    # Run the command and capture the output
    # print(comm)
    result = subprocess.run(comm, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        # print("ERROR", result.returncode)
        print(result.stderr)
        sys.exit(result.returncode)
    return result.stdout.strip()

def writeLogScript(p):
    with open("tailogs.bash", "w") as f:
        f.write(f"#!/bin/bash\n")
        f.write(f"az webapp log tail --name {p.name} --resource-group {p.group}\n")
    os.system("chmod a+x tailogs.bash")

def loadEnvs(env_file_path):
    # Load environment variables from the specified .env file
    env_vars = {}
    with open(env_file_path, 'r') as env_file:
        for line in env_file:
            line = line.strip()
            if line and not line.startswith('#'):
                key, value = line.split('=', 1)
                env_vars[key] = value
    return env_vars

def setEnvs(p, env_vars):
    # Build the Azure CLI command
    command = f"az webapp config appsettings set --name {p.name} --resource-group {p.group} --settings "
    # Add environment variables to the command
    for key, value in env_vars.items():
        value_ = value.strip('"') # remove quotes
        command += f'{key}="{value_}" '
    # print(command)
    # os.system(command)
    runComm(command)


# Parse the command-line arguments
p = parser.parse_args()

acr_url=f"https://{p.reg}.azurecr.io"

print("1. Getting ACR password")
acr_password = runComm(f"""az acr credential show 
--resource-group {p.group} 
--name {p.reg} 
--query "passwords[?name == 'password'].value" --output tsv
""".replace("\n"," "))

# writeLogScript(p) # quicktest
# sys.exit(2)

if p.skip_create:
    print("2. WARNING: SKIPPING WEBAPP CREATION")
else:
    print("2. Creating webapp")
    runComm(f"""az webapp create 
    --resource-group {p.group} 
    --plan {p.plan} 
    --name {p.name} 
    --multicontainer-config-type COMPOSE 
    --multicontainer-config-file {p.docker_compose_file} 
    --container-registry-user {p.reg} 
    --container-registry-password {acr_password}""".replace("\n"," "))
    # it's stupid that the webapp starts right away before we can set it's env variables
    # stupid, stupid

print("3. Creating webapp sys identity")
runComm(f"""az webapp identity 
assign -g {p.group} -n {p.name}
""".replace("\n"," "))

# get the ids
app_identity_id=runComm(f"""
az webapp identity show --name {p.name}
--resource-group {p.group}
--query "principalId" --output tsv
""".replace("\n"," "))
subs_id=runComm("""
az account show --query id --output tsv
""".replace("\n"," "))

print("app_identity_id:", app_identity_id)
print("subs_id:", subs_id)

print("4. Giving sys identity rights to do AcrPull")
runComm(f"""
az role assignment create
--role AcrPull
--assignee {app_identity_id}
--scope /subscriptions/{subs_id}/resourceGroups/{p.group}/providers/Microsoft.ContainerRegistry/registries/{p.reg}
""".replace("\n"," "))

print("5. Setting webapp env variables")
env_vars=loadEnvs(p.env_file)
# include docker registry login env vars
env_vars["DOCKER_REGISTRY_SERVER_PASSWORD"]=acr_password
env_vars["DOCKER_REGISTRY_SERVER_URL"]=acr_url
env_vars["DOCKER_REGISTRY_SERVER_USERNAME"]=p.reg
setEnvs(p, env_vars)

print("6. Restarting webapp")
runComm(f"""
az webapp restart --name {p.name} --resource-group {p.group}
""".replace("\n"," "))

print("7. Writing tailogs.bash for your convenience, Sir!")
writeLogScript(p)

print("Have a nice day!")
