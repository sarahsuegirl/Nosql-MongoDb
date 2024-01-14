import json
import os
from pymongo import MongoClient

# Replace with your actual MongoDB connection URI
uri = "mongodb+srv://dchacko1:Mdbdmck@cluster2.2umrks1.mongodb.net/"
client = MongoClient(uri)

# Select your database
db = client["Recipebookapp"]
subcategories_collection = db["Subcategories"]
recipes_collection = db["Allrecipes"]

# Retrieve all subcategories and their IDs from MongoDB
subcategories = subcategories_collection.find({})
subcategory_to_id = {subcat['name']: subcat['_id'] for subcat in subcategories}

# Base directory where subcategory folders are located
base_directory = "/Users/deepachacko/Desktop/NOSQL_Prjt_Data/"

# Specific categories to process
specific_categories = ["Cuisines", "Occasions", "QuickRecipes", "BlenderRecipes"]
# specific_categories = ["QuickRecipes", "BlenderRecipes"]

# Iterate over the specific categories
for main_cat in specific_categories:
    subcategory_directory = os.path.join(base_directory, main_cat)
    
    # Check if the main category directory exists
    if not os.path.exists(subcategory_directory):
        print(f"Directory does not exist: {subcategory_directory}")
        continue
    
    # Iterate over each subcategory directory and corresponding JSON file
    for subcat_name in os.listdir(subcategory_directory):
        # Check if the subcategory name is in the ID mapping
        if subcat_name not in subcategory_to_id:
            print(f"Subcategory ID not found for: {subcat_name}")
            continue
        
        subcategory_path = os.path.join(subcategory_directory, subcat_name)
        
        # Construct the path to the JSON file
        json_file_path = os.path.join(subcategory_path, subcat_name.lower() + '.json')
        
        # Check if the JSON file exists
        if not os.path.isfile(json_file_path):
            print(f"JSON file does not exist: {json_file_path}")
            continue
        
        # Load the recipes from the JSON file
        with open(json_file_path, 'r') as json_file:
            try:
                recipes_data = json.load(json_file)
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON from file {json_file_path}: {e}")
                continue

        # Add the subcategory ID to each recipe and insert them into the database
        for recipe in recipes_data:
            try:
                recipe['subcategory_id'] = subcategory_to_id[subcat_name]
                recipes_collection.insert_one(recipe)
            except Exception as e:
                print(f"Error inserting recipe for {subcat_name}: {e}")

        print(f"Inserted recipes for subcategory: {subcat_name}")