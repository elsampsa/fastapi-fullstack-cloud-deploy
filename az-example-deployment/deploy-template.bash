#!/bin/bash
../azdeploy.py \
    --group=your-resource-group \
    --name=yourapp \
    --plan=your-webplan \
    --reg=your-acr-registry \
    --docker_compose_file=cloud-deployment.yml \
    --env_file=cloud.env
# add --skip_create to the last line if you want
# to skip app creation
# NOTE: your-acr-registry is the name of the registry 
# WITHOUT ".azurecr.io"
