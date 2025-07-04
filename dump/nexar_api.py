# === Your credentials ===
CLIENT_ID = "415c8035-f44a-4202-aded-621fe2e96595"
CLIENT_SECRET = "9qA0X62WpHre0-98Aj6PL10gGhAGplf2_KRK"


import requests
import pandas as pd
import urllib3
from urllib3.exceptions import InsecureRequestWarning

# ─── Disable only the single InsecureRequestWarning ───────────────────────────
urllib3.disable_warnings(InsecureRequestWarning)

# === Your credentials (fill in locally) ===
# CLIENT_ID = "your_client_id_here"
# CLIENT_SECRET = "your_client_secret_here"

def get_nexar_token(client_id, client_secret):
    resp = requests.post(
        "https://identity.nexar.com/connect/token",
        data={
            'grant_type': 'client_credentials',
            'client_id': client_id,
            'client_secret': client_secret,
            'scope': 'supply.domain'
        },
        headers={'Content-Type': 'application/x-www-form-urlencoded'},
        verify=False
    )
    if resp.status_code != 200:
        print("❌ Token error:", resp.status_code, resp.text)
        resp.raise_for_status()
    return resp.json()["access_token"]

def query_part_specs(part_number, access_token):
    query = {
        "query": f'''
        {{
          supSearch(q: "{part_number}") {{
            results {{
              part {{
                mpn
                manufacturer {{ name }}
                shortDescription
                specs {{
                  attribute {{ name }}
                  displayValue
                }}
              }}
            }}
          }}
        }}
        '''
    }
    resp = requests.post(
        "https://api.nexar.com/graphql",
        json=query,
        headers={
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        },
        verify=False
    )
    try:
        resp.raise_for_status()
    except requests.HTTPError:
        print(f"\n❌ HTTP {resp.status_code} for {part_number}:\n{resp.text}")
        return None

    data = resp.json()
    # Check for GraphQL errors
    if 'errors' in data:
        print(f"\n❌ GraphQL errors for {part_number}:\n{data['errors']}")
        return None

    return data

def extract_spec_table(response_json, part_number):
    """
    Returns a DataFrame, or an empty DataFrame if no specs.
    """
    # Safety check
    if not response_json or 'data' not in response_json:
        return pd.DataFrame()
    results = response_json['data'].get('supSearch', {}).get('results', [])
    if not results:
        return pd.DataFrame()

    specs = results[0]['part'].get('specs', [])
    return pd.DataFrame([{
        "Attribute": s["attribute"]["name"],
        "Value": s.get("displayValue", "")
    } for s in specs])

if __name__ == "__main__":
    parts = ["BC847B", "MBRS360", "RD3L080SNFRA", "DWW-KZKG_Typ"]
    token = get_nexar_token(CLIENT_ID, CLIENT_SECRET)

    for part in parts:
        print(f"\n🔍 Specs for {part}:")
        resp = query_part_specs(part, token)
        if resp is None:
            print(f"  ❌ Skipping {part} due to previous errors.")
            continue

        df = extract_spec_table(resp, part)
        if df.empty:
            print("  ❌ No specs found.")
        else:
            print(df.to_string(index=False))
