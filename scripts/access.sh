set -x

ACR_NAME="acrzeissdev59"

#create app registration
az ad app create --display-name github-zeiss-assessment

#get client id of the app reg created
APP_ID=$(az ad app list \
  --display-name github-zeiss-assessment \
  --query "[0].appId" -o tsv)

# echo $APP_ID

#create service principle for the app reg
az ad sp create --id $APP_ID

#get the Resource ID of the ACR
ACR_ID=$(az acr show \
  --name $ACR_NAME \
  --query id -o tsv)

#assign access to push image to acr for the App registration created
az role assignment create \
  --assignee $APP_ID \
  --role AcrPush \
  --scope $ACR_ID

#create federated credential with the github and my user
az ad app federated-credential create \
  --id $APP_ID \
  --parameters '{
    "name": "github-main",
    "issuer": "https://token.actions.githubusercontent.com",
    "subject": "repo:muhammadali1405/zeiss-assesment:ref:refs/heads/main",
    "audiences": [
      "api://AzureADTokenExchange"
    ]
  }'

#get rg id to add access
RG_ID=$(az group show \
  --name rg-zeiss-assessment-01 \
  --query id \
  -o tsv)

#Added in ARM
#add Container Apps Contributor to deploy
# az role assignment create \
#   --assignee $APP_ID \
#   --role "358470bc-b998-42bd-ab17-a7e34c199c0f" \
#   --scope $RG_ID

# az role assignment create \
#   --assignee $APP_ID \
#   --role Contributor \
#   --scope $RG_ID

# az role assignment create \
#   --assignee $APP_ID \
#   --role "User Access Administrator" \
#   --scope $RG_ID
