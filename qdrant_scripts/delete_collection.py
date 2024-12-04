import requests

collection = ""
url = f"http://10.181.131.244:6333/collections/{collection}"

response = requests.delete(url)

if response.status_code == 200:
    print(f"Collection {collection} deleted successfully.")
else:
    print(
        f"Failed to delete collection {collection}. Status code: {response.status_code}, Message: {response.text}"
    )
