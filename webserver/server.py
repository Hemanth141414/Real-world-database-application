
"""
Columbia's COMS W4111.001 Introduction to Databases
Example Webserver
To run locally:
    python server.py
Go to http://localhost:8111 in your browser.
A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""
import os
  # accessible as a variable in index.html:
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response, url_for

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
stc_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
app = Flask(__name__, template_folder=tmpl_dir, static_folder=stc_dir)


#
# The following is a dummy URI that does not connect to a valid database. You will need to modify it to connect to your Part 2 database in order to use the data.
#
# XXX: The URI should be in the format of: 
#
#     postgresql://USER:PASSWORD@34.73.36.248/project1
#
# For example, if you had username zy2431 and password 123123, then the following line would be:
#
#     DATABASEURI = "postgresql://zy2431:123123@34.73.36.248/project1"
#
DATABASEURI = "postgresql://hp2581:499621@34.73.36.248/project1" # Modify this with your own credentials you received from Joseph!


#
# This line creates a database engine that knows how to connect to the URI above.
#
engine = create_engine(DATABASEURI)

#
# Example of running queries in your database
# Note that this will probably not work if you already have a table named 'test' in your database, containing meaningful data. This is only an example showing you how to run queries in your database using SQLAlchemy.
#
engine.execute("""CREATE TABLE IF NOT EXISTS test (
  id serial,
  name text
);""")
engine.execute("""INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace');""")


@app.before_request
def before_request():
  """
  This function is run at the beginning of every web request 
  (every time you enter an address in the web browser).
  We use it to setup a database connection that can be used throughout the request.

  The variable g is globally accessible.
  """
  try:
    g.conn = engine.connect()
  except:
    print("uh oh, problem connecting to database")
    import traceback; traceback.print_exc()
    g.conn = None

@app.teardown_request
def teardown_request(exception):
  """
  At the end of the web request, this makes sure to close the database connection.
  If you don't, the database could run out of memory!
  """
  try:
    g.conn.close()
  except Exception as e:
    pass


#
# @app.route is a decorator around index() that means:
#   run index() whenever the user tries to access the "/" path using a GET request
#
# If you wanted the user to go to, for example, localhost:8111/foobar/ with POST or GET then you could use:
#
#       @app.route("/foobar/", methods=["POST", "GET"])
#
# PROTIP: (the trailing / in the path is important)
# 
# see for routing: https://flask.palletsprojects.com/en/1.1.x/quickstart/#routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
#
usernames_Pass = {}
trackId_usernames = {}

@app.route('/')
def index():
  """
  request is a special object that Flask provides to access web request information:

  request.method:   "GET" or "POST"
  request.form:     if the browser submitted a form, this contains the data in the form
  request.args:     dictionary of URL arguments, e.g., {a:1, b:2} for http://localhost?a=1&b=2

  See its API: https://flask.palletsprojects.com/en/1.1.x/api/#incoming-request-data
  """

  # DEBUG: this is debugging code to see what request looks like
  print(request.args)


  #
  # example of a database query
  #
  cursor = g.conn.execute("select email_id, password, package.package_id from customer natural join sender natural join package")
  for result in cursor:
    usernames_Pass[result['email_id']] = result['password'] # can also be accessed using result[0]
    trackId_usernames[str(result['package_id'])] = result['email_id'] # can also be accessed using result[0]
  cursor.close()

  tracking = []
  cursor = g.conn.execute("select package_id from records natural join place natural join trasportaion;")
  for result in cursor:
      tracking.append(str(result["package_id"]))
  cursor.close()

  #
  # Flask uses Jinja templates, which is an extension to HTML where you can
  # pass data to a template and dynamically generate HTML based on the data
  # (you can think of it as simple PHP)
  # documentation: https://realpython.com/primer-on-jinja-templating/
  #
  # You can see an example template in templates/index.html
  #
  # context are the variables that are passed to the template.
  # for example, "data" key in the context variable defined below will be 
  # accessible as a variable in index.html:
  #
  #     # will print: [u'grace hopper', u'alan turing', u'ada lovelace']
  #     <div>{{data}}</div>
  #     
  #     # creates a <div> tag for each element in data
  #     # will print: 
  #     #
  #     #   <div>grace hopper</div>
  #     #   <div>alan turing</div>
  #     #   <div>ada lovelace</div>
  #     #
  #     {% for n in data %}
  #     <div>{{n}}</div>
  #     {% endfor %}
  #
  context = dict(userData = usernames_Pass, trackData = trackId_usernames, trackingAvail = tracking)


  #
  # render_template looks in the templates/ folder for files.
  # for example, the below file reads template/index.html
  #
  return render_template("index.html", **context)

#
# This is an example of a different path.  You can see it at:
# 
#     localhost:8111/another
#
# Notice that the function name is another() rather than index()
# The functions for each app.route need to have different names
#

@app.route('/back')
def back():
    context = dict(data = usernames_Pass)
    return render_template("index.html", **context)

@app.route('/another')
def another():
  return render_template("track.html")

@app.route('/customerinfo', methods=['GET'])
def customerinfo():
  email = request.args['email']
  cursor = g.conn.execute("select email_id, (first_name || ' ' || last_name) as name, (Street_Address || ', ' || Street_Name || ', ' || State || ', ' || Country) as address,  package.package_id, Service_Type, Category, Is_Fragile, Is_Hazardous, weight from customer natural join sender natural join package where email_id ='" + email + "';")
  customerdetails = {}
  packagearray = []
  count = 0
  for result in cursor:
        packagedetails = {}
        if not customerdetails:
            customerdetails['name'] = result['name']
            customerdetails['email_id'] = result['email_id']
            customerdetails['address'] = result['address']
        packagedetails["package_id"] = result["package_id"]
        packagedetails["service_type"] = result["service_type"]
        packagedetails["category"] = result["category"]
        packagedetails["weight"] = result["weight"]
        packagedetails["is_fragile"] = str(result["is_fragile"])
        packagedetails["is_hazardous"] = str(result["is_hazardous"])
        packagearray.insert(count, packagedetails)
        count = count + 1
  cursor.close()
  tracking = []
  cursor = g.conn.execute("select package_id from records natural join place natural join trasportaion;")
  for result in cursor:
      tracking.append(str(result["package_id"]))
  cursor.close()
  context = dict(data = customerdetails, packages = packagearray, trackingIds = tracking)
  return render_template("customerinfo.html", **context)


@app.route('/trackstatus', methods=['GET'])
def trackstatus():
  package = request.args['package']
  email = request.args['email']
  cursor = g.conn.execute("select * from records natural join place natural join trasportaion natural join transport where package_id = '" + package + "';")
  returnData = {}
  trackArray = []
  for result in cursor:
      trackdetails = {}    
      trackdetails["area"] = result["area_description"]
      trackdetails["departure_time"] = str(result["departure_time"])
      trackdetails["mode"] = result["mode"]
      trackArray.append(trackdetails) 
  cursor.close()
  returnData["trackArray"] = trackArray
  returnData["email"] = email     
  context = dict(data = returnData)
  return render_template("trackstatus.html", **context)



# Example of adding new data to the database
@app.route('/add', methods=['POST'])
def add():
  email_id = request.form['Email Address']
  Pass = request.form['Password']
  track_id = request.form['Tracking Id']
  if track_id:
      return redirect('/trackstatus')
  else:
      return redirect('/customerinfo')




@app.route('/login')
def login():
    abort(401)
    this_is_never_executed()


if __name__ == "__main__":
  import click

  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=8111, type=int)
  def run(debug, threaded, host, port):
    """
    This function handles command line parameters.
    Run the server using:

        python server.py

    Show the help text using:

        python server.py --help

    """

    HOST, PORT = host, port
    print("running on %s:%d" % (HOST, PORT))
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)

  run()
