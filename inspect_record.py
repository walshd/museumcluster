from api_client import VAClient
import json

client = VAClient()
# Fetch a chair record that we know exists
record = client.get_object("O72610")
print(json.dumps(record, indent=2))
