from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = "secretkey"  # change in production

# ----------- Database Setup ----------
def init_db():
    conn = sqlite3.connect("forum.db")
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY, username TEXT, password TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS topics(id INTEGER PRIMARY KEY, title TEXT, content TEXT, user_id INTEGER)")
    cur.execute("CREATE TABLE IF NOT EXISTS replies(id INTEGER PRIMARY KEY, content TEXT, topic_id INTEGER, user_id INTEGER)")
    conn.commit()
    conn.close()

init_db()

# ----------- Routes ----------
@app.route("/")
def index():
    conn = sqlite3.connect("forum.db")
    cur = conn.cursor()
    cur.execute("SELECT topics.id, title, content, username FROM topics JOIN users ON topics.user_id=users.id")
    topics = cur.fetchall()
    conn.close()
    return render_template("index.html", topics=topics)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("forum.db")
        cur = conn.cursor()
        cur.execute("INSERT INTO users(username,password) VALUES(?,?)", (username, password))
        conn.commit()
        conn.close()
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("forum.db")
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = cur.fetchone()
        conn.close()

        if user:
            session["user_id"] = user[0]
            session["username"] = user[1]
            return redirect(url_for("index"))
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

@app.route("/create_topic", methods=["GET", "POST"])
def create_topic():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]

        conn = sqlite3.connect("forum.db")
        cur = conn.cursor()
        cur.execute("INSERT INTO topics(title, content, user_id) VALUES(?,?,?)", (title, content, session["user_id"]))
        conn.commit()
        conn.close()
        return redirect(url_for("index"))
    return render_template("create_topic.html")

@app.route("/topic/<int:topic_id>", methods=["GET", "POST"])
def topic(topic_id):
    conn = sqlite3.connect("forum.db")
    cur = conn.cursor()
    cur.execute("SELECT title, content, username FROM topics JOIN users ON topics.user_id=users.id WHERE topics.id=?", (topic_id,))
    topic = cur.fetchone()

    cur.execute("SELECT content, username FROM replies JOIN users ON replies.user_id=users.id WHERE topic_id=?", (topic_id,))
    replies = cur.fetchall()
    conn.close()

    if request.method == "POST":
        reply_content = request.form["reply"]
        conn = sqlite3.connect("forum.db")
        cur = conn.cursor()
        cur.execute("INSERT INTO replies(content, topic_id, user_id) VALUES(?,?,?)", (reply_content, topic_id, session["user_id"]))
        conn.commit()
        conn.close()
        return redirect(url_for("topic", topic_id=topic_id))

    return render_template("topic.html", topic=topic, replies=replies)

if __name__ == "__main__":
    app.run(debug=True)
