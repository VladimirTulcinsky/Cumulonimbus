#!/bin/bash
# Cumulonimbus welcome banner — sourced by /root/.bashrc on container start

R='\033[0m'          # reset
BOLD='\033[1m'
DIM='\033[2m'
YEL='\033[93m'       # bright yellow  (lightning)
WHT='\033[97m'       # bright white   (title)
CYN='\033[36m'       # cyan           (tagline)
ORG='\033[38;5;208m' # orange         (AWS)
BLU='\033[34m'       # blue           (Azure)
GRY='\033[90m'       # dark grey      (borders)
GRN='\033[32m'       # green          (checkmarks)
RED='\033[31m'       # red            (warnings)

echo -e ""
echo -e "${GRY}  ╔══════════════════════════════════════════════════════════════════╗${R}"
echo -e "${GRY}  ║${R}                                                                  ${GRY}║${R}"
echo -e "${GRY}  ║${R}   ${YEL}${BOLD}⚡${R}  ${BOLD}${WHT}C U M U L O N I M B U S${R}                                      ${GRY}║${R}"
echo -e "${GRY}  ║${R}       ${DIM}${CYN}A  V U L N E R A B L E  C L O U D  E N V I R O N M E N T${R}    ${GRY}║${R}"
echo -e "${GRY}  ║${R}                                                                  ${GRY}║${R}"
echo -e "${GRY}  ║${R}       ${ORG}${BOLD}■ AWS${R}  ${GRY}│${R}  ${BLU}${BOLD}■ AZURE${R}       ${DIM}24 AWS labs · 29 Azure labs${R}         ${GRY}║${R}"
echo -e "${GRY}  ║${R}                                                                  ${GRY}║${R}"
echo -e "${GRY}  ╠══════════════════════════════════════════════════════════════════╣${R}"
echo -e "${GRY}  ║${R}                                                                  ${GRY}║${R}"
echo -e "${GRY}  ║${R}   ${BOLD}${WHT}Prerequisites${R}                                                    ${GRY}║${R}"
echo -e "${GRY}  ║${R}                                                                  ${GRY}║${R}"
echo -e "${GRY}  ║${R}   ${ORG}${BOLD}AWS${R}  IAM user / role:                                            ${GRY}║${R}"
echo -e "${GRY}  ║${R}     ${GRN}✓${R}  AdministratorAccess                                         ${GRY}║${R}"
echo -e "${GRY}  ║${R}                                                                  ${GRY}║${R}"
echo -e "${GRY}  ║${R}   ${BLU}${BOLD}Azure${R}  service principal:                                        ${GRY}║${R}"
echo -e "${GRY}  ║${R}     ${GRN}✓${R}  Global Administrator (Entra ID)                             ${GRY}║${R}"
echo -e "${GRY}  ║${R}     ${GRN}✓${R}  Owner on target subscription                                ${GRY}║${R}"
echo -e "${GRY}  ║${R}     ${GRN}✓${R}  Key Vault Administrator on target subscription              ${GRY}║${R}"
echo -e "${GRY}  ║${R}     ${GRN}✓${R}  Security defaults: ${RED}DISABLED${R}                                ${GRY}║${R}"
echo -e "${GRY}  ║${R}     ${GRN}✓${R}  Microsoft Graph app permissions (admin consented):          ${GRY}║${R}"
echo -e "${GRY}  ║${R}         ${DIM}User.ReadWrite.All · Application.ReadWrite.All${R}             ${GRY}║${R}"
echo -e "${GRY}  ║${R}         ${DIM}Directory.ReadWrite.All${R}                                    ${GRY}║${R}"
echo -e "${GRY}  ║${R}                                                                  ${GRY}║${R}"
echo -e "${GRY}  ╠══════════════════════════════════════════════════════════════════╣${R}"
echo -e "${GRY}  ║${R}   ${DIM}cnimbus -h   │   cnimbus azure -h   │   cnimbus aws -h${R}            ${GRY}║${R}"
echo -e "${GRY}  ╚══════════════════════════════════════════════════════════════════╝${R}"
echo -e ""
