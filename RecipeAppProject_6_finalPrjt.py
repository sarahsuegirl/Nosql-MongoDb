### Initialize Streamlit App
import streamlit as st
from pymongo import MongoClient
import pandas as pd
from bson import ObjectId
from pymongo.errors import DuplicateKeyError
from PIL import Image
# from streamlit_option_menu import option_menu

### Connect to MongoDB
client = MongoClient("mongodb+srv://dchacko1:Mdbdmck@cluster2.2umrks1.mongodb.net/")
db = client["Recipebookapp"]
categories_collection = db["Categories"]
subcategories_collection = db["Subcategories"]
recipes_collection = db["Allrecipes"]
users_collection = db["users"]

recipes_collection.create_index([("title", "text"), ("description", "text")])

# Set page configuration and title
st.set_page_config(page_title="Welcome To The Home Page", layout="wide")

# Initialize session state variables at the very start of the script
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'username' not in st.session_state:
    st.session_state['username'] = ''
if 'selected_category' not in st.session_state:
    st.session_state['selected_category'] = None
if 'selected_subcategory_id' not in st.session_state:
    st.session_state['selected_subcategory_id'] = None
if 'selected_subcategory_name' not in st.session_state:
    st.session_state['selected_subcategory_name'] = None

def set_background_color():
    # CSS to inject contained in a string
    background_style = """
    <style>
    .stApp {
        background-color: #e9eedd;
    }
    .css-1d391kg {
        background-color: #708238;
    }
    </style>
    """

    # Inject CSS with Markdown
    st.markdown(background_style, unsafe_allow_html=True)

# Call this function at the beginning of your script (right after setting page config)
set_background_color()

# Main categories and their corresponding subcategories
main_categories = {
    "Cuisines": ["Mexican", "Italian", "Chinese", "Indian", "Turkish", "Bangladeshi", "South African"],
    "OccasionRecipes": ["Ramadan", "Thanksgiving", "Christmas", "Diwali"],
    "QuickRecipes": ["Instant Pot", "Air Fryer", "Mug Recipes", "Sheet Pan Recipes"],
    "BlenderRecipes":["Blender Recipes"]
    # Add other categories and subcategories here
}

category_name_to_id = {}
for category_name in main_categories:
    category_document = categories_collection.find_one({"name": category_name})
    if category_document:
        category_name_to_id[category_name] = str(category_document["_id"])

### User Authentication Functions
def check_user(username, password):
    """Check if a user exists and the password is correct."""
    user = users_collection.find_one({"username": username})
    return user is not None and user["password"] == password

def create_user(username, password):
    """Create a new user account."""
    existing_user = users_collection.find_one({"username": username})
    if existing_user is not None:
        st.error("Username already exists. Please choose a different username.")
        # st.session_state['new_user'] = ''
        # st.session_state['new_password'] = ''
    else:
        try:
            users_collection.insert_one({"username": username, "password": password})
            st.success(f"User {username} created successfully!")
            # st.session_state['new_user'] = ''
            # st.session_state['new_password'] = ''
        except Exception as e:
            st.error(f"An error occurred while creating the user: {e}")
            # st.session_state['new_user'] = ''
            # st.session_state['new_password'] = ''  

def create_user_callback():
    # Attempt to create the user
    create_user(st.session_state['new_user'], st.session_state['new_password'])
    # Clear the input fields
    st.session_state['new_user'] = ''
    st.session_state['new_password'] = ''
    # Rerun the app to refresh the state and UI
    # st.experimental_rerun()

#### UI Functions

def create_user_ui():
    st.sidebar.subheader("Create New User")
    # Define the session state keys for new user and password if not already present
    if 'new_user' not in st.session_state:
        st.session_state['new_user'] = ''
    if 'new_password' not in st.session_state:
        st.session_state['new_password'] = ''
    
    # Create the text input widgets using the session state keys
    new_username = st.sidebar.text_input("New Username", key="new_user")
    new_password = st.sidebar.text_input("New Password", type="password", key="new_password")
    
    # Create the button with a callback function
    create_button = st.sidebar.button("Create User", on_click=create_user_callback)

def transform_id(doc):
    # Ensure 'ingredients' is a list
    doc['_id'] = str(doc['_id'])  # Convert ObjectId to string
    if 'ingredients' in doc and not isinstance(doc['ingredients'], list):
        doc['ingredients'] = doc['ingredients'].split(', ')

    # Ensure 'instructions' is a string
    if 'instructions' in doc and isinstance(doc['instructions'], list):
        doc['instructions'] = ' '.join(doc['instructions'])

    doc['_id'] = str(doc['_id'])  # Convert ObjectId to string
    return doc

### Define Functions for Database Operations
def insert_recipe(recipe_data):
    # Convert string of ingredients to a list if not already a list
    if isinstance(recipe_data['ingredients'], str):
        recipe_data['ingredients'] = recipe_data['ingredients'].split(', ')

    # Convert instructions string to a list
    if isinstance(recipe_data['instructions'], str):
        recipe_data['instructions'] = [instruction.strip() for instruction in recipe_data['instructions'].split('. ')]
        
    recipes_collection.insert_one(recipe_data)

def get_all_recipes():
    try:
        recipes = recipes_collection.find()
        # Apply the updated transformation function to each document
        recipes = [transform_id(doc) for doc in recipes]
        return pd.DataFrame(recipes)

    except Exception as e:
        st.error(f"An error occurred: {e}")
        return pd.DataFrame()  # Return an empty DataFrame in case of an error    

def update_recipe(recipe_id, update_data):
    """Update a recipe in the database."""
    recipes_collection.update_one({'_id': ObjectId(recipe_id)}, {'$set': update_data})
    st.success("Recipe updated successfully!")

def delete_recipe(recipe_id):
    """Delete a recipe from the database."""
    recipes_collection.delete_one({'_id': ObjectId(recipe_id)})
    st.success("Recipe deleted successfully!")       

# Function to show subcategories when a category is clicked
def show_subcategories(category_id):
    # Store the selected category ID in session state
    st.session_state["selected_category"] = category_id
    subcategories = subcategories_collection.find({"category_id": ObjectId(category_id)})
    
    # Ensure that the subcategories are displayed
    if subcategories_collection.count_documents({"category_id": ObjectId(category_id)}) == 0:
        st.write("Enjoy the Recipes")
        return

    for subcat in subcategories:
        subcat = dict(subcat)  # Ensure subcat is a dictionary
        subcat_name = subcat.get("name", "Unknown subcategory")
        subcat_id = str(subcat.get("_id", ""))  # Convert ObjectId to string

        # Use the subcategory name as the button label and the subcategory ID as the key
        if st.button(subcat_name, key=subcat_id):
            st.session_state["selected_subcategory_name"] = subcat_name
            st.session_state["selected_subcategory_id"] = subcat_id 

# Function to query and list recipes by subcategory ID from MongoDB
def get_recipes_by_subcategory(subcategory_id):
    # Ensure the ID is in the correct format for querying MongoDB
    if isinstance(subcategory_id, str):
        subcategory_id = ObjectId(subcategory_id)
    
    recipes = recipes_collection.find({"subcategory_id": subcategory_id})
    return list(recipes)  # Convert cursor to list

## Function to display recipe details
def show_recipes(subcategory_name, subcategory_id):
    st.header(f"Recipes for {subcategory_name}")
    recipes = get_recipes_by_subcategory(subcategory_id)
    if recipes:
#         # Add more details as needed 
        for recipe in recipes:
            st.subheader(recipe.get("title", "No title"))
            # Use the actual image if the 'images' field exists and is not empty; otherwise, use a placeholder
            image_url = recipe.get("images", "https://via.placeholder.com/150")
            st.image(image_url, width=300 if image_url else None)
            st.write("Description:", recipe.get("description", "No description provided"))
            st.write("Cook Time:", recipe.get("cook", "No Cook Time provided"))
            st.write("Prep Time:", recipe.get("prep", "No Prep Time provided"))
            st.write("Total Time:", recipe.get("total", "No Total Time provided"))
            st.write("Ingredients:", recipe.get("ingredients", "No Ingredients provided"))
            st.write("Directions:", recipe.get("directions", "No Directions provided"))
    else:
        st.write("No recipes found for this subcategory.")
       

### Add a Login UI
def login_ui():
    st.sidebar.title("Login")
    username = st.sidebar.text_input("Username", key="login_user")
    password = st.sidebar.text_input("Password", type="password", key="login_pass")

    if st.sidebar.button("Login", key="login_button"):
        if check_user(username, password):
            st.sidebar.success(f"Logged in as {username}")
            st.session_state["logged_in"] = True  # Set the logged-in state
            st.session_state["username"] = username  # Store the username
            # st.experimental_rerun()  # Rerun the app to update the UI
        else:
            st.sidebar.error("Incorrect username or password")

# Define the logout function
def logout_ui():
    st.session_state["logged_in"] = False
    st.session_state["username"] = None
    # st.experimental_rerun()  # Rerun the app to update the UI            

# Define the top bar navigation
def top_bar_navigation():
    top_bar_col1, top_bar_col2, top_bar_col3, top_bar_col4, top_bar_col5 = st.columns([1, 1, 1, 1, 1])
    with top_bar_col1:
        if st.button("Home", key="home"):
            st.write("Welcome to the home page!")
    with top_bar_col2:
        if st.button("About Us", key="about"):
            st.write("we are a project Team of two lovely graduate student in Fordham university.")
    with top_bar_col3:
        if st.button("Contact", key="contact"):
            st.write("Please contact us at [saljamal@fordham.edu] or [dchacko1@fordham.edu]")
            # st.write("Please contact me at [dchacko1@fordham.edu]")
    with top_bar_col4:
        if st.button("New User", key="register"):
            # Set a session state flag to trigger showing the new user UI in the sidebar
            st.session_state['show_new_user_form'] = True
            ## create_user_ui()  # Call the function to create a new user
    with top_bar_col5:
        if st.session_state.get("logged_in"):
            if st.button("Logout", key="logout"):
                st.session_state['logged_in'] = False
                st.session_state['username'] = None
                # logout_ui()
        else:
            if st.button("Login", key="login"):
                st.session_state['page'] = 'login'
                # login_ui()  # Call the function to log in

# In the sidebar logic
def sidebar():
    with st.sidebar:
        # ... your existing sidebar code for login/logout ...

        # Conditionally display the new user form based on the session state flag
        if st.session_state.get('show_new_user_form', False):
            create_user_ui()
            # Reset the flag to hide the form again after it's been shown
            st.session_state['show_new_user_form'] = False                

# Call the top bar navigation function to display it
top_bar_navigation()

sidebar()

# Sidebar Navigation
st.sidebar.image("/Users/deepachacko/Desktop/NoSQL/NoSQL Project/logo.jpg", width=150, use_column_width=True)
st.sidebar.title("Please Login")

### Build the Streamlit Interface
def add_recipe_ui():
    st.title("Add a New Recipe")
    with st.form("Recipe Form", clear_on_submit=True):
        title = st.text_input("Title")
        ingredients = st.text_area("Ingredients", 
                                   placeholder="Enter ingredients separated by commas")
        # Instruct the user to separate each step with a newline
        instructions = st.text_area("Instructions", 
                                    placeholder="Enter each step on a new line")
        submit_button = st.form_submit_button("Submit")
        
        if submit_button:
            # Split ingredients and instructions into lists
            ingredients_list = [i.strip() for i in ingredients.split(',')]
            instructions_list = [i.strip() for i in instructions.split('\n') if i]  # Split by new lines and remove empty lines
            
            recipe_data = {
                "title": title,
                "ingredients": ingredients_list,
                "instructions": instructions_list
            }
            insert_recipe(recipe_data)
            st.success("Recipe added successfully!")

# This function remains the same as I described earlier
def image_formatter(images):
    if images:  # Check if the URL is not None or empty
        return f'<img src="{images}" width="100"/>'
    return ""

def view_recipes_ui():
    st.title("View Recipes")
    recipes_df = get_all_recipes()
    # st.dataframe(recipes_df)
    if 'images' in recipes_df.columns:
        # Apply the formatter to the images column
        recipes_df['image_html'] = recipes_df['images'].apply(image_formatter)

        # Convert the DataFrame to HTML and use st.markdown to render it, with images
        st.markdown(recipes_df.to_html(escape=False, formatters={'image_html': lambda x: x}), unsafe_allow_html=True)
    else:
        st.dataframe(recipes_df)  

def update_recipe_ui():
    """UI to update an existing recipe."""
    recipe_id = st.text_input("Recipe ID to Update")
    title = st.text_input("New Title")
    ingredients = st.text_area("New Ingredients (separate by commas)")
    instructions = st.text_area("New Instructions")
    submit = st.button("Update Recipe")

    if submit:
        update_data = {
            "title": title,
            "ingredients": ingredients.split(','),
            "instructions": instructions
        }
        update_recipe(recipe_id, update_data)

def delete_recipe_ui():
    """UI to delete an existing recipe."""
    recipe_id = st.text_input("Recipe ID to Delete")
    if st.button("Delete Recipe"):
        delete_recipe(recipe_id)


# Open the image
background_image = Image.open('/Users/deepachacko/Desktop/NoSQL/NoSQL Project/k.jpg')

# Display the image using st.image
col1, col2, col3 = st.columns([1,7,1])
with col2:  # Assuming the middle column takes more space
    # st.image(background_image, width=500)
    st.image(background_image, use_column_width=True)
# st.image(background_image, width=600)

# st.text_input("Search for Recipes")

# st.markdown("Enjoy The Recipes")

def main():
    st.title("SarDee's Recipes")
    # Search bar for recipes
    search_query = st.text_input("Search for Recipes", key="search_query")
    if search_query:
        # Perform the search query here
        search_results = recipes_collection.find({"$text": {"$search": search_query}})
        results_list = list(search_results)
        
        # Use 'count_documents' instead of 'count' to get the number of documents
        if recipes_collection.count_documents({"$text": {"$search": search_query}}) > 0:
            # Display the search results
            for result in results_list:
                st.subheader(result['title'])  # Display the title of the recipe
                st.write("Description:", result.get("description", "No description provided"))
                st.write("Cook Time:", result.get("cook", "No Cook Time provided"))
                st.write("Prep Time:", result.get("prep", "No Prep Time provided"))
                st.write("Total Time:", result.get("total", "No Total Time provided"))
                st.write("Ingredients:", result.get("ingredients", "No Ingredients provided"))
                st.write("Directions:", result.get("directions", "No Directions provided"))
                # Check if there is an image URL in the result and display it
                if 'images' in result and result['images']:
                    st.image(result['images'], width=300)  # Adjust the width as needed
        else:
            st.write("No recipes found for your search.")

    # Main category buttons
    #st.title("Recipes")
    cols = st.columns(len(main_categories))
    for i, category_name in enumerate(main_categories.keys()):
        with cols[i]:
            if st.button(category_name):
                # Retrieve the ObjectId of the category from MongoDB
                category_document = categories_collection.find_one({"name": category_name})
                if category_document:
                    # Set the session state to the string representation of the ObjectId
                    st.session_state['selected_category'] = str(category_document["_id"])
                else:
                    # If the category is not found in the database, raise an error or handle appropriately
                    st.error(f"Category '{category_name}' not found in the database.")

    # Display subcategories for the selected main category
    if st.session_state.get('selected_category'):
        # Before displaying subcategories, we need to perform a reverse lookup to find the category name
        selected_category_id = st.session_state['selected_category']
        selected_category_name = None
        for category in categories_collection.find():
            if str(category["_id"]) == selected_category_id:
                selected_category_name = category["name"]
                break
        
        if selected_category_name:
            st.subheader(f"Menu for {selected_category_name}:")
            subcategory_names = main_categories[selected_category_name]
            
            # Iterate over the subcategory names
            for subcat_name in subcategory_names:
                # Retrieve the subcategory document from MongoDB using the name
                subcategory_document = subcategories_collection.find_one({"name": subcat_name})
            
                # If the subcategory document is found, use its name and ID
                if subcategory_document:
                    subcat_id = str(subcategory_document["_id"])  # Convert ObjectId to string for the key
                    if st.button(subcat_name, key=subcat_id):
                        st.session_state["selected_subcategory_id"] = subcat_id
                        st.write(f"You selected subcategory: {subcat_name}")
                else:
                    st.write(f"Subcategory {subcat_name} not found in the database.")
        else:
            st.error('Selected category ID does not match any known categories.')

    # Display the main categories as buttons
    if "selected_category" not in st.session_state:
        st.title("Select a Category")
        categories = categories_collection.find()
        for category in categories:
            if st.button(category["name"]):
                st.session_state["selected_category"] = str(category["_id"])
                # st.session_state["selected_category"] = category["_id"]
                # Clear the subcategory selection when a new category is chosen
                # st.session_state["selected_subcategory_id"] = None


    # If a category has been selected, show its subcategories
    if "selected_category" in st.session_state:
        category_id = st.session_state["selected_category"]
        show_subcategories(category_id)

    if "selected_subcategory_id" in st.session_state:
        subcategory_id = ObjectId(st.session_state["selected_subcategory_id"])
        subcategory = subcategories_collection.find_one({"_id": subcategory_id})
        if subcategory:
           show_recipes(subcategory["name"], subcategory_id)
        # else:
        #    st.error("Debug: Subcategory not found. Check the subcategory_id and database.")
    

    # Sidebar for login, logout, and registration
    with st.sidebar:
        if st.session_state['logged_in']:
            st.write(f"Logged in as {st.session_state['username']}")
            if st.button("Logout"):
                logout_ui()
            # # Admin user functionalities
            # if st.session_state['username'] == 'admin':
            #     create_user_ui()
        else:
            login_ui()
        # This will always display the create user UI, regardless of login status
        create_user_ui()    

    # Sidebar logic for login and user interactions
    if st.session_state.get('logged_in'):
        #     create_user_ui()
        # Display navigation options for logged in users
        option = st.sidebar.radio(
            "Choose an option",
            ["Add Recipe", "Update Recipe", "Delete Recipe"],
            # ["Add Recipe", "View Recipes", "Update Recipe", "Delete Recipe"],
            key="main_radio"
        )
        if option == "Add Recipe":
            add_recipe_ui()
        # elif option == "View Recipes":
        #     view_recipes_ui()
        elif option == "Update Recipe":
            update_recipe_ui()
        elif option == "Delete Recipe":
            delete_recipe_ui()
    # else:
    #     login_ui()

    # # Debug statements (remove these once everything is working correctly)
    # st.write(f"Debug: selected_category - {st.session_state.get('selected_category')}")
    # st.write(f"Debug: selected_subcategory_id - {st.session_state.get('selected_subcategory_id')}")

if __name__ == "__main__":
    
    main()       
