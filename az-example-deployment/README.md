
## Intro

Here we deploy the (official) fastapi fullstack example as an Azure (multi-container) webapp into the cloud.

The deployment is highly automatized, using scripts that in turn use the ``az`` command-line program.

This example scraps the traefik reverse-proxy server and postgresql server from the original example.  Instead, an azure-managed
postgresql server is used.

*This is a pretty simple auto-deployment of a fullstack app into Azure, i.e. it is not a "professional" CI/CD example.*

## Overview

The idea is, that you have one of these directories *as per* each of your azure
deployment.   This directory defines your azure deployment with all the env
variables, helper scripts, etc.

*What's in here?*
``` 
notes.md                    # general stuff about azure deployment
                            # documentation, commands and links to m$ docs

test-template.env           # TODO: copy into test.env & modify (see below)
cloud-template.env          # TODO: copy into cloud.env & modify (see below)
deploy-template.bash        # TODO: copy into deploy.bash & modify (see below)
push-template.bash          # TODO: copy into push.bash & modify (see below)
cloud-deployment-template.yml        
                            # TODO: copy into cloud-deployment.yml & modify (see below)

az-test-deployment.yml      # docker-compose file you can run locally
test.env                    # used by az-test-deployment.yml
                            # TODO: Sensitive information create by YOU
                            # never include into commit

cloud-deployment.yml        # a stripped-down/adapted version of az-test-deployment.yml
                            # used for actual deployment
cloud.env                   # use by cloud-deployment.yml
                            # TODO: Sensitive information create by YOU
                            # never include into commit

deploy.bash                 # TODO: Sensitive information create by YOU
                            # never include into commit
                            # Runs ../azdeploy.py for deploying your multi-
                            # container app as azure webapp

push.bash                   # TODO: Sensitive information create by YOU
                            # never include into commit
                            # tags & pushes your docker images from local to your ACR
```

## Step-by-step

### 1. Azure requirements
- subscription
- resource group
- webapp plan
- your own private ACR (azure docker registry)
- an azure managed postgresql server

These steps are done most conveniently from the Azure web GUI (they are not-that-repetitive)

For more details, you can see [notes.md](notes.md).

### 2. Azure login
```bash
az login
```
And check that you are using the correct subscription

### 3. Templating

Create env & yml files and bash scripts from the templates and as instructed above.

### 4. Run fastapi locally 

- Run in your local computer the original fastapi fullstack example
- Run the the fullstack example *again* with `az-test-deployment.yml` (see above) and see that it works ok, i.e.:
  ```bash
  docker-compose -f az-test-deployment.yml up
  ```
- Now you should have images `fapi-azure-backend` and `fapi-azure-frontend` in your local docker

### 5. Push 

Push `fapi-azure-backend` and `fapi-azure-frontend` into the ACR.  You can use the convenience script `push.bash`
(see above)

### 6. Deploy

Run
```bash
./deploy.bash
```
This command uses [../azdeploy.py](../azdeploy.py) and
automatizes many of the repetitive steps that you don't really
want to do from the azure web UI.

Although the ACR authentization by m$ is confusing, it has been automatized here for you.  Please read the notes
about that in [../azdeploy.py](../azdeploy.py) source code.

## Workflow

In your app's azure page, there is a tab named "Activity log".  Keep an eye on it to see
how things are progressing. Remember that Azure deployment can be kinda slow.

## Notes

WARNING: the initial password is set only once!  If you don't clear the db, changing the env variable 
`FIRST_SUPERUSER_PASSWORD` doesn't have any effect.

## FAQ

While running, `deploy.bash` I get:
```bash
ERROR: Cannot find user or service principal in graph database for
```
Woopsie - stuff has not propagated fast enough in Azure.  Just run `deploy.bash` again.  Before that,
you might want to add `--skip_create` to the last argument calling `azdeploy.py`.
