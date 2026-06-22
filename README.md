# zeiss-assesment
zeiss assesment Muhammad Ali DevOps

1. iac-arm contains
    a. rg-scope: To create Resources in the RG
    b. subscription-scope: To create Resource groups
2. api folder contains
    a. A simple Python API app
3. scripts:
    a. Contains script to create connection b/w Azure container registry and GitHub



Pending:
    1. Enable managed identity and add Azure service bus data roles and modify api to use that
    2. Add deployment in github action workflow


Need to set below env variables in GitHub:
1. AZURE_CLIENT_ID          : az ad app list --display-name <app_reg_name> --query "[0].appId" -o tsv  (github-zeiss-assessment)
#client id of the SP b/w github and ACR
2. AZURE_SUBSCRIPTION_ID    : az account show --query id -o tsv 
3. AZURE_TENANT_ID          : az account show --query tenantId -o tsv
4. ACR_NAME                 : ACR Name from iac deployment output
5. CONTAINER_APP_NAME       : Container app name from iac deployment output
6. RESOURCE_GROUP           : Resource Group name from iac deployment output
7. OBJ_ID                   : az ad sp show --id $AZURE_CLIENT_ID --query id -o tsv