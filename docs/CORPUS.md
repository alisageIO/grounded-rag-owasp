# CORPUS.md

Corpus for Stage 7 (Retrieval-Grounded Answering with Citations).

## Provenance

| Field | Value |
|---|---|
| Source | OWASP Cheat Sheet Series |
| Repository | https://github.com/OWASP/CheatSheetSeries |
| Licence | CC BY-SA 4.0 |
| Pinned commit | `640844e521ead212b4a6d74c0dc4dabb56eb6153` |
| Path | `cheatsheets/` |
| Documents indexed | 40 |
| Estimated tokens | ~159,998 (cl100k approximation) |
| Documents held out | 7 (see Abstention set) |

Token counts are estimates (`chars/3.7` and `words*1.35`, averaged). Recount with `tiktoken` locally before quoting them in the eval report.

## Theme

A single coherent domain: **securing a web application's identity, access and input surfaces.** The documents cross-reference each other 76 times, which is where the multi-document synthesis questions come from. The corpus is heavy in error codes, header names and flag literals, so BM25 contributes real signal alongside vector similarity.

## Indexed documents

### Identity & authentication (6)

| Document | ~Tokens |
|---|---|
| `Authentication_Cheat_Sheet.md` | 8,684 |
| `Multifactor_Authentication_Cheat_Sheet.md` | 7,682 |
| `Credential_Stuffing_Prevention_Cheat_Sheet.md` | 4,099 |
| `Choosing_and_Using_Security_Questions_Cheat_Sheet.md` | 2,954 |
| `Forgot_Password_Cheat_Sheet.md` | 2,207 |
| `Email_Validation_and_Verification_Cheat_Sheet.md` | 1,172 |

### Sessions & tokens (4)

| Document | ~Tokens |
|---|---|
| `Session_Management_Cheat_Sheet.md` | 12,578 |
| `JSON_Web_Token_Cheat_Sheet.md` | 9,525 |
| `OAuth2_Cheat_Sheet.md` | 3,515 |
| `Cookie_Theft_Mitigation_Cheat_Sheet.md` | 1,749 |

### Authorisation (4)

| Document | ~Tokens |
|---|---|
| `Authorization_Cheat_Sheet.md` | 7,223 |
| `Authorization_Regression_Testing_Cheat_Sheet.md` | 2,653 |
| `Mass_Assignment_Cheat_Sheet.md` | 1,546 |
| `Insecure_Direct_Object_Reference_Prevention_Cheat_Sheet.md` | 1,245 |

### Injection (7)

| Document | ~Tokens |
|---|---|
| `Injection_Prevention_Cheat_Sheet.md` | 4,820 |
| `SQL_Injection_Prevention_Cheat_Sheet.md` | 4,424 |
| `OS_Command_Injection_Defense_Cheat_Sheet.md` | 2,635 |
| `LDAP_Injection_Prevention_Cheat_Sheet.md` | 2,094 |
| `Database_Security_Cheat_Sheet.md` | 1,991 |
| `Query_Parameterization_Cheat_Sheet.md` | 1,747 |
| `NoSQL_Security_Cheat_Sheet.md` | 1,635 |

### Input handling (3)

| Document | ~Tokens |
|---|---|
| `Input_Validation_Cheat_Sheet.md` | 4,394 |
| `File_Upload_Cheat_Sheet.md` | 2,816 |
| `Bean_Validation_Cheat_Sheet.md` | 2,598 |

### Browser & client (11)

| Document | ~Tokens |
|---|---|
| `Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.md` | 16,257 |
| `DOM_based_XSS_Prevention_Cheat_Sheet.md` | 6,696 |
| `Cross_Site_Scripting_Prevention_Cheat_Sheet.md` | 6,593 |
| `HTTP_Headers_Cheat_Sheet.md` | 4,866 |
| `Content_Security_Policy_Cheat_Sheet.md` | 4,263 |
| `Clickjacking_Defense_Cheat_Sheet.md` | 3,436 |
| `DOM_Clobbering_Prevention_Cheat_Sheet.md` | 2,808 |
| `AJAX_Security_Cheat_Sheet.md` | 2,052 |
| `Unvalidated_Redirects_and_Forwards_Cheat_Sheet.md` | 1,780 |
| `Securing_Cascading_Style_Sheets_Cheat_Sheet.md` | 1,464 |
| `Prototype_Pollution_Prevention_Cheat_Sheet.md` | 493 |

### APIs & services (4)

| Document | ~Tokens |
|---|---|
| `REST_Security_Cheat_Sheet.md` | 5,503 |
| `gRPC_Security_Cheat_Sheet.md` | 2,910 |
| `Web_Service_Security_Cheat_Sheet.md` | 2,136 |
| `REST_Assessment_Cheat_Sheet.md` | 1,484 |

### Reference (1)

| Document | ~Tokens |
|---|---|
| `Security_Terminology_Cheat_Sheet.md` | 1,271 |

## Abstention set (fetched, never indexed)

These seven documents are **deliberately excluded from the index.** They share the corpus's vocabulary, register and author, and 13 of the 40 indexed documents cite them by name. Retrieval will therefore return high-similarity chunks for questions about them — chunks that discuss the topic without containing the answer. That is the point: abstention accuracy only means something when retrieval *looks* confident.

| Held-out document | ~Tokens | Cited by |
|---|---|---|
| `Secrets_Management_Cheat_Sheet.md` | 14,952 | 0 indexed doc(s) |
| `Key_Management_Cheat_Sheet.md` | 5,468 | 1 indexed doc(s) |
| `Transport_Layer_Security_Cheat_Sheet.md` | 5,364 | 6 indexed doc(s) |
| `Password_Storage_Cheat_Sheet.md` | 4,747 | 5 indexed doc(s) |
| `Cryptographic_Storage_Cheat_Sheet.md` | 4,331 | 4 indexed doc(s) |
| `Pinning_Cheat_Sheet.md` | 3,658 | 0 indexed doc(s) |
| `HTTP_Strict_Transport_Security_Cheat_Sheet.md` | 897 | 2 indexed doc(s) |

## Freshness demo (Stage 7.3)

`Authentication_Cheat_Sheet.md` changed twice in the pinned window:

| Commit | Date | Change |
|---|---|---|
| `b799b499d52b530046aa35381e4d0a51ede5e087` | 2026-06-19 | Passkey implementation guidance |
| `34c46661eb2195ca614577fc496e3a520e167cca` | 2026-06-22 | NIST SP 800-63B link updated to 800-63-4 |
| `640844e521ead212b4a6d74c0dc4dabb56eb6153` | 2026-07-09 | Login throttling reclassified |

Ingest at `b799b499`, then re-ingest at `640844e5`. Exactly one document changed. Assert that only its chunks were re-embedded, that superseded chunks are tombstoned rather than deleted, and that retrieval prefers the newest active version.

## Reproduce
```bash
bash fetch_corpus.sh
```
