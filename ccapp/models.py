from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class Jobseeker(db.Model):
    __tablename__ = 'jobseekers'
    jobseeker_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    jobseeker_fname = db.Column(db.String(100), nullable=False)
    jobseeker_lname = db.Column(db.String(100), nullable=False)
    jobseeker_email = db.Column(db.String(200), nullable=False, unique=True)
    jobseeker_gender = db.Column(db.Enum('Male', 'Female'), nullable=False)
    jobseeker_password = db.Column(db.String(255), nullable=False)
    jobseeker_phone = db.Column(db.String(15))
    jobseeker_cv = db.Column(db.Text)
    jobseeker_dp = db.Column(db.Text)
    date_registered = db.Column(db.DateTime, default=datetime.now())
    dob = db.Column(db.Date)
    date_updated = db.Column(db.DateTime, default=datetime.now(), onupdate=datetime.now())

    # Setting foreign key
    jobseeker_levelid = db.Column(db.Integer, db.ForeignKey('level.level_id'), nullable=True)
    jobseeker_stateid = db.Column(db.Integer, db.ForeignKey('state.state_id'))
    jobseeker_lgaid = db.Column(db.Integer, db.ForeignKey('lga.lga_id'))
    jobseeker_categoryid = db.Column(db.Integer, db.ForeignKey('category.category_id'), nullable=True)

    # Setting relationships
    jobseeker_state = db.relationship("State", back_populates="state_jobseeker")
    jobseeker_application = db.relationship("Application", back_populates="application_jobseeker")
    jobseeker_bookmark = db.relationship("Bookmark", back_populates="bookmark_jobseeker")
    jobseeker_jobseekerskills = db.relationship("JobseekerSkill", back_populates="jobseekerskills_jobseeker")
    jobseeker_level = db.relationship("Level", back_populates="level_jobseeker")
    jobseeker_category = db.relationship("Category", back_populates="category_jobseeker")
    jobseeker_feedback = db.relationship("Feedback", back_populates="feedback_jobseeker")
    jobseeker_lga = db.relationship("Lga", back_populates="lga_jobseeker")


class Admin(db.Model):
    admin_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    admin_firstname = db.Column(db.String(100), nullable=False)
    admin_lastname = db.Column(db.String(100), nullable=False)
    admin_email = db.Column(db.String(200), nullable=False, unique=True)
    admin_password = db.Column(db.String(255), nullable=False)
    last_loggedin = db.Column(db.DateTime, default=datetime.now())
    date_updated = db.Column(db.DateTime, default=datetime.now(), onupdate=datetime.now())


class Employer(db.Model):
    __tablename__ = 'employers'
    employer_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    employer_firstname = db.Column(db.String(200), nullable=False)
    employer_lastname = db.Column(db.String(200), nullable=False)
    employer_email = db.Column(db.String(200), nullable=False, unique=True)
    employer_password = db.Column(db.String(255), nullable=False)
    employer_phone = db.Column(db.String(15), nullable=False)

    employer_company_name = db.Column(db.String(255), nullable=False)
    employer_company_size = db.Column(db.String(200), nullable=False)
    employer_company_address = db.Column(db.Text)
    employer_company_description = db.Column(db.Text)
    employer_company_logo = db.Column(db.Text)
    employer_company_email = db.Column(db.String(255), unique=True)
    date_registered = db.Column(db.DateTime, default=datetime.now())
    date_updated = db.Column(db.DateTime, default=datetime.now(), onupdate=datetime.now())

    # Setting foreign key
    employer_stateid = db.Column(db.Integer, db.ForeignKey('state.state_id'))
    employer_lgaid = db.Column(db.Integer, db.ForeignKey('lga.lga_id'))
    employer_typeid = db.Column(db.Integer, db.ForeignKey('type.type_id'))

    # Setting relationships
    employer_state = db.relationship("State", back_populates="state_employer")
    employer_lga = db.relationship("Lga", back_populates="lga_employer")
    employer_type = db.relationship("Type", back_populates="type_employer")
    employer_job = db.relationship("Job", back_populates="job_employer")
    employer_feedback = db.relationship("Feedback", back_populates="feedback_employer")
    employer_application = db.relationship("Application", back_populates="application_employer")


class State(db.Model):
    state_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    state_name = db.Column(db.String(100), nullable=False)

    # Setting relationships
    state_jobseeker = db.relationship("Jobseeker", back_populates="jobseeker_state")
    state_employer = db.relationship("Employer", back_populates="employer_state")
    state_job = db.relationship("Job", back_populates="job_state")
    state_lga = db.relationship("Lga", back_populates="lga_state")


class Lga(db.Model):
    lga_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    lga_name = db.Column(db.String(100), nullable=False)

    # setting foreign keys
    lga_stateid = db.Column(db.Integer, db.ForeignKey('state.state_id'))

    # setting relationships
    lga_state = db.relationship("State", back_populates="state_lga")
    lga_job = db.relationship("Job", back_populates="job_lga")
    lga_jobseeker = db.relationship("Jobseeker", back_populates="jobseeker_lga")
    lga_employer = db.relationship("Employer", back_populates="employer_lga")


class Level(db.Model):
    level_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    level_name = db.Column(db.String(255), nullable=False)

    # Setting relationships
    level_job = db.relationship("Job", back_populates="job_level")
    level_jobseeker = db.relationship("Jobseeker", back_populates="jobseeker_level")


# Profession categories
class Category(db.Model):
    category_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    category_name = db.Column(db.String(255), nullable=False)

    # Setting relationships
    category_skill = db.relationship("Skill", back_populates="skill_category")
    category_job = db.relationship("Job", back_populates="job_category")
    category_jobseeker = db.relationship("Jobseeker", back_populates="jobseeker_category")
    

# Company categories
class Type(db.Model):
    type_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    type_name = db.Column(db.String(255), nullable=False)

    # Setting relationships
    type_employer = db.relationship("Employer", back_populates="employer_type")


class Skill(db.Model):
    __tablename__ = 'skills'
    skill_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    skill_name = db.Column(db.String(255), nullable=False)

    # Setting foreign key
    skill_categoryid = db.Column(db.Integer, db.ForeignKey('category.category_id'))

    # Setting relationships
    skill_category = db.relationship("Category", back_populates="category_skill")
    skill_jobseekerskills = db.relationship("JobseekerSkill", back_populates="jobseekerskills_skill")


class JobseekerSkill(db.Model):
    __tablename__ = 'jobseekerskills'
    jobseeker_skill_id = db.Column(db.Integer, autoincrement=True, primary_key=True)

    # Setting foreign key
    skill_skillid = db.Column(db.Integer, db.ForeignKey('skills.skill_id'))
    jobseeker_skill_jobseekerid = db.Column(db.Integer, db.ForeignKey('jobseekers.jobseeker_id'))

    # Setting relationships
    jobseekerskills_skill = db.relationship("Skill", back_populates="skill_jobseekerskills")
    jobseekerskills_jobseeker = db.relationship("Jobseeker", back_populates="jobseeker_jobseekerskills")


class Bookmark(db.Model):
    bookmark_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    date_bookmarked = db.Column(db.DateTime, default=datetime.now())

    # Setting foreign key
    bookmark_jobid = db.Column(db.Integer, db.ForeignKey('jobs.job_id'))
    bookmark_jobseekerid = db.Column(db.Integer, db.ForeignKey('jobseekers.jobseeker_id'))

    # Setting relationships
    bookmark_jobseeker = db.relationship("Jobseeker", back_populates="jobseeker_bookmark")
    bookmark_job = db.relationship("Job", back_populates="job_bookmark")


class Application(db.Model):
    application_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    applied_on = db.Column(db.DateTime, default=datetime.now())
    application_jobseeker_cv = db.Column(db.String(255), nullable=False)
    application_status = db.Column(db.Enum('Pending', 'Accepted', 'Declined'), server_default='Pending')

    # Setting foreign key
    application_jobid = db.Column(db.Integer, db.ForeignKey('jobs.job_id'))
    application_jobseekerid = db.Column(db.Integer, db.ForeignKey('jobseekers.jobseeker_id'))
    application_employerid = db.Column(db.Integer, db.ForeignKey('employers.employer_id'))

    # Setting relationships
    application_jobseeker = db.relationship("Jobseeker", back_populates="jobseeker_application")
    application_job = db.relationship("Job", back_populates="job_application")
    application_feedback = db.relationship("Feedback", back_populates="feedback_application")
    application_employer = db.relationship("Employer", back_populates="employer_application")


class Job(db.Model):
    __tablename__ = 'jobs'
    job_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    job_title = db.Column(db.String(255), nullable=False)
    job_type = db.Column(db.String(25), nullable=False)
    job_mode = db.Column(db.String(25), nullable=False)
    job_description = db.Column(db.Text, nullable=False)
    job_responsibilities = db.Column(db.Text, nullable=True)
    job_qualification = db.Column(db.Text, nullable=True)
    job_vacancy = db.Column(db.String(15), nullable=True)
    language = db.Column(db.String(200))
    job_salary = db.Column(db.String(150))
    job_status = db.Column(db.Enum('Available', 'Closed'), server_default='Available')
    posted_on = db.Column(db.DateTime, default=datetime.now())
    expires_on = db.Column(db.DateTime)

    # Setting foreign key
    job_employerid = db.Column(db.Integer, db.ForeignKey('employers.employer_id'), nullable=True)
    job_categoryid = db.Column(db.Integer, db.ForeignKey('category.category_id'))
    job_stateid = db.Column(db.Integer, db.ForeignKey('state.state_id'))
    job_levelid = db.Column(db.Integer, db.ForeignKey('level.level_id'))
    job_lgaid = db.Column(db.Integer, db.ForeignKey('lga.lga_id'))

    # Setting relationships
    job_employer = db.relationship("Employer", back_populates="employer_job")
    job_level = db.relationship("Level", back_populates="level_job")
    job_category = db.relationship("Category", back_populates="category_job")
    job_state = db.relationship("State", back_populates="state_job")
    job_lga = db.relationship("Lga", back_populates="lga_job")
    job_bookmark = db.relationship("Bookmark", back_populates="bookmark_job")
    job_application = db.relationship("Application", back_populates="application_job")


class Feedback(db.Model):
    feedback_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    content = db.Column(db.Text, nullable=False)
    sent_on = db.Column(db.DateTime, default=datetime.now())

    # setting foreign key
    feedback_employerid = db.Column(db.Integer, db.ForeignKey('employers.employer_id'), nullable=True)
    feedback_jobseekerid = db.Column(db.Integer, db.ForeignKey('jobseekers.jobseeker_id'), nullable=True)
    feedback_applicationid = db.Column(db.Integer, db.ForeignKey('application.application_id'), nullable=True)

    # Setting relationships
    feedback_employer = db.relationship("Employer", back_populates="employer_feedback")
    feedback_jobseeker = db.relationship("Jobseeker", back_populates="jobseeker_feedback")
    feedback_application = db.relationship("Application", back_populates="application_feedback")
