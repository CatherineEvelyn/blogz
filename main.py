from flask import Flask, request, redirect, render_template, flash, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:beproductive@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key='abc'

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    blog_name = db.Column(db.String(120))
    entry = db.Column(db.String(500))
#why is there owner_id and owner on self.owner, why are they not the same name? Ask CJ!
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, blog_name, entry, owner):
        self.blog_name = blog_name
        self.entry = entry
        self.owner = owner

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120))
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes=['display_login', 'display_signup', 'display_blog', 'index']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')


@app.route('/', methods=['POST', 'GET'])
def index():
    userlist = User.query.all()
    return render_template('index.html',title="blog user!", userlist=userlist)

@app.route('/newpost', methods=['GET', 'POST'])
def display_new_post():

    owner = User.query.filter_by(username=session['username']).first()
    blank_title_error = ''
    blank_body_error = ''
    blog_name = ""
    blog_entry = ''

    if request.method == 'POST':
        blog_name = request.form['blog_title']
        blog_entry = request.form['blog_entry']
        if blog_name == '':
            blank_title_error = "fill in the title"
        if blog_entry == '':
            blank_body_error = "fill in the entry"
        if blog_name and blog_entry != '':
            new_blog = Blog(blog_name, blog_entry, owner)
            db.session.add(new_blog)
            db.session.commit()
            return redirect('/each?blog-id=' + str(new_blog.id))
#or you can use str.format() like this:
#return redirect("/each?blog-id={0}".format(new_blog.id))
        
    return render_template('newpost.html',
        blank_title_error=blank_title_error, blank_body_error=blank_body_error,
        blogtitle=blog_name, blogbody=blog_entry)

@app.route('/blog', methods=['GET', 'POST'])
def display_blog():
    blogs = Blog.query.all()
    y = User.query.all()
    return render_template('blog.html',title="Build A Blog", blogs=blogs, y=y)

@app.route('/each', methods=['GET'])
def display_each():
    blogs = Blog.query.all()
    blog_id = request.args.get('blog-id')
    entry = Blog.query.filter_by(id=blog_id).first()
    written_by = entry.owner_id
    y = User.query.filter_by(id=written_by).first()    
    return render_template('each.html',title="Build A Blog", blogs=blogs, entry=entry, y=y)

@app.route('/singleUser', methods=['GET'])
def blogs_from_singleUser():
    blogs = Blog.query.all()
    user_id = request.args.get('user-id')
    entry = Blog.query.filter_by(owner_id=user_id).all()
    y = User.query.filter_by(id=user_id).first()
    return render_template('singleUser.html',title="Build A Blog", entry=entry, y=y, blogs=blogs)

@app.route('/signup', methods=['POST', 'GET'])
def display_signup():
    error_no_match = ""

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        if password != verify:
            error_no_match = "password doesn't match the verify"

        existing_user = User.query.filter_by(username=username).first()
#if existing user is empty (existing_user is not True or blank)
        if not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')
#        else:
            
        return render_template('signup.html', error_no_match=error_no_match)

    return render_template('signup.html')

@app.route('/login', methods=['POST', 'GET'])
def display_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

#user.password -> password comes from database column name
#the == password, password comes from the input (request.form['password'])
        if user and user.password == password:
            session['username'] = username
            return redirect('/newpost')
        else:
            flash("user doesn't exist or password incorrect", 'error')
    return render_template('login.html')

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')


if __name__ == '__main__':
    app.run()