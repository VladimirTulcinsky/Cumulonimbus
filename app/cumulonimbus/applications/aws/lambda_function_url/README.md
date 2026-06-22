# Lambda Function URL — No Authentication

**Provider:** AWS | **Category:** Serverless / Exposure

## Scenario

A developer deployed an internal diagnostics Lambda function and exposed it via a
**Lambda Function URL** configured with `AuthType: NONE`. This makes the function
publicly accessible to anyone on the internet without any AWS credentials.

The function was intended only for internal health checks, but because it returns
sensitive data in the response body, any unauthenticated caller can retrieve it.

## Attack Path

```
[Attacker] No credentials required
    |
    v
Discover the function URL (e.g. from terraform output / misconfigured CI artifact)
    |
    v
curl <function_url>  -->  JSON response with flag
```

### Step 1 — Call the function URL

```bash
FUNCTION_URL="<function_url>"

curl -s "${FUNCTION_URL}" | jq .
```

The response contains:

```json
{
  "message": "Internal diagnostics endpoint",
  "flag": "CUMULONIMBUS{L4mbd4_Funct10n_URL_N0_Auth}"
}
```

## How to Fix in Production

1. **Set `AuthType: AWS_IAM`** on the Function URL — this requires callers to sign
   requests with valid AWS credentials using SigV4.
2. **Use API Gateway** instead of Function URLs for public-facing functions, and add
   an authorizer (Cognito, Lambda, or IAM).
3. **Never expose internal diagnostic endpoints** publicly — use VPC endpoints or
   restrict the function URL CORS policy and add IP-based conditions via Lambda@Edge.
4. **Audit all Lambda Function URLs** in your account:
   ```bash
   aws lambda list-function-url-configs --function-name <name> \
     --query "FunctionUrlConfigs[?AuthType=='NONE']"
   ```

## MITRE ATT&CK Mapping

| Technique | ID |
|---|---|
| Exploit Public-Facing Application | [T1190](https://attack.mitre.org/techniques/T1190/) |
| Cloud Infrastructure Discovery | [T1580](https://attack.mitre.org/techniques/T1580/) |
| Data from Cloud Storage | [T1530](https://attack.mitre.org/techniques/T1530/) |
