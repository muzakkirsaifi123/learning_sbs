---
description: "How to check the email is working or not in the keycloak\u2019"
notion_url: "https://app.notion.com/p/keycloak-3c09f2a93248808184c0f65c17f966f2"
created_time: "2026-08-18T07:55:00.000Z"
last_edited_time: "2026-08-18T08:16:00.000Z"
---

# keycloak


## How to check the email is working or not in the keycloak’

### Steps to follow:
- You need to check the secret first like aws access key {**AWS_ACCESS_KEY_ID**} as the user and for the passwd in the relam setting you can use this {**AWS_SMTP_KEY} **smtp secret.
- You need to use the these cmd for the same:
 

```javascript
for user ---

╭─ ~ ····················································································································· ✘ 0|1 at 01:22:41 PM
╰─❯ echo "sdgsg=" | base64 -d
sdgsgs%           
for smtp:--                                                                                                                
╭─ ~ ··························································································································· at 01:22:52 PM
╰─❯ echo "sdgsg" | base64 -d
dgsgdsgsgg%

for the hsot you need to run this:
helm get values keycloak -n test -a | grep -B2 -A20 -i smtp

```



--8<-- "abbreviations.md"
