#!/bin/bash
./azdeploy.py \
    --group=your-resource-group \
    --name=yourapp \
    --plan=your-webplan \
    --reg=your-acr-registry \
    --docker_compose_file=cloud-deployment.yml \
    --env_file=cloud.env
#--skip_create
