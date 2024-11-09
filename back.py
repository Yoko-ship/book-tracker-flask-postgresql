from flask import Flask,request,jsonify
from flask import render_template,redirect,url_for,flash
import psycopg2
from config import host,password,user,db_name,port
from flask_login import login_required,login_user,logout_user,current_user,LoginManager,UserMixin
from werkzeug.security import generate_password_hash,check_password_hash

app = Flask(__name__)


app.secret_key = "test_key"
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "/login"


connection = psycopg2.connect( # подключаемся к бз
    host=host,
    user=user,
    password=password,
    database=db_name,
    port=port     
)


cursor = connection.cursor()
connection.autocommit = True # автокоммит



create_user_tables = cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(
                                    ID SERIAL PRIMARY KEY,
                                    ИМЯ VARCHAR NOT NULL,
                                    ПОЧТА VARCHAR NOT NULL,
                                    ПАРОЛЬ VARCHAR NOT NULL
    )
""")
#создаем таблицу
create_table = cursor.execute(""" 
    CREATE TABLE IF NOT EXISTS book(
                ID SERIAL PRIMARY KEY,
                ИМЯ VARCHAR NOT NULL,
                АВТОР VARCHAR NOT NULL,
                ЖАНР VARCHAR NOT NULL,
                СТАТУС VARCHAR NOT NULL,
                ОЦЕНКА SERIAL NOT NULL,
                userId SERIAL NOT NULL,
                FOREIGN KEY(userId) REFERENCES users(id)
    )
""")



class User(UserMixin):
    def __init__(self,id):
        self.id = id


userEmail = None


@login_manager.user_loader
def load_user(user_id):
     return User(user_id)

@app.route("/")
def show_site():
    checked = userEmail
    if checked:
        cursor.execute("SELECT ID FROM users WHERE ПОЧТА = %s",(checked,))
        id_users = cursor.fetchone()
        users_texted_id = id_users[0]
        cursor.execute("SELECT * FROM book WHERE userId = %s AND ОЦЕНКА > 6",(users_texted_id,))
        top_rank = cursor.fetchall()
        return render_template("site.html",top_rank=top_rank)
    else:
        return render_template("site.html")

@app.route("/books",methods=["GET"])
def show_books():
        check_email = userEmail
        if check_email:
            cursor.execute("SELECT ID FROM users WHERE ПОЧТА = %s",(check_email,))
            get_id = cursor.fetchone()
            get_id_texted = get_id[0]
            cursor.execute("SELECT * FROM book WHERE userId = %s ORDER BY ОЦЕНКА DESC",(get_id_texted,))
            sorted_elements = cursor.fetchall()

            #* Получаем переменную где хранится idшник
            elements = request.args.get("id")

            selectElement = request.args.get("value")

            selectId = request.args.get("div-id")

            #* Удалаем строку по idшнику
            if elements:  
                cursor.execute("DELETE FROM book WHERE id = %s",(elements,))
            if selectElement and selectId:
                cursor.execute("UPDATE book SET СТАТУС = %s WHERE id = %s",(selectElement,selectId))

            return render_template("show_books.html",name_info=sorted_elements)
        else:
            return render_template("show_books.html")


@app.route("/add-books")
@login_required
def add_books():
    return render_template("form.html")



@app.route("/process",methods=["POST"])
@login_required
def process_data():
        name = request.form.get('name')
        author = request.form.get("author")
        genre = request.form.get("genre")
        status = request.form.get("status")
        mark = request.form.get("mark")
        cursor.execute("SELECT ID FROM users WHERE ПОЧТА = %s",(userEmail,))
        user_id = cursor.fetchone()
        user_texted_id = user_id[0]
 
        cursor.execute("""
                INSERT INTO book (ОЦЕНКА,АВТОР,ЖАНР,СТАТУС,ИМЯ,userId) VALUES(%s,%s,%s,%s,%s,%s)
""",(mark,author,genre,status,name,user_texted_id))
        
        return render_template("process.html")
        


@app.route("/register",methods=["POST","GET"])
def register():
    if request.method == "POST":
        user_name = request.form.get("name")
        user_email = request.form.get("email")
        user_password = request.form.get("password")
        global hashed_password
        hashed_password = generate_password_hash(user_password)

        #* Проверяем на существует ли почта
        cursor.execute("SELECT 1 FROM users WHERE ПОЧТА = %s",(user_email,))
        check_email = cursor.fetchone()
        if check_email:
            return render_template(("register.html",flash("Этот эмейл уже существует","error")))
        else:
            cursor.execute("INSERT INTO users (ИМЯ,ПОЧТА,ПАРОЛЬ) VALUES(%s,%s,%s)",(user_name,user_email,hashed_password))
            connection.commit()
            flash("Вы успешно зарегистрированы","success")
            return redirect("/login")
    
    return render_template("register.html")





# Авторизация
@app.route("/login",methods=["GET","POST"])
def logIn():
    if request.method == "POST":
        global userEmail
        userEmail = request.form.get("email")
        passwords = request.form.get("password")
        #* Получаем пароль с почты которого указал пользователь и сравниваем внизу()
        cursor.execute("SELECT ПАРОЛЬ , ID FROM users WHERE ПОЧТА = %s",(userEmail,))
        result = cursor.fetchone()
        if result:
            stored_password , user_id = result
            if check_password_hash(stored_password,passwords):
                user = User(user_id)
                login_user(user)
                return redirect("/profile")
            else:
                 flash("Введенные вами данные не совпадают", "error")
        else:
             flash("Пользователь не найден", "error")     
    return render_template("logIn.html")


@app.route("/logout")
def logout():
    if logout_user():
        global userEmail
        userEmail = None
    return render_template("logout.html")

@app.route("/profile")
@login_required
def profile():
    check_email = userEmail
    if check_email:
        cursor.execute("SELECT ИМЯ FROM users WHERE ПОЧТА = %s",(check_email,))
        user_name = cursor.fetchone()
        texted_name = user_name[0]
        return render_template("profile.html",name=texted_name)
    else:
        return render_template("profile.html")


if __name__ == "__main__":
    app.run(debug=True)

else:
     cursor.close()
     connection.close()

