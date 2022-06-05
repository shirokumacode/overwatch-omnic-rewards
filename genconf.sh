#!/bin/bash

if [[ -z "${ACCOUNT_ID}" ]]; then
  echo "ACCOUNT_ID must be set"
  exit 1
fi

# Save config file for specified account id
cat > config.json << EOL
{
    "account": "${ACCOUNT_ID}",
    "owl": true,
    "owc": true,
    "middle_click": "open_owl_owc",
    "left_click": "context_menu",
    "min_check": 10,
    "force_track": false
}
EOL