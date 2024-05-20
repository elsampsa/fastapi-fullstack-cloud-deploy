#!/bin/bash
#
# run first docker-compose -f filename build [--no-cache]
#
group=your-resource-group
reg=your-acr-registry # $reg.azurecr.io
imgnames="fapi-azure-backend fapi-azure-backend"

export ACR_PASSWORD=$(az acr credential show \
--resource-group ${group} \
--name ${reg} \
--query "passwords[?name == 'password'].value" \
--output tsv)

echo "DOCKER LOGIN"
docker login $reg.azurecr.io --username $reg --password $ACR_PASSWORD

echo "TAGGING & PUSHING IMAGES"
for imgname in $imgnames
do
    echo "IMAGE:"$imgname
    docker tag $imgname:latest $reg.azurecr.io/$imgname:latest
    docker push $reg.azurecr.io/$imgname:latest
done
