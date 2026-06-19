#!/bin/bash

#parameter file and template file location
PARAMETER_FILE="iac-arm/subscription-scope/rg.parameters.json"
TEMPLATE_FILE="iac-arm/subscription-scope/rg.json"

#takes the name of Resource group from the paramater file
RG_NAME=$(jq -r '.parameters.resourceGroupName.value' "$PARAMETER_FILE")

echo "Checking Resource Group: ${RG_NAME}"

#checks whether rg exists, if not will create one
if az group exists --name "${RG_NAME}" | grep -q true; then
    echo "Resource Group exists. Skipping creation."
else
    echo "Creating Resource Group: ${RG_NAME}"

    OUTPUT=$(az deployment sub create \
        --location centralindia \
        --template-file "$TEMPLATE_FILE" \
        --parameters "$PARAMETER_FILE" \
        2>&1)

    #checks if previous command suceeded
    if [ $? -eq 0 ]; then
        echo "RG ${RG_NAME} created successfully."
    else
        echo "Failed to create RG ${RG_NAME}"
        echo "$OUTPUT"
        exit 1
    fi
fi