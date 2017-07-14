from flask import Flask, request, redirect, render_template, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:beproductive@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key='abc'

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    blog_name = db.Column(db.String(120))
    entry = db.Column(db.String(500))

    def __init__(self, blog_name, entry):
        self.blog_name = blog_name
        self.entry = entry


@app.route('/', methods=['POST', 'GET'])
def index():
    blogs = Blog.query.all()
    return render_template('blog.html',title="Build A Blog", blogs=blogs)

@app.route('/newpost', methods=['GET', 'POST'])
def display_new_post():
    if request.method == 'POST':
        blog_name = request.form['blog_title']
        blog_entry = request.form['blog_entry']

        if blog_name and blog_entry != '':
            new_blog = Blog(blog_name, blog_entry)
            db.session.add(new_blog)
            db.session.commit()
            return redirect('/')
        else:
            flash("Please fill in the form", 'error')
        
    return render_template('newpost.html')

@app.route('/blog', methods=['GET', 'POST'])
def display_blog():
    blogs = Blog.query.all()
    return render_template('blog.html',title="Build A Blog", blogs=blogs)

@app.route('/each', methods=['GET'])
def display_each():
    blogs = Blog.query.all()
    
    if 'blog-id' in request.args:
        blog_id = request.args.get('blog-id')
        y = Blog.query.get(blog_id)
        return render_template('each.html', y=y)
        
    return render_template('each.html',title="Build A Blog", blogs=blogs)

if __name__ == '__main__':
    app.run()