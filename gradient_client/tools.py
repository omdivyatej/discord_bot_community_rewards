import requests
from bs4 import BeautifulSoup

# Step 1: Fetch the webpage
url = 'https://docs.gaianet.ai/creator-guide/knowledge/web-tool'
response = requests.get(url)

# Step 2: Parse the content
soup = BeautifulSoup(response.content, 'html.parser')

# Step 3: Extract text
text = soup.get_text()

# Step 4: Save to a file
with open('output.txt', 'w', encoding='utf-8') as f:
    f.write(text)

from gradio_client import Client, file

client = Client("https://tools.gaianet.xyz/")
result = client.predict(
		uploaded_file=file('output.txt'),
		db_name="mazed-ai",
		em_model="nomic-embed-text-v1.5.f16",
		chat_history=[],
		api_name="/handle_upload"
)
print(result)