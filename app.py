import os
from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from functools import wraps
from dotenv import load_dotenv

from models import db, User, Student
from forms import LoginForm, RegistrationForm, StudentForm, EditProfileForm

load_dotenv()

app = Flask(__name__)

# ── Configuration ──────────────────────────────────────────────────────────────
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
    'DATABASE_URL',
    'mysql+pymysql://root@localhost/enrollment_db'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# ── Extensions ─────────────────────────────────────────────────────────────────
db.init_app(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'warning'


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


# ── Decorators ─────────────────────────────────────────────────────────────────
def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash('Access denied. Admins only.', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated


# ── Auth Routes ────────────────────────────────────────────────────────────────
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash(f'Welcome back, {user.username}!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard'))
        flash('Invalid username or password.', 'danger')
    return render_template('login.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data, role='student')
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.flush()  # get user.id before committing

        student = Student(
            user_id=user.id,
            student_number=form.student_number.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            course=form.course.data,
            year_level=form.year_level.data,
            contact_number=form.contact_number.data or None,
        )
        db.session.add(student)
        db.session.commit()
        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))


# ── Dashboard ──────────────────────────────────────────────────────────────────
@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.is_admin():
        total_students = Student.query.count()
        recent_students = Student.query.order_by(Student.id.desc()).limit(5).all()
        return render_template('dashboard.html', total_students=total_students, recent_students=recent_students)
    else:
        student = Student.query.filter_by(user_id=current_user.id).first()
        return render_template('dashboard.html', student=student)


# ── Admin: Students CRUD ───────────────────────────────────────────────────────
@app.route('/students')
@login_required
@admin_required
def students():
    search = request.args.get('search', '').strip()
    query = Student.query.join(User)
    if search:
        query = query.filter(
            db.or_(
                Student.first_name.ilike(f'%{search}%'),
                Student.last_name.ilike(f'%{search}%'),
                Student.student_number.ilike(f'%{search}%'),
            )
        )
    all_students = query.order_by(Student.last_name).all()
    return render_template('students.html', students=all_students, search=search)


@app.route('/students/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_student():
    form = StudentForm()
    if form.validate_on_submit():
        # Validate uniqueness manually (StudentForm doesn't inherit RegistrationForm validators)
        if User.query.filter_by(username=form.username.data).first():
            flash('Username already taken.', 'danger')
            return render_template('add_student.html', form=form)
        if User.query.filter_by(email=form.email.data).first():
            flash('Email already registered.', 'danger')
            return render_template('add_student.html', form=form)
        if Student.query.filter_by(student_number=form.student_number.data).first():
            flash('Student number already exists.', 'danger')
            return render_template('add_student.html', form=form)
        if not form.password.data:
            flash('Password is required when creating a new student.', 'danger')
            return render_template('add_student.html', form=form)

        user = User(username=form.username.data, email=form.email.data, role='student')
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.flush()

        student = Student(
            user_id=user.id,
            student_number=form.student_number.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            course=form.course.data,
            year_level=form.year_level.data,
            contact_number=form.contact_number.data or None,
        )
        db.session.add(student)
        db.session.commit()
        flash(f'Student {student.full_name} added successfully.', 'success')
        return redirect(url_for('students'))
    return render_template('add_student.html', form=form)


@app.route('/students/edit/<int:student_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_student(student_id):
    student = db.get_or_404(Student, student_id)
    form = StudentForm()

    if request.method == 'GET':
        # Pre-populate all fields manually to avoid obj= mapping wrong model
        form.username.data = student.user.username
        form.email.data = student.user.email
        form.student_number.data = student.student_number
        form.first_name.data = student.first_name
        form.last_name.data = student.last_name
        form.course.data = student.course
        form.year_level.data = student.year_level
        form.contact_number.data = student.contact_number

    if form.validate_on_submit():
        # Check username uniqueness (excluding current user)
        existing = User.query.filter_by(username=form.username.data).first()
        if existing and existing.id != student.user_id:
            flash('Username already taken.', 'danger')
            return render_template('edit_student.html', form=form, student=student)

        existing = User.query.filter_by(email=form.email.data).first()
        if existing and existing.id != student.user_id:
            flash('Email already registered.', 'danger')
            return render_template('edit_student.html', form=form, student=student)

        existing = Student.query.filter_by(student_number=form.student_number.data).first()
        if existing and existing.id != student.id:
            flash('Student number already exists.', 'danger')
            return render_template('edit_student.html', form=form, student=student)

        student.user.username = form.username.data
        student.user.email = form.email.data
        if form.password.data:
            student.user.set_password(form.password.data)

        student.student_number = form.student_number.data
        student.first_name = form.first_name.data
        student.last_name = form.last_name.data
        student.course = form.course.data
        student.year_level = form.year_level.data
        student.contact_number = form.contact_number.data or None

        db.session.commit()
        flash(f'Student {student.full_name} updated successfully.', 'success')
        return redirect(url_for('students'))
    return render_template('edit_student.html', form=form, student=student)


@app.route('/students/delete/<int:student_id>', methods=['POST'])
@login_required
@admin_required
def delete_student(student_id):
    student = db.get_or_404(Student, student_id)
    name = student.full_name
    user = student.user
    db.session.delete(user)   # cascade deletes student
    db.session.commit()
    flash(f'Student {name} deleted successfully.', 'success')
    return redirect(url_for('students'))


# ── Student: Profile ───────────────────────────────────────────────────────────
@app.route('/profile')
@login_required
def profile():
    if current_user.is_admin():
        flash('Admins do not have a student profile.', 'info')
        return redirect(url_for('dashboard'))
    student = Student.query.filter_by(user_id=current_user.id).first_or_404()
    return render_template('profile.html', student=student)


@app.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if current_user.is_admin():
        return redirect(url_for('dashboard'))
    student = Student.query.filter_by(user_id=current_user.id).first_or_404()
    form = EditProfileForm(obj=student)

    if request.method == 'GET':
        form.email.data = current_user.email

    if form.validate_on_submit():
        existing = User.query.filter_by(email=form.email.data).first()
        if existing and existing.id != current_user.id:
            flash('Email already in use.', 'danger')
            return render_template('edit_profile.html', form=form, student=student)

        current_user.email = form.email.data
        if form.new_password.data:
            current_user.set_password(form.new_password.data)

        student.first_name = form.first_name.data
        student.last_name = form.last_name.data
        student.course = form.course.data
        student.year_level = form.year_level.data
        student.contact_number = form.contact_number.data or None

        db.session.commit()
        flash('Profile updated successfully.', 'success')
        return redirect(url_for('profile'))
    return render_template('edit_profile.html', form=form, student=student)


# ── DB init helper ─────────────────────────────────────────────────────────────
@app.cli.command('init-db')
def init_db():
    """Create all tables and seed an admin account."""
    db.create_all()
    if not User.query.filter_by(role='admin').first():
        admin = User(username='admin', email='admin@school.edu', role='admin')
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print('Admin user created  →  username: admin  |  password: admin123')
    else:
        print('Tables already exist.')


if __name__ == '__main__':
    app.run(debug=True)
