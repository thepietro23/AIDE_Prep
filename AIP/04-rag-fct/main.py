from app.loaders.website_loader import WebsiteLoader

loader = WebsiteLoader("https://forensiccybertech.com/")
documents = loader.load()
doc = documents[0]

print("=" * 50)
print(f"Document ID: {doc.title}")
print("=" * 50)
print(doc.content[:3000])