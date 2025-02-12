from flask import Flask,render_template,redirect,request,url_for,flash,session,request, jsonify
import mysql.connector, os, uuid, re, pytesseract
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from PIL import Image, ImageFilter, ImageOps

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



# アップロードされた画像を保存するディレクトリ
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER



# 拡張子が許可されているかを確認する関数
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



# Tesseract実行パス（Windowsの場合のみ必要）
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'



# カテゴリー分類用キーワード辞書
CATEGORY_KEYWORDS = {
    "食費": ["レストラン", "カフェ", "フード", "食品", "弁当", "ファストフード", "食事"],
    "交通費": ["タクシー", "電車", "バス", "交通", "航空券"],
    "宿泊費": ["ホテル", "旅館", "宿泊"],
    "日用品費": ["日用品", "ドラッグストア", "ホームセンター", "薬局"],
    "遊興費": ["映画館", "カラオケ", "テーマパーク", "遊園地", "遊興"],
    "雑費": ["雑貨", "その他"]
}



# カテゴリー分類関数
def classify_category(text):
    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text:
                return category
    return "雑費"  # 該当なしの場合は "雑費"



# 画像を指定領域で切り取ってOCRする関数
def extract_text_by_position(image_path):
    image = Image.open(image_path)

    # 日付抽出
    date_area = image.crop((450, 40, 700, 100))  # 必要に応じて座標調整
    date_text = pytesseract.image_to_string(date_area, lang='jpn').strip()

    # 金額抽出
    amount_area = image.crop((400, 250, 700, 320))  # 必要に応じて座標調整
    amount_text = pytesseract.image_to_string(amount_area, config='--psm 7').strip()

    # 店名抽出
    store_area = image.crop((450, 350, 750, 400))  # 必要に応じて座標調整
    store_text = pytesseract.image_to_string(store_area, lang='jpn').strip()

    return date_text, amount_text, store_text



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
            return redirect(url_for("index"))
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



# トップページ
@app.route('/index')
def index():
    category_id = request.args.get('category_id')  # URLからcategory_idを取得
    conn = conn_db()  # conn_db関数でMySQL接続を取得
    cursor = conn.cursor(dictionary=True)
    
    try:
        if category_id:
            # 特定のカテゴリーIDでフィルタリングするクエリ
            query = "SELECT image_path FROM receipts WHERE category_id = %s ORDER BY receipt_created_at DESC"
            cursor.execute(query, (category_id,))
            print(f"カテゴリーID {category_id} でフィルタリング中")
        else:
            # 全てのレシートを取得するクエリ
            query = "SELECT image_path FROM receipts ORDER BY receipt_created_at DESC"
            cursor.execute(query)
            print("全レシートを取得中")
        
        receipts = cursor.fetchall()  # クエリ結果を取得
    except Exception as e:
        print(f"データベースクエリエラー: {e}")
        receipts = []
    finally:
        cursor.close()
        conn.close()  # 必ず接続を閉じる

    # index.html に領収書画像のリストを渡して表示
    return render_template('index.html', receipts=receipts)



# カテゴリごとの領収書データを返すAPIエンドポイント
@app.route('/get_receipts/<int:category_id>', methods=['GET'])
def get_receipts(category_id):
    conn = conn_db()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # カテゴリに一致する領収書データを取得
        query = "SELECT image_path FROM receipts WHERE category_id = %s ORDER BY receipt_created_at DESC"
        cursor.execute(query, (category_id,))
        receipts = cursor.fetchall()
    except Exception as e:
        print(f"データベースクエリエラー: {e}")
        receipts = []
    finally:
        cursor.close()
        conn.close()

    # JSON形式で返す
    return jsonify(receipts)


# スキャン結果を表示するページ
@app.route('/scan_result')
def scan_result():
    image_filename = request.args.get('image')
    return render_template('scan_result.html', image_filename=image_filename)



#スキャン完了
@app.route("/completed")
def completed():
    return render_template("completed.html")



# 画像アップロード
@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            # 元のファイルの拡張子を取得（例: .jpg, .png）
            extension = os.path.splitext(file.filename)[1].lower()
            # UUID を使って一意のファイル名を生成
            unique_filename = f"{uuid.uuid4().hex}{extension}"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)

            # ファイルを保存
            file.save(file_path)
            print(f"ファイルが保存されました: {file_path}")
            print(f"生成されたファイル名: {unique_filename}")
            print(f"保存されたパス: {file_path}")

            # パスをWeb形式に変換してscan_result.htmlに渡す
            # web_file_path = f"static/uploads/{unique_filename}".replace('\\', '/')
            # print(f"Web用パス: {web_file_path}")

            web_file_path = url_for('static', filename=f'uploads/{unique_filename}')
            print(f"Flaskが生成したWebパス: {web_file_path}")
            
            # OCR処理
            extracted_text = ""
            store_name = ""
            receipt_date = ""
            amount = ""
            category = "未分類"
            try:
                image = Image.open(file_path)
                image = Image.open(file_path).convert('L')  # グレースケール変換
                image = ImageOps.invert(image)  # 明暗反転で文字を強調
                image = image.filter(ImageFilter.SHARPEN)   # シャープ化
                extracted_text = pytesseract.image_to_string(image, lang='jpn')

                extracted_text = pytesseract.image_to_string(image, lang='jpn')
                print("抽出されたテキスト:", extracted_text)

                # 右下部分を切り取って店名を抽出
                width, height = image.size
                right_bottom_region = image.crop((width * 0.6, height * 0.8, width, height))  # 右下20%部分
                store_name = pytesseract.image_to_string(right_bottom_region, lang='jpn').strip()
                print(f"右下領域から抽出した店名: {store_name}")

                # 日付の抽出と変換
                date_match = re.search(r'\d{4}[-/\.]\d{1,2}[-/\.]\d{1,2}', extracted_text)
                if date_match:
                    receipt_date = date_match.group().replace('/', '-').replace('.', '-')  # 変換してYYYY-MM-DD形式に
                    receipt_date = '-'.join([f"{int(part):02d}" for part in receipt_date.split('-')])
                    print(f"抽出された日付: {receipt_date}")

                # 金額を領収書の特定位置から抽出
                width, height = image.size
                amount_region = image.crop((width * 0.3, height * 0.5, width * 0.7, height * 0.6))  # 金額の領域を指定
                amount_text = pytesseract.image_to_string(amount_region, lang='eng')
                print(f"金額領域の抽出結果: {amount_text}")

                # 金額テキストを整形して数値だけにする
                amount_cleaned = re.sub(r'[^\d]', '', amount_text)  # 数字以外を除去
                print(f"最終抽出された金額: {amount_cleaned}")

                # カテゴリーをキーワードマッチングで分類
                category = classify_category(extracted_text)
                print(f"分類されたカテゴリー: {category}")
            except Exception as e:
                print(f"OCR処理に失敗しました: {e}")

            # scan_result.html にリダイレクトし、保存した画像を表示
            return render_template('scan_result.html', image_file=web_file_path, store_name=store_name, receipt_date=receipt_date, amount=amount_cleaned, category=category)
        else:
            flash('許可されていないファイル形式です。jpgまたはpngのみアップロード可能です。')
            return redirect(request.url)
    return render_template('upload.html')



#DBに登録
@app.route('/save', methods=['POST'])
def save():
    print("フォームデータ:", request.form.to_dict())  # フォームデータを確認
    print("sessionのデータ:", session)
    try:
        # フォームデータを取得
        store_name = request.form['store_name']
        receipt_date = request.form['receipt_date']
        amount = request.form['amount']
        category = request.form['category']
        image_file = request.form['image_file']
        user_id = session.get('user_id')

        # カテゴリーIDのマッピング
        category_mapping = {
            "食費": 1,
            "交通費": 2,
            "宿泊費": 3,
            "日用品費": 4,
            "遊興費": 5,
            "雑費": 6
        }
        category_id = category_mapping.get(category, 6)  # 未分類はデフォルトで6

        # MySQLにデータをINSERT
        conn = conn_db()
        cursor = conn.cursor()

        insert_query = """
        INSERT INTO receipts (store_name, receipt_date, amount, category_id, image_path, user_id)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        data = (store_name, receipt_date, amount, category_id, image_file, user_id)
        cursor.execute(insert_query, data)
        conn.commit()
        cursor.close()
        conn.close()

        flash('データが正常に登録されました！')
        return redirect('/completed')

    except Exception as e:
        print(f"MySQLへのINSERTに失敗しました: {e}")
        flash('データ登録に失敗しました。もう一度お試しください。')
        return redirect('/index')





#ログアウト
@app.route("/logout")
def logout():
    session.pop("user_id", None)
    flash("ログアウトしました。", "success")
    return redirect(url_for("login"))



if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
