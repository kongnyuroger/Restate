from flask import render_template,request, redirect, url_for, flash, session, send_from_directory
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename
from flask_bcrypt import Bcrypt
import os
from models import User, Property, Image

def registered_routes(app, db):
    bcrypt = Bcrypt(app)
    login_manager = LoginManager(app)
    login_manager.login_view = 'login'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    app.config['UPLOAD_FOLDER'] = 'uploads'

    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    @app.route('/')
    def home():
        return render_template('home.html', )
    
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            name = request.form['name']
            password = request.form['password']
            email = request.form['email']
            is_agent = 'is_agent' in request.form
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
            existing_user = User.query.filter_by(name=name).first()
            if existing_user:
                flash('Username already exists. Please choose a different name.')
                return redirect(request.url)
            user = User(name=name, password=hashed_password, email=email, is_agent= is_agent )
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('home'))
        return render_template('register.html')
    
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            name = request.form['name']
            password = request.form['password']
            user = User.query.filter_by(name=name).first()
            if user and bcrypt.check_password_hash(user.password, password):
                login_user(user)               
                return redirect(url_for('home'))
        return render_template('login.html')
    
    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        return redirect(url_for('login'))

    
    
    @app.route('/upload', methods= ['GET','POST'])
    @login_required
    def upload():
        if request.method == "POST":
            if 'files' not in request.files:
                return redirect(request.url)
        
            name = request.form['name']
            type = request.form['type']
            description = request.form['description']
            price = request.form['price']
            files = request.files.getlist('files')
            user_id = current_user.id
            status = request.form['status']
            location = request.form['location']

            new_property = Property(type=type, description=description, price=price, name = name, status=status, location=location, user_id=user_id )
            db.session.add(new_property)
            db.session.commit()
            for file in files:
                    if file.filename == '':
                        continue
                    if file and allowed_file(file.filename):
                        filename = secure_filename(file.filename)
                        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                        file.save(file_path)

                        new_image = Image(filename=filename, filepath=file_path, property_id=new_property.id)
                        db.session.add(new_image)

            db.session.commit()
            user_id = current_user.id
            user = User.query.get(user_id)
            return render_template('dashboard.html', user = user )
        return render_template('upload.html')
        
    @app.route('/uploads/<filename>')
    def uploaded_file(filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    
    @app.route('/properties')
    def show_properties():
        properties = Property.query.all()
        return render_template('blog.html', properties=properties)
    
    @app.route('/property/<int:property_id>')
    def property_details(property_id):
        property = Property.query.get_or_404(property_id)
        return render_template('property-detail.html', property=property)
    
    @app.route('/add_to_dashboard/<int:property_id>',  methods = ['GET', 'POST'])
    @login_required
    def add_to_dashboard(property_id):
        
        if request.method == "POST":
            user_id = current_user.id
            user = User.query.get(user_id)
            property = Property.query.get(property_id)

            if property not in user.properties:
                user.properties.append(property)
                db.session.commit()

            return redirect(url_for('show_properties'))
        return redirect(url_for('show_properties'))
        
    
    @app.route('/dashboard')
    @login_required
    def dashboard():
       
        status = current_user.is_agent
        user_id = current_user.id
        user = User.query.get(user_id)
        return render_template('dashboard.html', user=user, status = status)
    
            
    @app.route('/search_results')
    def search_results():
        location = request.args.get('location')
        property_type = request.args.get('type')

        query = Property.query

        if location:
            query = query.filter(Property.location.ilike(f'%{location}%'))
        if property_type:
            query = query.filter_by(type=property_type)

        properties = query.all()

        return render_template('search-results.html', properties=properties)
    
    @app.route('/services')
    def services():
        return render_template('services.html')
    
    @app.route('/about')
    def about():
        return render_template('about.html')

