@app.route('/customerDetails', methods=['POST'])
def customerDetails():
  email = request.form['Email Address']
  cursor = g.conn.execute("select first_name, last_name, email_id from customer where email_id ='" + email + "';")
  names = []
  emails = []
  for result in cursor:
    names.append(result['first_name'] + result['last_name'])  # can also be accessed using result[0]
    emails.append(result['email_id']) 
  cursor.close()
  context = dict(data1 = names, data2 = emails)
  return render_template("trackstatus.html", **context)