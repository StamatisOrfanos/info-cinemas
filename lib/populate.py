import json

def insert(collection, document):
	match = collection.find_one(document)
	
	if not match:
		collection.insert_one(document)

def insert_json(path, collection):
	data = None

	try:
		with open(path, "r") as file:
			data = json.load(file)
	except Exception:
		print(f"Failed to read the file and/or parse json for the {collection} we want to insert to the database")
		return
	
	for document in data:
		insert(collection, document)
