from pymongo import MongoClient

#   Replace with your actual MongoDB connection URI
uri = "mongodb+srv://dchacko1:Mdbdmck@cluster2.2umrks1.mongodb.net/"
client = MongoClient(uri)

#   Select your database
db = client["Recipebookapp"]

#   Select your collection
categories_collection = db["Categories"]

#   Documents to insert
category_documents = [
    # {"name": "Cuisines"},
    # {"name": "OccasionRecipes"},
    # {"name": "QuickRecipes"},
    # {"name": "BlenderRecipes"}
]

#  Insert documents
result = categories_collection.insert_many(category_documents)

# Insert multiple documents and retrieve their IDs
inserted_ids = result.inserted_ids

# Print the IDs of the inserted documents
for inserted_id in inserted_ids:
    print(f"Inserted document ID: {inserted_id}")

## outputs
## Inserted document ID: 65754068004b85794a540b2b
## Inserted document ID: 65754068004b85794a540b2c
## Inserted document ID: 65754068004b85794a540b2d
## Inserted document ID: 65754068004b85794a540b2e    

#   Output the result
# print(f"Inserted {len(result.inserted_ids)} documents into the collection.")