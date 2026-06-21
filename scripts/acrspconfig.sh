set -x

az ad app create --display-name github-zeiss-assessment

APP_ID=$(az ad app list \
  --display-name github-zeiss-assessment \
  --query "[0].appId" -o tsv)

echo $APP_ID

az ad sp create --id $APP_ID

ACR_ID=$(az acr show \
  --name acrzeissassesment003 \
  --query id \
  -o tsv)

az role assignment create \
  --assignee $APP_ID \
  --role AcrPush \
  --scope $ACR_ID

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