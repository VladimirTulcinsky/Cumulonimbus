#!/bin/bash
# Cumulonimbus welcome banner — sourced by /root/.bashrc on container start

R='\033[0m'
BOLD='\033[1m'
DIM='\033[2m'
YEL='\033[93m'
WHT='\033[97m'
CYN='\033[36m'
ORG='\033[38;5;208m'
BLU='\033[34m'
GRY='\033[90m'
GRN='\033[32m'
RED='\033[31m'

HR="${GRY}  ══════════════════════════════════════════════════════════════════${R}"

echo -e ""
echo -e "$HR"
echo -e ""
echo -e "   ${YEL}${BOLD}⚡${R}  ${BOLD}${WHT}CUMULONIMBUS${R}"
echo -e "       ${DIM}${CYN}A VULNERABLE CLOUD ENVIRONMENT${R}"
echo -e ""
echo -e "       ${ORG}${BOLD}■ AWS${R}  ${GRY}│${R}  ${BLU}${BOLD}■ AZURE${R}    ${DIM}24 AWS labs · 31 Azure labs${R}"
echo -e ""
echo -e "$HR"
echo -e ""
echo -e "   ${BOLD}${WHT}Prerequisites${R}"
echo -e ""
echo -e "   ${ORG}${BOLD}AWS${R}   ${GRN}✓${R}  AdministratorAccess"
echo -e ""
echo -e "   ${BLU}${BOLD}Azure${R} ${GRN}✓${R}  Global Administrator (Entra ID)"
echo -e "         ${GRN}✓${R}  Owner on target subscription"
echo -e "         ${GRN}✓${R}  Key Vault Administrator on target subscription"
echo -e "         ${GRN}✓${R}  Security defaults: ${RED}DISABLED${R}"
echo -e "         ${GRN}✓${R}  Microsoft Graph app permissions ${DIM}(admin consented)${R}:"
echo -e "            ${DIM}User.ReadWrite.All · Application.ReadWrite.All · Directory.ReadWrite.All${R}"
echo -e ""
echo -e "$HR"
echo -e "   ${DIM}cnimbus -h   │   cnimbus azure -h   │   cnimbus aws -h${R}"
echo -e "$HR"
echo -e ""
