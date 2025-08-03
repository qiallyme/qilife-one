from wyze_sdk import Client

# Replace these with your actual credentials
KEY_ID = "cf4a4e4e-0620-47a5-957b-f8e3b8ea96c2"
API_KEY = "Kmre8OlfkCFjfyEPXLLvSd77621PgAQ540n62QsgfmetRB2WYD5Ey1WnuHKA"

client = Client(key_id=KEY_ID, api_key=API_KEY)

# List all devices
devices = client.devices.list()
for d in devices:
    print(f"{d.nickname} - {d.mac} - {d.product.model}")
