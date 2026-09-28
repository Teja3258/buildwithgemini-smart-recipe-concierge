import json
import subprocess
import urllib.error
import urllib.request

PROJECT_ID = "qwiklabs-gcp-03-7698bbba51cd"


def get_access_token():
    return (
        subprocess.check_output(["gcloud", "auth", "print-access-token"])
        .decode("utf-8")
        .strip()
    )


def firestore_set_document(collection: str, doc_id: str, fields: dict, token: str):
    url = f"https://firestore.googleapis.com/v1/projects/{PROJECT_ID}/databases/(default)/documents/{collection}/{doc_id}"

    # Convert python dict to Firestore REST API field values
    firestore_fields = {}
    for key, val in fields.items():
        if isinstance(val, str):
            firestore_fields[key] = {"stringValue": val}
        elif isinstance(val, int):
            firestore_fields[key] = {"integerValue": str(val)}
        elif isinstance(val, list):
            array_vals = []
            for item in val:
                if isinstance(item, str):
                    array_vals.append({"stringValue": item})
            firestore_fields[key] = {"arrayValue": {"values": array_vals}}

    data = json.dumps({"fields": firestore_fields}).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        method="PATCH",
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))


def seed_database():
    """Seed Firestore database with initial pantry items and recipes."""
    print(f"Connecting to Firestore for project: '{PROJECT_ID}'...")
    token = get_access_token()

    # 1. Seed Pantry Items
    initial_pantry = [
        {
            "id": "pantry-001",
            "name": "Arborio Rice",
            "category": "Grains",
            "quantity": "500g",
            "expiration_date": "2026-12-31",
        },
        {
            "id": "pantry-002",
            "name": "Parmesan Cheese",
            "category": "Dairy",
            "quantity": "200g",
            "expiration_date": "2026-10-15",
        },
        {
            "id": "pantry-003",
            "name": "Olive Oil",
            "category": "Pantry Staples",
            "quantity": "1 Liter",
            "expiration_date": "2027-01-01",
        },
        {
            "id": "pantry-004",
            "name": "Garlic",
            "category": "Produce",
            "quantity": "3 bulbs",
            "expiration_date": "2026-10-20",
        },
        {
            "id": "pantry-005",
            "name": "Mushrooms",
            "category": "Produce",
            "quantity": "250g",
            "expiration_date": "2026-10-05",
        },
        {
            "id": "pantry-006",
            "name": "Cherry Tomatoes",
            "category": "Produce",
            "quantity": "300g",
            "expiration_date": "2026-10-08",
        },
    ]

    for item in initial_pantry:
        firestore_set_document("pantry_items", item["id"], item, token)
        print(f"  [+] Seeded pantry item: {item['name']} ({item['category']})")

    # 2. Seed Recipes
    initial_recipes = [
        {
            "id": "recipe-001",
            "title": "Classic Mushroom Risotto",
            "cuisine": "Italian",
            "prep_time_minutes": 35,
            "ingredients": [
                "Arborio Rice",
                "Mushrooms",
                "Parmesan Cheese",
                "Garlic",
                "Olive Oil",
            ],
            "instructions": "Sauté garlic and mushrooms in olive oil. Toast arborio rice, then gradually add warm broth while stirring. Finish with grated parmesan.",
            "tags": ["Vegetarian", "Dinner", "Italian"],
        },
        {
            "id": "recipe-002",
            "title": "Garlic Butter Pasta",
            "cuisine": "Italian",
            "prep_time_minutes": 15,
            "ingredients": [
                "Pasta",
                "Garlic",
                "Parmesan Cheese",
                "Olive Oil",
                "Black Pepper",
            ],
            "instructions": "Boil pasta. Sauté minced garlic in olive oil until fragrant. Toss cooked pasta with garlic oil and top with fresh parmesan cheese.",
            "tags": ["Quick", "Vegetarian", "Pasta"],
        },
        {
            "id": "recipe-003",
            "title": "Roasted Tomato & Garlic Bruschetta",
            "cuisine": "Italian",
            "prep_time_minutes": 20,
            "ingredients": [
                "Bread",
                "Cherry Tomatoes",
                "Garlic",
                "Olive Oil",
                "Basil",
            ],
            "instructions": "Dice cherry tomatoes and toss with minced garlic, olive oil, and basil. Spoon over toasted slices of crusty bread.",
            "tags": ["Appetizer", "Quick", "Vegetarian"],
        },
    ]

    for recipe in initial_recipes:
        firestore_set_document("recipes", recipe["id"], recipe, token)
        print(f"  [+] Seeded recipe: {recipe['title']} ({recipe['cuisine']})")

    print("\n✅ Firestore database seeded successfully!")


if __name__ == "__main__":
    seed_database()
