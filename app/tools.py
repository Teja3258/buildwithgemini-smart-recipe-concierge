import json
import os
import urllib.parse
import urllib.request
import uuid
from google import genai
from google.genai import types
from google.cloud import firestore, storage

# Hardcoded Project ID string and bucket as required
PROJECT_ID = "qwiklabs-gcp-03-7698bbba51cd"
BUCKET_NAME = "smart-recipe-concierge-qwiklabs-gcp-03-7698bbba51cd"


def _get_firestore_client() -> firestore.Client:
    """Returns a Firestore client initialized with the hardcoded project ID."""
    return firestore.Client(project=PROJECT_ID)


def get_pantry_items(category: str = "") -> list[dict]:
    """Retrieves current items in the user's pantry from Firestore.

    Args:
        category: Optional category filter (e.g. 'Produce', 'Grains', 'Dairy', 'Pantry Staples').

    Returns:
        List of pantry item dictionaries containing id, name, category, quantity, and expiration_date.
    """
    db = _get_firestore_client()
    pantry_ref = db.collection("pantry_items")

    if category:
        docs = pantry_ref.where("category", "==", category).stream()
    else:
        docs = pantry_ref.stream()

    items = [doc.to_dict() for doc in docs]
    return items


def add_pantry_item(
    name: str, category: str, quantity: str, expiration_date: str = ""
) -> dict:
    """Adds a new ingredient or item to the user's pantry in Firestore.

    Args:
        name: Name of the ingredient/item (e.g. 'Avocado', 'Olive Oil').
        category: Category of the item (e.g. 'Produce', 'Grains', 'Dairy', 'Pantry Staples').
        quantity: Quantity string (e.g. '2 units', '500g').
        expiration_date: Optional expiration date (e.g. '2026-10-15').

    Returns:
        Dictionary representing the created or updated pantry item.
    """
    db = _get_firestore_client()
    doc_id = f"pantry-{uuid.uuid4().hex[:6]}"
    item_data = {
        "id": doc_id,
        "name": name,
        "category": category,
        "quantity": quantity,
        "expiration_date": expiration_date,
    }
    db.collection("pantry_items").document(doc_id).set(item_data)
    return item_data


def get_recipes(cuisine: str = "") -> list[dict]:
    """Retrieves available recipes from the Firestore recipe database.

    Args:
        cuisine: Optional cuisine filter (e.g. 'Italian', 'Mexican', 'Asian').

    Returns:
        List of recipe dictionaries containing title, cuisine, prep_time_minutes, ingredients, instructions, and tags.
    """
    db = _get_firestore_client()
    recipes_ref = db.collection("recipes")

    if cuisine:
        docs = recipes_ref.where("cuisine", "==", cuisine).stream()
    else:
        docs = recipes_ref.stream()

    recipes = [doc.to_dict() for doc in docs]
    return recipes


def add_recipe(
    title: str,
    cuisine: str,
    prep_time_minutes: int,
    ingredients: list[str],
    instructions: str,
    tags: list[str] = None,
) -> dict:
    """Saves a new recipe to the Firestore database.

    Args:
        title: Title of the recipe (e.g. 'Avocado Toast').
        cuisine: Cuisine style (e.g. 'American', 'Italian').
        prep_time_minutes: Preparation time in minutes.
        ingredients: List of ingredient names needed for the recipe.
        instructions: Step-by-step cooking instructions.
        tags: Optional list of tags (e.g. ['Breakfast', 'Quick', 'Vegetarian']).

    Returns:
        Dictionary representing the saved recipe document.
    """
    db = _get_firestore_client()
    doc_id = f"recipe-{uuid.uuid4().hex[:6]}"
    recipe_data = {
        "id": doc_id,
        "title": title,
        "cuisine": cuisine,
        "prep_time_minutes": prep_time_minutes,
        "ingredients": ingredients,
        "instructions": instructions,
        "tags": tags or [],
    }
    db.collection("recipes").document(doc_id).set(recipe_data)
    return recipe_data


def check_pantry_recipe_availability(recipe_title: str) -> dict:
    """Checks if the user has enough ingredients in their pantry to make a specific recipe.

    Args:
        recipe_title: The title or keyword of the recipe to check (e.g. 'Classic Mushroom Risotto', 'Pasta').

    Returns:
        Dictionary detailing available ingredients, missing ingredients, match percentage, and readiness.
    """
    db = _get_firestore_client()

    # 1. Search for matching recipe
    recipes_docs = db.collection("recipes").stream()
    matching_recipes = [
        doc.to_dict()
        for doc in recipes_docs
        if recipe_title.lower() in doc.to_dict().get("title", "").lower()
    ]

    if not matching_recipes:
        return {"error": f"No recipe found matching '{recipe_title}'."}

    recipe = matching_recipes[0]
    required_ingredients = recipe.get("ingredients", [])

    # 2. Fetch current pantry items
    pantry_docs = db.collection("pantry_items").stream()
    pantry_names = [
        doc.to_dict().get("name", "").lower() for doc in pantry_docs
    ]

    # 3. Match ingredients
    available = []
    missing = []

    for req in required_ingredients:
        req_lower = req.lower()
        if any(
            p_name in req_lower or req_lower in p_name for p_name in pantry_names
        ):
            available.append(req)
        else:
            missing.append(req)

    match_pct = (
        int((len(available) / len(required_ingredients)) * 100)
        if required_ingredients
        else 0
    )

    return {
        "recipe_title": recipe.get("title"),
        "match_percentage": f"{match_pct}%",
        "available_ingredients": available,
        "missing_ingredients": missing,
        "can_cook_now": len(missing) == 0,
    }


def search_public_recipes(query: str) -> list[dict]:
    """Searches TheMealDB public recipe database for real online recipes matching a term or ingredient.

    Args:
        query: Search term or main ingredient (e.g. 'chicken', 'pasta', 'pie').

    Returns:
        List of matching public recipes with title, category, cuisine area, instructions snippet, and image URL.
    """
    encoded_query = urllib.parse.quote(query.strip())
    url = f"https://www.themealdb.com/api/json/v1/1/search.php?s={encoded_query}"

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode("utf-8"))
            meals = data.get("meals") or []
            results = []

            for meal in meals[:3]:  # Limit to top 3 matching meals
                results.append({
                    "title": meal.get("strMeal"),
                    "category": meal.get("strCategory"),
                    "cuisine_area": meal.get("strArea"),
                    "instructions_snippet": (
                        meal.get("strInstructions", "")[:250] + "..."
                        if meal.get("strInstructions")
                        else ""
                    ),
                    "image_url": meal.get("strMealThumb"),
                })

            if not results:
                return [{"message": f"No public recipes found for query: '{query}'."}]

            return results
    except Exception as e:
        return [{"error": f"Failed to reach public recipe API: {str(e)}"}]


def generate_dish_image(item_name: str) -> dict:
    """Generates an image for a food item or recipe using gemini-3.1-flash-lite-image in the global region,
    saves it locally as an artifact, uploads it to Cloud Storage, and returns the public URL.

    Args:
        item_name: Name or description of the dish/item (e.g. 'Classic Mushroom Risotto', 'Garlic Butter Pasta').

    Returns:
        Dictionary containing item_name, local_artifact_path, and public_url.
    """
    try:
        client = genai.Client(
            vertexai=True,
            project=PROJECT_ID,
            location="global",
        )

        prompt = f"A delicious, high-quality, professional food photograph of {item_name}"
        response = client.models.generate_content(
            model="gemini-3.1-flash-lite-image",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE"],
            ),
        )

        img_bytes = None
        mime_type = "image/jpeg"
        for part in response.candidates[0].content.parts:
            if part.inline_data:
                img_bytes = part.inline_data.data
                mime_type = part.inline_data.mime_type or mime_type
                break

        if not img_bytes:
            return {"error": f"Failed to generate image for '{item_name}'."}

        ext = "png" if "png" in mime_type else "jpg"
        os.makedirs("artifacts", exist_ok=True)
        filename = f"dish_{uuid.uuid4().hex[:6]}.{ext}"
        artifact_path = os.path.join("artifacts", filename)

        with open(artifact_path, "wb") as f:
            f.write(img_bytes)

        # Upload to Cloud Storage bucket
        storage_client = storage.Client(project=PROJECT_ID)
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(f"images/{filename}")
        blob.upload_from_filename(artifact_path, content_type=mime_type)

        public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/images/{filename}"

        return {
            "item_name": item_name,
            "artifact_path": artifact_path,
            "public_url": public_url,
        }
    except Exception as e:
        return {"error": f"Failed to generate and upload dish image: {str(e)}"}
