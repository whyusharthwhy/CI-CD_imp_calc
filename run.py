from imp_calc import app



#checks if the run.py file has executed directly and not imported

if __name__ == '__main__':
	app.run(host='0.0.0.0',port =8080,debug=True)
