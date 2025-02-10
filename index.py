from flask import Flask,render_template,redirect,request,url_for,flash,session
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "digiresi123"

#DBコネクト
def conn_db():
    conn = mysql.connector.connect(
        host = "127.0.0.1",
        user = "root",
        password = "P@ssw0rd",
        database = "digiresi"
    )
    return conn



#ログイン
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        
        try:   
            conn = conn_db()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
            user = cursor.fetchone()
        except mysql.connector.Error as e:
            flash("データベースエラーが発生しました。", "danger")
            print(f"MySQL Error: {e}")
            return redirect(url_for("login"))
        finally:
            conn.close()
        
        if user and check_password_hash(user["password_hash"], password):
            session["user_id"] = user["user_id"]
            flash("ログインに成功しました！", "success")
            return render_template("index.html")
        else:
            flash("ユーザー名またはパスワードが間違っています。", "danger")
            return redirect(url_for("login"))
        
    return render_template("login.html")



#パスワード再設定
@app.route("/reset_pass", methods=["GET", "POST"])
def reset_pass():
    if request.method == "POST":
        username = request.form["login_f_username"]
        new_password = request.form["login_f_password"]
        new_password_hash = generate_password_hash(new_password)
        
        conn = conn_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        if not user:
            flash("そのユーザー名は登録されていません。", "danger")
        else:
            cursor.execute(
                "UPDATE users SET password_hash = %s WHERE username = %s",
                (new_password_hash, username)
            )
            conn.commit()
            flash("パスワードがリセットされました。", "success")
        conn.close()
        
        return redirect(url_for("login"))
    
    return render_template("login_forgot.html")



#新規会員登録
@app.route("/membership", methods=["GET", "POST"])
def membership():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        password_hash = generate_password_hash(password)
        
        conn = conn_db()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO users (username, password_hash) VALUES (%s,%s)",
                (username, password_hash)
            )
            conn.commit()
            flash("アカウントが作成されました。ログインしてください。", "success")
            return redirect(url_for("login"))
        except mysql.connector.errors.IntegrityError:
            flash("そのユーザー名は既に存在します。", "danger")
        finally:
            conn.close()
            
    return render_template("create_account.html")



#トップページ
@app.route("/index", methods=["GET", "POST"])
def index():
    return render_template("index.html")



#スキャン確認
@app.route("/scan_result", methods=["GET", "POST"])
def scan_result():
    return render_template("scan_result.html")



#スキャン完了
@app.route("/completed")
def completed():
    return render_template("completed.html")



#ログアウト
@app.route("/logout")
def logout():
    session.pop("user_id", None)
    flash("ログアウトしました。", "success")
    return redirect(url_for("login"))



if __name__ == "__main__":
    app.route(debug=True)
