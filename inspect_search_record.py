from api_client import VAClient
import json

client = VAClient()
results = client.search("chair", page_size=1)
if results.get('records'):
    record = results['records'][0]
    print("Search Record Keys:")
    print(list(record.keys()))
    print("\nFull Search Record:")
    print(json.dumps(record, indent=2))
