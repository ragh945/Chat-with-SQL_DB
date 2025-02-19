import sqlite3

connection=sqlite3.connect("Student.db")

cursor=connection.cursor()

table_info="""
create table student(NAME VARCHAR(25),
CLASS VARCHAR(25),SECTION VARCHAR(25),MARKS INT)"""

cursor.execute(table_info)

cursor.execute('''Insert into student values("Raghu","DataScience","A",85)''')
cursor.execute('''Insert into student values("Bhanu","DataScience","A",100)''')
cursor.execute('''Insert into student values("Vamshi","Data Analysis","A",85)''')
cursor.execute('''Insert into student values("Charan","Devops","B",95)''')
cursor.execute('''Insert into student values("Khan","DataScience","B",80)''')
cursor.execute('''Insert into student values("PK","Machine Learning","A",85)''')
cursor.execute('''Insert into student values("Tharun","Generative AI","B",85)''')
cursor.execute('''Insert into student values("Siri","AI","A",70)''')


print("The inserted records are ")
data=cursor.execute("""select * from student""")

for row in data:
    print(row)


connection.commit()
connection.close()
