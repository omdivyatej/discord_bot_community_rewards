import requests
from bs4 import BeautifulSoup
import os
from urllib.parse import urlparse

def is_url(input_string):
    """Check if the input string is a valid URL."""
    try:
        result = urlparse(input_string)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False

def is_text_file(file_path):
    """Check if the file exists and is a text file."""
    if os.path.isfile(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                f.read(1024)  # Read first 1KB
            return True
        except (UnicodeDecodeError, PermissionError):
            return False
    return False


def create_knowledge_base(k_source):
     
	if is_url(k_source):
	# Step 1: Fetch the webpage
		url = 'https://docs.gaianet.ai/creator-guide/knowledge/web-tool'
		response = requests.get(url)

		# Step 2: Parse the content
		soup = BeautifulSoup(response.content, 'html.parser')

		# Step 3: Extract text
		text = soup.get_text()
    
	elif is_text_file(k_source):
		# Step 1: Read the file
		with open(k_source, 'r', encoding='utf-8') as f:
			text = f.read()
	
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