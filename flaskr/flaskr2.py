# all the imports
import os
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash

app = Flask(__name__)
DATABASE = app.root_path + '\\flaskr.db'
app.config.from_object(__name__)

# from flask import g

# DATABASE = 'database.db'

# def connect_db():
#     return sqlite3.connect(DATABASE)

# @app.before_request
# def before_request():
#     g.db = connect_db()

# @app.teardown_request
# def teardown_request(exception):
#     if hasattr(g, 'db'):
#         g.db.close()

# def get_connection():
#     db = getattr(g, '_db', None)
#     if db is None:
#         db = g._db = connect_db()
#     return db

# app.config.update(dict(    
#     DATABASE=os.path.join(app.root_path, 'flaskr.db'),    
#     DEBUG=True,    
#     SECRET_KEY='development key',    
#     USERNAME='admin',      
#     PASSWORD='admin'
# ))
# app.config.from_envvar('FLASKR_SETTINGS', silent=True)


# def query_db(query, args=(), one=False):
#     cur = g.db.execute(query, args)
#     rv = [dict((cur.description[idx][0], value)
#                for idx, value in enumerate(row)) for row in cur.fetchall()]
#     return (rv[0] if rv else None) if one else rv
 

def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv


@app.cli.command('initdb')
def initdb_command(): 
    init_db()    
    print('Initialized the database.')

def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):        
        g.sqlite_db = connect_db()    
    return g.sqlite_db

@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


# def init_db():
#     with app.app_context():
#         db = get_db()
#         with app.open_resource('schema.sql', mode='r') as f:
#             db.cursor().executescript(f.read())
#         db.commit()



# @app.before_request
# def before_request():
#     g.db.connect()
#     g.user = current_user

# @app.after_request
# def after_request(response):
#     """Close the database connection after each request"""
#     g.db.close()
#     return response

# @login_manager.user_loader
# def load_user(user_id):
#     """user_loader - A decorator to mark the function responsible for loading a user from whatever data source we use."""
#     return User.query.filter(User.id == int(user_id)).first()

# #初始化部分
# def init_db():    
#     db = get_db()    
#     with app.open_resource('schema.sql', mode='r') as f:     
#         db.cursor().executescript(f.read())    
#     db.commit()

#主页部分
# @app.route('/')
# def show_entries():    
#     db = get_db()    
#     cur = db.execute('select title, text from entries order by id desc')    
#     entries = cur.fetchall()    
#     return render_template('show_entries.html',entries=entries)

@app.route('/')
def show_entries():
    cur = g.db.execute('select title, text from entries order by id desc')
    entries = [dict(title=row[0], text=row[1]) for row in cur.fetchall()]
    return render_template('show_entries.html', entries=entries)


#add页面
@app.route('/add', methods=['POST'])
def add_entry():    
    if not session.get('logged_in'):        
        abort(401)    
    db = get_db()    
    db.execute('insert into entries (title, text) values (?, ?)',[request.form['title'], request.form['text']])             
    db.commit()    
    flash('New entry was successfully posted')    
    return redirect(url_for('show_entries'))

#登陆页面
@app.route('/login', methods=['GET', 'POST'])
def login():    
    error = None    
    if request.method == 'POST':        
        if request.form['username'] != app.config['USERNAME']:            
            error = 'Invalid username'        
        elif request.form['password'] != app.config['PASSWORD']:            
            error = 'Invalid password'        
        else:            
            session['logged_in'] = True            
            flash('You were logged in')            
            return redirect(url_for('show_entries'))    
    return render_template('login.html', error=error)

#登出页面
@app.route('/logout')
def logout():    
    session.pop('logged_in', None)    
    flash('You were logged out')    
    return redirect(url_for('show_entries'))

# @app.route('/')
# def show_entries():
#     cur = g.db.execute('select title, text from entries order by id desc')
#     entries = [dict(title=row[0], text=row[1]) for row in cur.fetchall()]
#     return render_template('show_entries.html', entries=entries)

# @app.route('/add', methods=['POST'])
# def add_entry():
#     if not session.get('logged_in'):
#         abort(401)
#     g.db.execute('insert into entries (title, text) values (?, ?)',
#                  [request.form['title'], request.form['text']])
#     g.db.commit()
#     flash('New entry was successfully posted')
#     return redirect(url_for('show_entries'))

# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     error = None
#     if request.method == 'POST':
#         if request.form['username'] != app.config['USERNAME']:
#             error = 'Invalid username'
#         elif request.form['password'] != app.config['PASSWORD']:
#             error = 'Invalid password'
#         else:
#             session['logged_in'] = True
#             flash('You were logged in')
#             return redirect(url_for('show_entries'))
#     return render_template('login.html', error=error)


# @app.route('/logout')
# def logout():
#     session.pop('logged_in', None)
#     flash('You were logged out')
#     return redirect(url_for('show_entries'))
    

if __name__ == '__main__':
    app.run()

