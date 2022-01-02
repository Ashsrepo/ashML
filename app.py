from flask import Flask, render_template, request, redirect, url_for, session
from sqlite3 import*
from flask_mail import Mail, Message
from random import randrange
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression

app = Flask(__name__)
app.secret_key="ashishbhairocks"

app.config['MAIL_SERVER']="smtp.gmail.com"
app.config['MAIL_PORT']=587
app.config['MAIL_USERNAME']="zelnerash@gmail.com"
app.config['MAIL_PASSWORD']="ashishbhaidoodhmalai"
app.config['MAIL_USE_TLS']=True
app.config['MAIL_USE_SSL']=False
mail = Mail(app)


@app.route("/", methods=["GET","POST"])
def home():
	if "username" in session:
		return render_template("laptop.html", name=session["username"])
	else:
		return redirect(url_for('login'))


@app.route("/check", methods=["GET","POST"])
def check():
	if "username" in session:
		# import data
		data = pd.read_csv("Laptop_pricing1.csv")
		print(data.head())
		print(data.isnull().sum())

		data.drop(["Manufacturer"], axis='columns', inplace=True)
		print(data.head())

		# features and target
		features = data[["processing speed(GHz)", "Ram(gb)","SSD(gb)","Graphics(gb)","ScreenSize(inch)"]]
		target = data["Price"]
	
		print(features)
		print(target)

		# train test split
		x_train,x_test,y_train,y_test=train_test_split(features,target,random_state=100)

		# model 
		model = LinearRegression()
		model.fit(x_train, y_train)
	
		#performance
		train_score = model.score(x_train,y_train)  #score --> x_train ==> y_pred and y_train
		print("train score ", train_score)
		test_score = model.score(x_test,y_test) #score --> x_pred and compare with y_test
		print("test score",test_score)

		speed = float(request.form["speed"])
		RAM = int(request.form["RAM"])
		SSD = int(request.form["SSD"])
		graphics = int(request.form["graphics"])
		size = float(request.form["size"])

		d = [[speed, RAM, SSD, graphics, size]]
		#predict
		pred = model.predict(d)
		pr = round(pred.item(),2)
	
		res = "estimated price of laptop is ₹" + str(pr)
		return render_template("laptop.html", msg = res)
	else:
        	return redirect(url_for('login'))

@app.route("/logout", methods=["GET","POST"])
def logout():
	session.pop("username",	None)
	return redirect(url_for('login'))

@app.route("/login", methods=["GET","POST"])
def login():
	if request.method=="POST":
		un=request.form["un"]
		pw=request.form["pw"]
		con = None
		try:
			con = connect("lappy.db")
			cursor=con.cursor()
			sql="select * from users where username = '%s' and password = '%s'"
			cursor.execute(sql%(un,pw))
			data=cursor.fetchall()
			if len(data) == 0:
				return render_template("login.html", msg="invalid login")
			else:
				session["username"]=un
				return redirect(url_for('home'))
		except Exception as e:
			msg = "issue" + e
			return render_template("signup.html", msg=msg)
		finally:
			if con is not None:
				con.close()
	else:
		return render_template("login.html")


@app.route("/signup", methods=["GET","POST"]) 
def signup():
	if request.method == "POST": 
		un = request.form["un"]
		con = None
		try: 
			con = connect("lappy.db") 
			cursor = con.cursor()
			pw =""
			text = "abcdefghijklmnopqrstuvwxyz" 
			for i in range(6):
				pw = pw + text[randrange(len(text))]
			print(pw)
			sql = "insert into users values('%s', '%s')" 
			cursor.execute(sql %(un, pw)) 
			con.commit()
			msg = Message("Welcome to my Website", sender="zelnerash@gmail.com", recipients=[un])
			msg.body = "ur password is " + pw 
			mail.send(msg)
			return redirect(url_for('login'))
 
		except Exception as e:
			con.rollback()
			return render_template("signup.html", msg="user already registered " + str(e))
		finally:
			if con is not None:
				con.close()

	else:
		return render_template("signup.html")

@app.route("/forgotpassword",methods=["GET","POST"])
def forgotpassword():
	if request.method == "POST": 
		un = request.form["un"] 
		con = None
		try:
			con = connect("lappy.db") 
			cursor = con.cursor()
			sql = "select * from users where username = '%s'"
			cursor.execute(sql % (un))
			data = cursor.fetchall() 
			if len(data) == 0:
				return render_template("fp.html", msg = "user does not exists ")
			else:
				pw=""
				text = "abcdefghijklmnopqrstuvwxyz" 
				for i in range(6):
					pw = pw + text[randrange(len(text))]
				print(pw)
				sql = "update users set password = '%s' where username = '%s'" 
				cursor.execute(sql % (pw, un))
				con.commit()
				msg = Message("Welcome to my Website", sender="zelnerash@gmail.com", recipients=[un] )
				msg.body = "ur new password is " + pw 
				mail.send(msg)
				return redirect( url_for('login')) 
		except Exception as e:
			con.rollback()
			return render_template("signup.html", msg="user already registered" + str(e))
		finally:
			if con is not None:
				con.close()

	else:
		return render_template("fp.html")
if __name__=="__main__":
	app.run(debug=True)

