import json


# ---------- Load JSON Data ----------
def load_data(filename):
    with open(filename, "r") as file:
        return json.load(file)


# ---------- Save JSON Data ----------
def save_data(data, filename):
    with open(filename, "w") as file:
        json.dump(data, file, indent=4)


# ---------- Data Cleaning ----------
def clean_data(data):

    # Remove users with missing or empty names
    data["users"] = [
        user for user in data["users"]
        if user.get("name") and user["name"].strip()
    ]

    # Remove duplicate friends for each user
    for user in data["users"]:
        user["friends"] = list(set(user.get("friends", [])))

    # Remove inactive users (no friends and no liked pages)
    data["users"] = [
        user for user in data["users"]
        if len(user.get("friends", [])) + len(user.get("liked_pages", [])) > 0
    ]

    # Remove duplicate pages using page id
    unique_pages = {}
    for page in data["pages"]:
        unique_pages[page["id"]] = page
    data["pages"] = list(unique_pages.values())

    return data


# ---------- Display Users and Connections ----------
def display_users(data):
    print("\nUsers and Their Connections:\n")
    for user in data["users"]:
        print(
            f"{user['name']} (ID: {user['id']}) | "
            f"Friends: {user['friends']} | "
            f"Liked Pages: {user['liked_pages']}"
        )

    print("\nPages:\n")
    for page in data["pages"]:
        print(f"{page['id']} : {page['name']}")


# ---------- People You May Know Recommendation ----------
def find_people_you_may_know(user_id, data):

    # Create user to friends mapping
    user_friends = {
        user["id"]: set(user.get("friends", []))
        for user in data["users"]
    }

    if user_id not in user_friends:
        return []

    direct_friends = user_friends[user_id]
    suggestions = {}

    # Count mutual friends for recommendation
    for friend in direct_friends:
        for mutual in user_friends.get(friend, []):
            if mutual != user_id and mutual not in direct_friends:
                suggestions[mutual] = suggestions.get(mutual, 0) + 1

    # Sort users based on mutual friend count
    sorted_suggestions = sorted(
        suggestions.items(),
        key=lambda x: (-x[1], x[0])
    )

    return [user for user, _ in sorted_suggestions]


# ---------- Pages You Might Like Recommendation ----------
def find_pages_you_might_like(user_id, data):

    user_pages = {
        user["id"]: set(user.get("liked_pages", []))
        for user in data["users"]
    }

    if user_id not in user_pages:
        return []

    user_liked_pages = user_pages[user_id]
    page_scores = {}

    for other_user, pages in user_pages.items():
        if other_user != user_id:
            shared_pages = user_liked_pages.intersection(pages)
            if shared_pages:
                for page in pages:
                    if page not in user_liked_pages:
                        page_scores[page] = page_scores.get(page, 0) + len(shared_pages)

    if page_scores:
        return [page for page, _ in sorted(page_scores.items(), key=lambda x: -x[1])]

    page_popularity = {}
    for pages in user_pages.values():
        for page in pages:
            if page not in user_liked_pages:
                page_popularity[page] = page_popularity.get(page, 0) + 1

    return [page for page, _ in sorted(page_popularity.items(), key=lambda x: -x[1])]



# ---------- Text-Based Visualization ----------
def visualize_friends_distribution(data):

    # Visualize friend count using text bars
    print("\nFriends Distribution:\n")
    for user in data["users"]:
        count = len(user.get("friends", []))
        print(f"{user['name']:<15} | {'#' * count} ({count})")


def visualize_page_popularity(data):

    page_count = {page["id"]: 0 for page in data["pages"]}

    for user in data["users"]:
        for page in user.get("liked_pages", []):
            page_count[page] += 1

    print("\nPage Popularity:\n")
    for page_id, count in page_count.items():
        stars = "*" * count if count > 0 else "-"
        print(f"Page {page_id}: {stars}")



# ---------- Main Execution ----------
raw_data = load_data("data.json")
cleaned_data = clean_data(raw_data)
save_data(cleaned_data, "cleaned_codebook_data.json")

display_users(cleaned_data)

user_id = 1
people_recommendations = find_people_you_may_know(user_id, cleaned_data)
page_recommendations = find_pages_you_might_like(user_id, cleaned_data)

print(f"\nPeople You May Know for User {user_id}: {people_recommendations}")
print(f"Pages You Might Like for User {user_id}: {page_recommendations}")

visualize_friends_distribution(cleaned_data)
visualize_page_popularity(cleaned_data)
