from flask import Flask,request,jsonify
from flask import render_template
import psycopg2
from config import host,password,user,db_name,port

app = Flask(__name__)

connection = psycopg2.connect( # подключаемся к бз
    host=host,
    user=user,
    password=password,
    database=db_name,
    port=port     
)


cursor = connection.cursor()
connection.autocommit = True # автокоммит

#создаем таблицу
create_table = cursor.execute(""" 
    CREATE TABLE IF NOT EXISTS book(
               ID SERIAL PRIMARY KEY,
               ИМЯ VARCHAR NOT NULL,
               АВТОР VARCHAR NOT NULL,
               ЖАНР VARCHAR NOT NULL,
               СТАТУС VARCHAR NOT NULL,
               ОЦЕНКА SERIAL NOT NULL
    )
""")

@app.route("/")
def show_site():
    cursor.execute("SELECT * FROM book WHERE ОЦЕНКА > 6")
    top_rank = cursor.fetchall()
    return render_template("site.html",top_rank=top_rank)


@app.route("/books",methods=["GET"])
def show_books():
        cursor.execute("SELECT * FROM book ORDER BY ОЦЕНКА DESC")
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


@app.route("/add-books")
def add_books():
    print("add_book")
    return render_template("form.html")



@app.route("/process",methods=["POST"])
def process_data():
        name = request.form.get('name')
        author = request.form.get("author")
        genre = request.form.get("genre")
        status = request.form.get("status")
        mark = request.form.get("mark")
        print(mark)
 
        cursor.execute("""
                INSERT INTO book (ОЦЕНКА,АВТОР,ЖАНР,СТАТУС,ИМЯ) VALUES(%s,%s,%s,%s,%s)
""",(mark,author,genre,status,name))
        
        return render_template("process.html")
        




if __name__ == "__main__":
    app.run(debug=True)

else:
     cursor.close()
     connection.close()

