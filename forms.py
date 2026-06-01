from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, NumberRange, Optional, ValidationError
from models import User, Student


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=80)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=80)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    # Student fields
    student_number = StringField('Student Number', validators=[DataRequired(), Length(max=20)])
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=50)])
    course = SelectField('Course', choices=[
        ('BSCS', 'BS Computer Science'),
        ('BSIT', 'BS Information Technology'),
        ('BSIS', 'BS Information Systems'),
        ('BSCE', 'BS Computer Engineering'),
        ('BSEd', 'BS Education'),
        ('BSBA', 'BS Business Administration'),
        ('BSN', 'BS Nursing'),
        ('BSEE', 'BS Electrical Engineering'),
    ], validators=[DataRequired()])
    year_level = SelectField('Year Level', choices=[(1, '1st Year'), (2, '2nd Year'), (3, '3rd Year'), (4, '4th Year')],
                             coerce=int, validators=[DataRequired()])
    contact_number = StringField('Contact Number', validators=[Optional(), Length(max=20)])
    submit = SubmitField('Register')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already taken.')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    def validate_student_number(self, field):
        if Student.query.filter_by(student_number=field.data).first():
            raise ValidationError('Student number already exists.')


class StudentForm(FlaskForm):
    """Used by admin to add/edit student records."""
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=80)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[Optional(), Length(min=6)])
    student_number = StringField('Student Number', validators=[DataRequired(), Length(max=20)])
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=50)])
    course = SelectField('Course', choices=[
        ('BSCS', 'BS Computer Science'),
        ('BSIT', 'BS Information Technology'),
        ('BSIS', 'BS Information Systems'),
        ('BSCE', 'BS Computer Engineering'),
        ('BSEd', 'BS Education'),
        ('BSBA', 'BS Business Administration'),
        ('BSN', 'BS Nursing'),
        ('BSEE', 'BS Electrical Engineering'),
    ], validators=[DataRequired()])
    year_level = SelectField('Year Level', choices=[(1, '1st Year'), (2, '2nd Year'), (3, '3rd Year'), (4, '4th Year')],
                             coerce=int, validators=[DataRequired()])
    contact_number = StringField('Contact Number', validators=[Optional(), Length(max=20)])
    submit = SubmitField('Save')


class EditProfileForm(FlaskForm):
    """Used by student to edit their own profile."""
    email = StringField('Email', validators=[DataRequired(), Email()])
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=50)])
    course = SelectField('Course', choices=[
        ('BSCS', 'BS Computer Science'),
        ('BSIT', 'BS Information Technology'),
        ('BSIS', 'BS Information Systems'),
        ('BSCE', 'BS Computer Engineering'),
        ('BSEd', 'BS Education'),
        ('BSBA', 'BS Business Administration'),
        ('BSN', 'BS Nursing'),
        ('BSEE', 'BS Electrical Engineering'),
    ], validators=[DataRequired()])
    year_level = SelectField('Year Level', choices=[(1, '1st Year'), (2, '2nd Year'), (3, '3rd Year'), (4, '4th Year')],
                             coerce=int, validators=[DataRequired()])
    contact_number = StringField('Contact Number', validators=[Optional(), Length(max=20)])
    new_password = PasswordField('New Password (leave blank to keep current)', validators=[Optional(), Length(min=6)])
    confirm_password = PasswordField('Confirm New Password', validators=[EqualTo('new_password')])
    submit = SubmitField('Update Profile')
