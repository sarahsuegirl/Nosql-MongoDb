from pymongo import MongoClient

#   Replace with your actual MongoDB connection URI
uri = "mongodb+srv://dchacko1:Mdbdmck@cluster2.2umrks1.mongodb.net/"
client = MongoClient(uri)

#   Select your database
db = client["Recipebookapp"]

#   Select your collection
subcategories_collection = db["Subcategories"]

# Manually create a dictionary that maps category names to their MongoDB IDs
category_name_to_id = {
    "Cuisines": "65754068004b85794a540b2b",
    "OccasionRecipes": "65754068004b85794a540b2c",
    "QuickRecipes": "65754068004b85794a540b2d",
    "BlenderRecipes": "65754068004b85794a540b2e",
}

# Define subcategories with reference to their parent category's _id
subcategory_documents = [
    # {"name": "Blender Recipes", "category_id": category_name_to_id["BlenderRecipes"]},
    # {"name": "Italian", "category_id": category_name_to_id["Cuisines"]},
    # {"name": "Mexican", "category_id": category_name_to_id["Cuisines"]},
    # {"name": "Indian", "category_id": category_name_to_id["Cuisines"]},
    # {"name": "Chinese", "category_id": category_name_to_id["Cuisines"]},
    # {"name": "Bangladeshi", "category_id": category_name_to_id["Cuisines"]},
    # {"name": "South African", "category_id": category_name_to_id["Cuisines"]},
    # {"name": "Turkish", "category_id": category_name_to_id["Cuisines"]},
    # {"name": "Thanksgiving", "category_id": category_name_to_id["OccasionRecipes"]},
    # {"name": "Christmas", "category_id": category_name_to_id["OccasionRecipes"]},
    # {"name": "Ramadan", "category_id": category_name_to_id["OccasionRecipes"]},
    # {"name": "Diwali", "category_id": category_name_to_id["OccasionRecipes"]},
    # {"name": "Events Gathering", "category_id": category_name_to_id["OccasionRecipes"]},
    # {"name": "Instant Pot", "category_id": category_name_to_id["QuickRecipes"]},
    # {"name": "Microwave Recipes", "category_id": category_name_to_id["QuickRecipes"]},
    # {"name": "Air Fryer", "category_id": category_name_to_id["QuickRecipes"]},
    # {"name": "Mug Recipes", "category_id": category_name_to_id["QuickRecipes"]},
    # {"name": "Sheet Pan Recipes", "category_id": category_name_to_id["QuickRecipes"]},
]

# Insert subcategory documents
subcategories_result = subcategories_collection.insert_many(subcategory_documents)

# Capture the inserted IDs for subcategories
subcategory_name_to_id = {doc['name']: id for doc, id in zip(subcategory_documents, subcategories_result.inserted_ids)}

# Print the names and the IDs of the inserted subcategory documents
for name, subcategory_id in subcategory_name_to_id.items():
    print(f"Subcategory name: {name}, ID: {subcategory_id}")


# Subcategory name: Italian, ID: 657a004661b4e0bc47789d37
# Subcategory name: Mexican, ID: 657a004661b4e0bc47789d38
# Subcategory name: Indian, ID: 657a004661b4e0bc47789d39
# Subcategory name: Chinese, ID: 657a004661b4e0bc47789d3a
# Subcategory name: Bangladeshi, ID: 657a004661b4e0bc47789d3b
# Subcategory name: South African, ID: 657a004661b4e0bc47789d3c
# Subcategory name: Turkish, ID: 657a004661b4e0bc47789d3d
# Subcategory name: Thanksgiving, ID: 657a004661b4e0bc47789d3e
# Subcategory name: Christmas, ID: 657a004661b4e0bc47789d3f
# Subcategory name: Ramadan, ID: 657a004661b4e0bc47789d40
# Subcategory name: Diwali, ID: 657a004661b4e0bc47789d41
# Subcategory name: Events Gathering, ID: 657a004661b4e0bc47789d42
# Subcategory name: Instant Pot, ID: 657a004661b4e0bc47789d43
# Subcategory name: Microwave Recipes, ID: 657a004661b4e0bc47789d44
# Subcategory name: Air Fryer, ID: 657a004661b4e0bc47789d45
# Subcategory name: Mug Recipes, ID: 657a004661b4e0bc47789d46
# Subcategory name: Sheet Pan Recipes, ID: 657a004661b4e0bc47789d47    
# Subcategory name: Blender Recipes, ID: 657a17367930eae87e3498a2