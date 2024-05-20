# Azure Notes

*These are just some notes, NOT a tutorial*

## Azure CLI commands to deploy a multicontainer web app

Before starting to work in the shell, do
```bash
az login
```
### 0. Variables

```bash
group=
name=
plan=
reg= # complete address will be: $reg.azurecr.io.  Here, just put the reg part
vnet= # virtual network name
```

All non-repetitive tasks are best done at the web UI, repetitive tasks
at the CLI.

### 1. Create Resource Group (RG)

Best done at the web ui.

```bash
az group create --name $group --location eastus
```
You must be *owner* of the resource group.

### 2. Create Container Registry (ACR)

Best done at the web ui.

```bash
az acr create --resource-group $group --name $reg --sku Basic --admin-enabled true
```

Get the ACR's password into an env variable:
```bash
export ACR_PASSWORD=$(az acr credential show \
--resource-group ${group} \
--name ${reg} \
--query "passwords[?name == 'password'].value" \
--output tsv)
```

### 3. Build or Push Docker Image

Push docker image from local to ACR or build it directly into the ACR.

Repetitive task: done more conveniently at CLI.

Login to docker:
```bash
docker login $reg.azurecr.io --username $reg --password $ACR_PASSWORD
```

Build directly at the ACR:
```bash
az acr build --resource-group $group --registry $reg --image $imgname:latest .
```

OR

Only push to the ACR:
```bash
docker tag $imgname:latest $reg.azurecr.io/$imgname:latest
docker push $reg.azurecr.io/$imgname:latest
```

### 4. Create Application Plan

Best done at the web ui.

```bash
az appservice plan create --name $plan --resource-group $group --sku B1 --is-linux
```

### 5. Create Application

Repetitive task: done more conveniently at CLI.

Single-image (note: set `imgname` env variable first):
```bash
az webapp create --resource-group $group --plan $plan --name $name \
    --deployment-container-image-name $reg.azurecr.io/$imgname:latest \
```

Multi-image (emphasis here is in the multi-image app):
```bash
az webapp create --resource-group $group --plan $plan --name $name \
    --multicontainer-config-type COMPOSE \
    --multicontainer-config-file docker-compose-azure.yml \
    --container-registry-user $reg \
    --container-registry-password $ACR_PASSWORD
```

Some extra arguments if required:
```bash
--vnet $vnet \
--subnet default
```

Links:

- https://learn.microsoft.com/en-us/cli/azure/webapp?view=azure-cli-latest
- https://learn.microsoft.com/en-us/cli/azure/containerapp?view=azure-cli-latest
- https://learn.microsoft.com/en-us/azure/app-service/tutorial-multi-container-app

NOTE: For multi-image, your `docker-compose-azure.yml` (above) image names need to include the custom registry name

Give the application a system-assigned identity:
```bash
az webapp identity assign -g $group -n $name
```

Now it's "agentic" and it can be given user rights

Let's get some ids:
```bash
export app_identity_id=$(az webapp identity show --name $name --resource-group $group --query "principalId" --output tsv)
export subs_id=$(az account show --query id --output tsv)
```

Give the app pull access rights to the custom docker registry:
```bash
az role assignment create \
    --role AcrPull \
    --assignee $app_identity_id \
    --scope /subscriptions/$subs_id/resourceGroups/$group/providers/Microsoft.ContainerRegistry/registries/$reg
```
NOTE: I think this gives the *app* itself rights to do acr pull?

Or from the web-UI:

- Go to docker registry & choose IAM.
- There go to "Add Role Assignment".  This grants resources to the repo.  Choose `AcrPull` & click Next.
- "Assign access to Managed Identity" --> "Select Members" --> choose the webapp

### 6. Setting App Environmental Variables

Repetitive task: this is most conveniently done from the command line:
```bash
az webapp config appsettings set --name $name --resource-group $group --settings \
DOMAIN="some-domain" \
ENVIRONMENT="staging" \
BACKEND_CORS_ORIGINS="http://etc" \
SECRET_KEY="changeme" \
POSTGRES_SERVER="name.postgres.database.azure.com" \
POSTGRES_PORT="5432" \
POSTGRES_DB="postgres" \
POSTGRES_USER="postgres" \
POSTGRES_PASSWORD="changeme" \
# etc. environmental variables your running containers need
```

### 7. Logging

App:
```bash
az webapp log tail --name $name --resource-group $group
```

Deployment: (but doesn't seem to work):
```bash
az webapp log deployment show --name $name --resource-group $group
```

If deployment logs are not avail, they can be fetched from here:
```
https://$name.scm.azurewebsites.net/api/logs/docker/zip
```

Links:
- https://learn.microsoft.com/en-us/cli/azure/webapp/log?view=azure-cli-latest#az-webapp-log-tail
- https://learn.microsoft.com/en-us/azure/app-service/troubleshoot-diagnostic-logs#enable-application-logging-linuxcontainer

### 8. PostgreSQL Config

Had success with [1](https://stackoverflow.com/questions/75952510/operationalerror-server-closed-the-connection-unexpectedly), but
better one would be [2](https://stackoverflow.com/questions/76602470/how-to-connect-a-azurecontainerapp-to-an-azure-hosted-postgresql-flexible-server).

Config (1) makes it available to the whole internet (!)

## Some more random stuff

- [Webapp autostart when containers are update](https://stackoverflow.com/questions/76151530/how-can-i-force-an-azure-web-app-to-re-pull-its-container)

*Create Managed Identity*

```bash
az identity create --name $idname --resource-group $group
```

