set -x

ACR_NAME="acrzeissdev2"

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

RG_ID=$(az group show \
  --name rg-zeiss-assessment-01 \
  --query id \
  -o tsv)

#add contributer to deploy
az role assignment create \
  --assignee $APP_ID \
  --role Contributor \
  --scope $RG_ID
