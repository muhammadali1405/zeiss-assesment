#!/bin/bash

#parameter file and template file location to create resources
RES_PARAMETER_FILE="rg-scope/main.parameters.json"
RES_TEMPLATE_FILE="rg-scope/main.json"

#parameter file and template file location to create resources
RG_NAME="rg-zeiss-assessment-01"

echo "Checking Resource Group: ${RG_NAME}"

# checks whether rg exists
if az group exists --name "${RG_NAME}" | grep -q true; then


echo "Deploying resources to Resource Group: ${RG_NAME}"
DEPLOYMENT_NAME="zeiss-deployment-$(date +%Y%m%d-%H%M%S)"

OUTPUT=$(az deployment group create \
    --name "$DEPLOYMENT_NAME" \
    --resource-group "${RG_NAME}" \
    --template-file "$RES_TEMPLATE_FILE" \
    --parameters @"$RES_PARAMETER_FILE" \
    2>&1)

# checks if previous command succeeded
if [ $? -eq 0 ]; then
    echo "Resources deployed successfully."
else
    echo "Failed to deploy resources."
    echo "$OUTPUT"
    exit 1
fi

else

echo "Resource Group '${RG_NAME}' does not exist."
echo "Please create the Resource Group first."
exit 1

fi

echo "Deployment Results:"
az deployment operation group list \
    --resource-group "$RG_NAME" \
    --name "$DEPLOYMENT_NAME" \
    --query "[].{
        Resource: properties.targetResource.resourceName,
        Type: properties.targetResource.resourceType,
        Status: properties.provisioningState
    }" -o table