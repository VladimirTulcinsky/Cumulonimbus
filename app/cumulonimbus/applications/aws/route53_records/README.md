# Route53 Records — Sensitive Data in DNS

**Provider**: AWS  
**Difficulty**: Beginner  
**MITRE ATT&CK**: [T1526 — Cloud Service Discovery](https://attack.mitre.org/techniques/T1526/)

## Scenario

You have obtained AWS credentials for an IAM user. The user has read access to Route53. A developer has stored a sensitive value in a DNS TXT record inside a private hosted zone.

## Objective

Retrieve the flag hidden in a Route53 DNS record.

## Permissions

The attacker IAM user has the following permissions:

- `route53:ListHostedZones`
- `route53:ListHostedZonesByName`
- `route53:GetHostedZone`
- `route53:ListResourceRecordSets`

## Attack Path

1. Configure AWS CLI with the provided credentials.
2. List hosted zones to find the target zone ID:
   ```bash
   aws route53 list-hosted-zones
   ```
3. List all resource record sets in the hosted zone:
   ```bash
   aws route53 list-resource-record-sets --hosted-zone-id <zone-id>
   ```
4. Locate the TXT record — its value contains the flag.

## Flag

`CUMULONIMBUS{R0ut353_TXT_R3c0rd_S3cr3ts}`

## Remediation

- Do not store secrets, tokens, or sensitive strings in DNS records.
- Apply least-privilege IAM policies — restrict Route53 access to specific hosted zones using resource ARNs.
- Audit hosted zone records periodically for sensitive data exposure.

## MITRE ATT&CK Mapping

| Technique ID | Technique Name | Tactic |
|---|---|---|
| [T1016](https://attack.mitre.org/techniques/T1016/) | System Network Configuration Discovery | Discovery |
| [T1590.002](https://attack.mitre.org/techniques/T1590/002/) | Gather Victim Network Information: DNS | Reconnaissance |
