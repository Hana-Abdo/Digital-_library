from flask import Flask, request, jsonify, render_template, send_from_directory
from pymongo import MongoClient
from bson import ObjectId
import hashlib, random, pandas as pd, os

app = Flask(__name__)
# -------------------- MongoDB Setup --------------------
client = MongoClient("mongodb://localhost:27017/")
db = client['digital_library']

# CSV Files
files = {
    'books.csv': 'books',
    'childrenstories.csv': 'childrenstories',
    'novels.csv':'novels',
    'podcasts.csv': 'podcasts'
}

for file_name, collection_name in files.items():
    try:
        df = pd.read_csv(file_name)
        data = df.to_dict(orient='records')  
        if db[collection_name].count_documents({}) == 0:
            db[collection_name].insert_many(data)
            print(f"{collection_name} uploaded successfully")
    except FileNotFoundError:
        print(f"{file_name} not found")

users_collection = db['users']
movies = [
    {"id": 1, "title": "The Shawshank Redemption (1994)", "image_url": "img/img/Movies/photo1.jpeg.jpg", "movie_url": "videos/video1.mp4"},
    {"id": 2, "title": "The Godfather (1972)", "image_url": "img/img/Movies/photo2.jpeg.jpg", "movie_url": "videos/video2.mp4"},
    {"id": 3, "title": "The Dark Knight (2008)", "image_url": "img/img/Movies/photo3.jpeg.jpg", "movie_url": "videos/video3.mp4"},
    {"id": 4, "title": "The Godfather Part II (1974)", "image_url": "img/img/Movies/photo4.jpeg.jpg", "movie_url": "videos/video4.mp4"},
    {"id": 5, "title": "12 Angry Men (1957)", "image_url": "img/img/Movies/photo5.jpeg.jpg", "movie_url": "videos/video5.mp4"},
    {"id": 6, "title": "Schindler's List (1993)", "image_url": "img/img/Movies/photo6.jpeg.jpg", "movie_url": "videos/video6.mp4"},
    {"id": 7, "title": "LOTR: Return of the King (2003)", "image_url": "img/img/Movies/photo7.jpeg.jpg", "movie_url": "videos/video7.mp4"},
    {"id": 8, "title": "Pulp Fiction (1994)", "image_url": "img/img/Movies/photo8.jpeg.jpg", "movie_url": "videos/video8.mp4"},
    {"id": 9, "title": "LOTR: Fellowship (2001)", "image_url": "img/img/Movies/photo9.jpeg.jpg", "movie_url": "videos/video9.mp4"},
    {"id": 10, "title": "The Good, the Bad and the Ugly (1966)", "image_url": "img/img/Movies/photo10.jpeg.jpg", "movie_url": "videos/video10.mp4"},
    {"id": 11, "title": "Forrest Gump (1994)", "image_url": "img/img/Movies/photo11.jpeg.jpg", "movie_url": "videos/video11.mp4"},
    {"id": 12, "title": "Fight Club (1999)", "image_url": "img/img/Movies/photo12.jpeg.jpg", "movie_url": "videos/video12.mp4"},
    {"id": 13, "title": "LOTR: The Two Towers (2002)", "image_url": "img/img/Movies/photo13.jpeg.jpg", "movie_url": "videos/video13.mp4"},
    {"id": 14, "title": "Inception (2010)", "image_url": "img/img/Movies/photo14.jpeg.jpg", "movie_url": "videos/video14.mp4"},
    {"id": 15, "title": "Star Wars: Episode V - The Empire Strikes Back (1980)", "image_url": "img/img/Movies/photo1.jpeg.jpg", "movie_url": "videos/video15.mp4"}
]

# -------------------- User Functions --------------------
def create_user(collection, user_data: dict):
    result = db[collection].insert_one(user_data)
    return f"User created with ID: {result.inserted_id}"

def read_user(collection, query: dict):
    user = db[collection].find_one(query)
    return user if user else "User not found"

def update_user(collection, query: dict, new_data: dict):
    result = db[collection].update_one(query, {"$set": new_data})
    return "User updated" if result.modified_count > 0 else "No user updated"

def delete_user(collection, query: dict):
    result = db[collection].delete_one(query)
    return "User deleted" if result.deleted_count > 0 else "No user deleted"

def register_user(name, email, password):
    if users_collection.find_one({"email": email}):
        return "Email already registered!"
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    user_data = {"name": name, "email": email, "password": hashed_password}
    users_collection.insert_one(user_data)
    return "User registered successfully!"

# -------------------- Item Functions --------------------
def get_all_items():
    return (
        list(db["books"].find()) +
        list(db["novels"].find()) +
        list(db["movies"].find()) +
        list(db["podcasts"].find()) +
        list(db["childrenstories"].find())
    )

def search_all(data, **kwargs):
    results = data
    for key, value in kwargs.items():
        if key in ['title', 'category', 'director', 'host']:
            results = [item for item in results if value.lower() in item.get(key,'').lower()]
        elif key == 'author':
            results = [item for item in results if value.lower() in item.get('author','').lower() or value.lower() in item.get('authors','').lower()]
        elif key == 'keyword':
            results = [item for item in results if value.lower() in item.get('description','').lower()]
        elif key == 'year':
            results = [item for item in results if item.get('year') == int(value)]
        elif key == 'rating':
            results = [item for item in results if item.get('rating',0) >= float(value)]
    return results

def search_backend(**kwargs):
    all_items = get_all_items()
    results = search_all(all_items, **kwargs)
    return {"results": results}

def get_all_reviews(item_collection):
    items = db[item_collection].find()
    result = []
    for item in items:
        item_info = {"_id": str(item["_id"]), "title": item.get("title", ""), "reviews": item.get("reviews", [])}
        result.append(item_info)
    return result

def get_all_notes(item_collection):
    items = db[item_collection].find()
    result = []
    for item in items:
        item_info = {"_id": str(item["_id"]), "title": item.get("title", ""), "notes": item.get("notes", [])}
        result.append(item_info)
    return result

def books_statistics(item_collection="books"):
    items = db[item_collection].find()
    stats = []
    for item in items:
        num_reviews = len(item.get("reviews", []))
        num_notes = len(item.get("notes", []))
        total_activity = num_reviews + num_notes
        stats.append({"title": item.get("title", ""), "reviews_count": num_reviews, "notes_count": num_notes, "total_activity": total_activity})
    stats_sorted = sorted(stats, key=lambda x: x["total_activity"], reverse=True)
    return stats_sorted

def positive_message(username, book_title):
    messages = [
        "🔥 Amazing work! Truly impressive!",
        "💪 Keep going… you're leveling up every day!",
        "🚀 Outstanding performance! Your passion for reading really shows!",
        "🏆 Great achievement! You should be proud!",
        "📚 Your mind is growing stronger—keep it up, champion!",
        "✨ Excellent progress! You're doing fantastic!",
        "🌟 You're crushing it! Keep pushing forward!",
        "🔥 You're on fire! Amazing dedication!",
        "💥 Brilliant effort! You're unstoppable!",
        "🌈 Keep shining, you're doing amazing!"
    ]
    msg = random.choice(messages)
    return f"🎉 Congrats {username}! You finished: {book_title}\n{msg}"

def switch_language(item, lang="en"):
    result = {}
    for key in item:
        if key.endswith("_en") or key.endswith("_ar"):
            base = key[:-3]
            result[base] = item.get(f"{base}_{lang}", item.get(f"{base}_en", ""))
        elif not "_" in key:
            result[key] = item[key]
    return result

# -------------------- Flask Routes --------------------
@app.route('/')
def home():
    return render_template('project.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        return render_template('categories.html', username=username)
    return render_template('login.html')

@app.route('/categories')
def categories():
    return render_template('categories.html')

@app.route('/books')
def books():
    books_data = list(db['books'].find())
    for book in books_data:
        book['_id'] = str(book['_id'])
    return render_template('books.html', books=books_data)

@app.route('/stories')
def stories():
    images_folder = 'img/img/kids' 
    img_files = os.listdir(os.path.join(app.static_folder, images_folder))
    stories_list = []
    for img in img_files:
        name_base = os.path.splitext(img)[0]
        stories_list.append({"img_name": img, "story_name": name_base})
    return render_template('stories.html', stories=stories_list)
  
@app.route('/story/<story_name>')
def story_page(story_name):
    return render_template(f"{story_name}.html")
@app.route('/pdf/<filename>')
def serve_pdf(filename):
    return send_from_directory(os.path.join(app.static_folder, 'pdf'), filename)

@app.route('/novels')
def novels_page():
    novels = list(db['novels'].find())
    for novel in novels:
        novel['_id'] = str(novel['_id'])
        if 'pdf_url' not in novel:
            novel['pdf_url'] = ''
    return render_template('novels.html', novels=novels)


@app.route('/seminars')
@app.route('/seminars.html')
def seminars():
    return render_template('seminars.html')

# -------------------- PDF Route --------------------
@app.route('/novel_pdf/<novel_id>')
def get_pdf(novel_id):
    try:
        novel = db['novels'].find_one({"_id": ObjectId(novel_id)})
        if novel and "pdf_file" in novel:
            pdf_filename = novel["pdf_file"]
            return send_from_directory(os.path.join(app.static_folder, "pdf"), pdf_filename)
        else:
            return "PDF not found", 404
    except Exception as e:
        return f"Error: {str(e)}", 500

# -------------------- Interaction Routes --------------------
@app.route("/like", methods=["POST"])
def like_book():
    data = request.json
    db.likes.insert_one({"book_id": data["book_id"]})
    return jsonify({"message": "liked"})

@app.route("/favorite", methods=["POST"])
def favorite_book():
    data = request.json
    db.favorites.insert_one({"book_id": data["book_id"]})
    return jsonify({"message": "favorite added"})

@app.route("/playlist", methods=["POST"])
def playlist_book():
    data = request.json
    db.playlist.insert_one({"book_id": data["book_id"]})
    return jsonify({"message": "playlist added"})

@app.route("/comment", methods=["POST"])
def comment_book():
    data = request.json
    db.comments.insert_one({"book_id": data["book_id"], "comment": data["comment"]})
    return jsonify({"message": "comment added"})

# -------------------- User API --------------------
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    result = register_user(name, email, password)
    return jsonify({"message": result})

@app.route('/users', methods=['GET'])
def get_users():
    users = list(db['users'].find({}, {"password":0}))
    for u in users:
        u["_id"] = str(u["_id"])
    return jsonify(users)

@app.route('/users/<user_id>', methods=['GET'])
def get_user(user_id):
    user = db['users'].find_one({"_id": ObjectId(user_id)}, {"password":0})
    if user:
        user["_id"] = str(user["_id"])
        return jsonify(user)
    return jsonify({"message": "User not found"}), 404

@app.route('/users/<user_id>', methods=['PUT'])
def update_user_route(user_id):
    data = request.json
    result = update_user('users', {"_id": ObjectId(user_id)}, data)
    return jsonify({"message": result})

@app.route('/users/<user_id>', methods=['DELETE'])
def delete_user_route(user_id):
    result = delete_user('users', {"_id": ObjectId(user_id)})
    return jsonify({"message": result})

@app.route('/search', methods=['GET'])
def search_items():
    args = request.args.to_dict()
    results = search_backend(**args)
    for item in results['results']:
        item['_id'] = str(item['_id'])
    return jsonify(results)

@app.route('/reviews/<item_collection>', methods=['GET'])
def get_reviews(item_collection):
    reviews = get_all_reviews(item_collection)
    return jsonify(reviews)

@app.route('/notes/<item_collection>', methods=['GET'])
def get_notes(item_collection):
    notes = get_all_notes(item_collection)
    return jsonify(notes)

@app.route('/stats/books', methods=['GET'])
def books_stats():
    stats = books_statistics("books")
    return jsonify(stats)

@app.route('/positive_message', methods=['POST'])
def send_positive_message():
    data = request.json
    username = data.get('username')
    book_title = data.get('book_title')
    msg = positive_message(username, book_title)
    return jsonify({"message": msg})

@app.route('/switch_language', methods=['POST'])
def switch_lang():
    data = request.json
    item = data.get('item')
    lang = data.get('lang', 'en')
    result = switch_language(item, lang)
    return jsonify(result)

@app.route('/podcasts')
def podcasts():
    images_folder = 'img/podcasts'  # مكان الصور في static

    # جلب أسماء الصور
    image_files = os.listdir(os.path.join(app.static_folder, images_folder))
    podcasts_list = []

    for img in image_files:
        # الاسم بدون امتداد
        name_base = os.path.splitext(img)[0]  
        podcasts_list.append({
            "image_name": img,
            "podcast_name": name_base
        })

    return render_template('podcasts.html', podcasts=podcasts_list)

@app.route('/podcasts/<podcast_name>')
def podcast_page(podcast_name):
    try:
        return render_template(f"{podcast_name}.html")
    except:
        return "<h1>Podcast not found!</h1>",404

@app.route('/art_vibes')
def art_vibes():
    return render_template('art_vibes.html')

@app.route('/Businees_Insights')
def Businees_Insights():
    return render_template('Businees_Insights.html')

@app.route('/movies')
def movies_page():
    return render_template('movies.html', movies=movies)

@app.route('/movie/<int:movie_id>')
def movie_detail(movie_id):
    movie = next((m for m in movies if m['id'] == movie_id), None)
    if not movie:
        return "<h2>Movie not found</h2>"
    return render_template('movie_detail.html', movie=movie)
# -------------------- Run Flask --------------------
if __name__ == '__main__':
    app.run(debug=True)
