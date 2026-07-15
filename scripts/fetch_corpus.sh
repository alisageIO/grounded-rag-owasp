#!/usr/bin/env bash
# Stage 7 corpus fetcher. Pins a commit so eval numbers stay reproducible.
set -euo pipefail
SHA="640844e521ead212b4a6d74c0dc4dabb56eb6153"
BASE="https://raw.githubusercontent.com/OWASP/CheatSheetSeries/$SHA/cheatsheets"
mkdir -p corpus/indexed corpus/holdout

INDEXED=(  Authentication_Cheat_Sheet
  Authorization_Cheat_Sheet
  Session_Management_Cheat_Sheet
  JSON_Web_Token_Cheat_Sheet
  OAuth2_Cheat_Sheet
  Multifactor_Authentication_Cheat_Sheet
  Credential_Stuffing_Prevention_Cheat_Sheet
  Forgot_Password_Cheat_Sheet
  Insecure_Direct_Object_Reference_Prevention_Cheat_Sheet
  Input_Validation_Cheat_Sheet
  Injection_Prevention_Cheat_Sheet
  SQL_Injection_Prevention_Cheat_Sheet
  Query_Parameterization_Cheat_Sheet
  OS_Command_Injection_Defense_Cheat_Sheet
  LDAP_Injection_Prevention_Cheat_Sheet
  Mass_Assignment_Cheat_Sheet
  File_Upload_Cheat_Sheet
  Cross_Site_Scripting_Prevention_Cheat_Sheet
  DOM_based_XSS_Prevention_Cheat_Sheet
  Cross-Site_Request_Forgery_Prevention_Cheat_Sheet
  Clickjacking_Defense_Cheat_Sheet
  Content_Security_Policy_Cheat_Sheet
  HTTP_Headers_Cheat_Sheet
  Unvalidated_Redirects_and_Forwards_Cheat_Sheet
  REST_Security_Cheat_Sheet
  Prototype_Pollution_Prevention_Cheat_Sheet
  Email_Validation_and_Verification_Cheat_Sheet
  Security_Terminology_Cheat_Sheet
  Securing_Cascading_Style_Sheets_Cheat_Sheet
  REST_Assessment_Cheat_Sheet
  NoSQL_Security_Cheat_Sheet
  Cookie_Theft_Mitigation_Cheat_Sheet
  Database_Security_Cheat_Sheet
  AJAX_Security_Cheat_Sheet
  Web_Service_Security_Cheat_Sheet
  Bean_Validation_Cheat_Sheet
  Authorization_Regression_Testing_Cheat_Sheet
  DOM_Clobbering_Prevention_Cheat_Sheet
  gRPC_Security_Cheat_Sheet
  Choosing_and_Using_Security_Questions_Cheat_Sheet
)

HOLDOUT=(  Password_Storage_Cheat_Sheet
  Cryptographic_Storage_Cheat_Sheet
  Key_Management_Cheat_Sheet
  Transport_Layer_Security_Cheat_Sheet
  Secrets_Management_Cheat_Sheet
  Pinning_Cheat_Sheet
  HTTP_Strict_Transport_Security_Cheat_Sheet
)

echo "Fetching ${#INDEXED[@]} indexed documents at $SHA ..."
for d in "${INDEXED[@]}"; do curl -fsSL "$BASE/$d.md" -o "corpus/indexed/$d.md"; done

echo "Fetching ${#HOLDOUT[@]} held-out documents (NEVER index these) ..."
for d in "${HOLDOUT[@]}"; do curl -fsSL "$BASE/$d.md" -o "corpus/holdout/$d.md"; done

# Freshness pair: same document, two commits.
OLD="b799b499d52b530046aa35381e4d0a51ede5e087"
mkdir -p corpus/revisions
curl -fsSL "https://raw.githubusercontent.com/OWASP/CheatSheetSeries/$OLD/cheatsheets/Authentication_Cheat_Sheet.md" \
  -o corpus/revisions/Authentication_Cheat_Sheet.v1.md
cp corpus/indexed/Authentication_Cheat_Sheet.md corpus/revisions/Authentication_Cheat_Sheet.v2.md

echo "Done. Licence: CC BY-SA 4.0 — attribute OWASP and share alike."
