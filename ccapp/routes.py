from functools import wraps
import os
from flask_mail import Message
from datetime import datetime, timedelta
from secrets import compare_digest
from flask import render_template, redirect, request, session, flash, url_for
from ccapp import app, mail
from ccapp.forms import LoginForm
from ccapp.models import db, Employer, Jobseeker, Admin, Job, Category, Level, State, Application
from werkzeug.security import check_password_hash, generate_password_hash
from secrets import token_hex



def get_admin_by_id(uid):
    user_details = db.session.query(Admin).get(uid)
    return user_details


def login_required(func):
    @wraps(func)
    def check_login(*args, **kwargs):
        if session.get('adminonline'):
            return func(*args, **kwargs)
        else:
            return redirect('/admin/login/')

    return check_login


@app.after_request
def add_no_cache_header(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    return response


# Login for other users
@app.route('/login/', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if email and password:
            jobseeker = db.session.query(Jobseeker).filter(Jobseeker.jobseeker_email == email).first()
            employer = db.session.query(Employer).filter(Employer.employer_email == email).first()
            if jobseeker is not None:
                pw_hashed = jobseeker.jobseeker_password
                chk_pwd = check_password_hash(pw_hashed, password)
                if chk_pwd is True:
                    session['useronline'] = jobseeker.jobseeker_id
                    return redirect(url_for('jobseeker_dashboard'))
                else:
                    flash("Invalid Password", "error")
            elif employer is not None:
                pw_hashed = employer.employer_password
                chk_pwd = check_password_hash(pw_hashed, password)
                if chk_pwd is True:
                    session['employeronline'] = employer.employer_id
                    return redirect(url_for('employer_dashboard'))
                else:
                    flash("Invalid Password", "error")
            else:
                flash("Invalid Username", "error")
                return redirect('/login/')
        else:
            flash("Email and password are required.", category='error')

    return render_template('utilities/login.html', title="Login", form=form)


@app.route('/admin/dashboard/', methods=['GET', 'POST'])
@login_required
def admin_dashboard():
    aid = session.get('adminonline')
    adminid = get_admin_by_id(aid)
    total_jobs = Job.query.count()
    total_employers = Employer.query.count()
    total_jobseekers = Jobseeker.query.count()
    total_categories = Category.query.count()
    total_applications = Application.query.count()
    return render_template("admin/dashboard.html", title='Dashboard', total_jobs=total_jobs, total_employers=total_employers, adminid=adminid,
                        total_jobseekers=total_jobseekers, total_categories=total_categories,total_applications=total_applications)


@app.route('/admin/jobseekers/')
@login_required
def jobseekers():
    aid = session.get('adminonline')
    adminid = get_admin_by_id(aid)
    jobseekers = db.session.query(Jobseeker).all()
    return render_template("admin/jobseekers.html", jobseekers=jobseekers, title="Jobseekers", adminid=adminid)


@app.route('/admin/employers/')
@login_required
def employers():
    aid = session.get('adminonline')
    adminid = get_admin_by_id(aid)
    employers = db.session.query(Employer).all()
    return render_template("admin/employers.html", employers=employers, title='Employers', adminid=adminid)


@app.route('/admin/jobs/')
@login_required
def jobs():
    aid = session.get('adminonline')
    adminid = get_admin_by_id(aid)
    jobs = db.session.query(Job).all()
    return render_template('admin/jobs.html', jobs=jobs, title="Jobs", adminid=adminid)


@app.route('/admin/add-job/', methods=['GET', 'POST'])
@login_required
def add_job():
    aid = session.get('adminonline')
    adminid = get_admin_by_id(aid)
    if request.method == 'GET':
        curr_date = datetime.now()
        end_date = curr_date + timedelta(days=30)
        categories = db.session.query(Category).all()
        levels = db.session.query(Level).all()
        states = db.session.query(State).all()
        employers = db.session.query(Employer).all()
        return render_template('admin/addjob.html', title="Add Job", categories=categories,
                               levels=levels, states=states, employers=employers, adminid=adminid)
    else:
        title = request.form.get('title')
        job_type = request.form.get('job_type')
        job_mode = request.form.get('job_mode')
        level = request.form.get('level')
        desc = request.form.get('description')
        responsibilities = request.form.getlist('responsibilities')
        qualification = request.form.getlist('qualification')
        salary = request.form.get('salary')
        category = request.form.get('category')
        state = request.form.get('state')
        lga = request.form.get('lga')
        vacancy = request.form.get('vacancy')
        language = request.form.get('language')
        employer = request.form.get('employer')

        if title and category and level and state and job_mode and job_type and desc and responsibilities and qualification and lga:
            job_qual = '*'.join(qualification)
            job_resp = '*'.join(responsibilities)
            job = Job(job_title=title, job_type=job_type, job_mode=job_mode, job_levelid=level, job_description=desc, expires_on=end_date,
                      job_salary=salary, language=language, job_lgaid=lga, job_responsibilities=job_resp, job_qualification=job_qual,
                      job_employerid=employer, job_categoryid=category, job_stateid=state, job_vacancy=vacancy)
              
            db.session.add(job) 
            db.session.commit()
            flash("Job has been successfully added.", 'success')
        else:
            flash("Please complete all fields with * to continue.", 'error')
        return redirect(url_for('add_job'))


@app.route('/job_status/<int:id>/', methods=['GET', 'POST'])
@login_required
def job_status(id):
    job_deets = Job.query.get_or_404(id)
    status = job_deets.job_status
    if status == 'Available':
        job_deets.job_status = 'Closed'
    else:
        job_deets.job_status = 'Available'
    db.session.commit()
    return redirect(url_for('jobs'))


@app.route('/admin/delete-employer/<int:id>/')
@login_required
def delete_employer(id):
    employer = db.session.query(Employer).get_or_404(id)
    actual_logo = employer.employer_company_logo
    db.session.delete(employer)
    db.session.commit()

    # Delete the file from the folder
    os.remove(f"ccapp/static/logos/{actual_logo}")

    flash("Employer deleted successfully.", 'success')
    return redirect(url_for('employers'))


@app.route('/delete/jobseeker/<int:id>/')
@login_required
def delete_jobseeker(id):
    jobseeker = db.session.query(Jobseeker).get_or_404(id)
    db.session.delete(jobseeker)
    db.session.commit()

    flash("Jobseeker deleted successfully.", 'success')
    return redirect(url_for('jobseekers'))


@app.route('/admin/delete-job/<int:id>/')
@login_required
def delete_job(id):
    job = db.session.query(Job).get_or_404(id)
    db.session.delete(job)
    db.session.commit()

    flash("Job deleted successfully.", 'success')
    return redirect(url_for('jobs'))


@app.route('/admin/logout/')
def admin_logout():
    if session.get('adminonline'):
        session.pop('adminonline')
        session.clear()
    return redirect(url_for('admin_login'))


@app.route('/admin-profile/', methods=['GET', 'POST'])
@login_required
def admin_profile():
    aid = session.get('adminonline')
    adminid = get_admin_by_id(aid)
    
    if request.method == 'POST':
        firstname = request.form.get('firstname')
        lastname = request.form.get('lastname')
        if firstname and lastname:
            adminid.admin_firstname = firstname
            adminid.admin_lastname = lastname
            db.session.commit()
            flash("Your profile has been updated.", 'successs')
        else:
            flash("Please enter your firstname and lastname.", 'error')
    return render_template('admin/profile.html', title="Profile Setting", adminid=adminid)


@app.route('/admin-settings/', methods=['GET', 'POST'])
@login_required
def admin_settings():
    aid = session.get('adminonline')
    adminid = get_admin_by_id(aid)
    if request.method == 'POST':
        password = request.form.get('password')
        confPassword = request.form.get('confPassword')
        if password and confPassword:
            if compare_digest(password, confPassword) is True:
                hashed_pwd = generate_password_hash(password)

                adminid.admin_password = hashed_pwd
                db.session.commit()
                flash("Your password has been updated.", 'success')
            else:
                flash("Passwords do not match", 'error')
        else:
            flash("Please complete both password fields.", 'error')
        return redirect(url_for('admin_settings'))
    return render_template('admin/settings.html', title="Account Settings", adminid=adminid)


@app.errorhandler(404)
def error404_handler(error):
    form = LoginForm()
    return render_template('utilities/error404.html', error=error, form=form), 404


# Admin login
@app.route('/admin/login/', methods=['GET', 'POST'])
def admin_login():
    form = LoginForm()
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if email and password:
            admin = db.session.query(Admin).filter(Admin.admin_email == email).first()
            if admin:
                pw_hashed = admin.admin_password
                chk_pwd = check_password_hash(pw_hashed, password)
                if chk_pwd is True:
                    session['adminonline'] = admin.admin_id
                    admin.last_loggedin = datetime.now()
                    db.session.commit()
                    return redirect(url_for('admin_dashboard'))
                else:
                    flash("Invalid Password", "error")
            else:
                flash("Invalid Username", "error")
                return redirect(url_for('admin_login'))
        else:
            flash("Email and password are required.", category='error')

    return render_template('admin/login.html', title="Login", form=form)


@app.route('/show/cv/<cv_file>')
def show_cv(cv_file):
    cv_file = f'/static/cv/{cv_file}'
    return redirect(cv_file)


@app.route('/forgot-password/', methods=['POST'])
def forgot_password():
    reg_email = request.form.get('regEmail')
    if reg_email:
        jobseeker = db.session.query(Jobseeker).filter(Jobseeker.jobseeker_email == reg_email).first()
        employer = db.session.query(Employer).filter(Employer.employer_email == reg_email).first()
        if jobseeker is not None:
            new_pwd = token_hex(10)
            hash_pwd = generate_password_hash(new_pwd)
            jobseeker.jobseeker_password = hash_pwd
            sender = ('CareerConnnect Web Team')
            subject = "Recovery Password."
            msg = Message(subject=subject, sender=sender, recipients=[reg_email])
            msg.body = f"Your recovery password is {new_pwd}, please login to your dashboard and change the password.\nRegards! CareerConnect Web Team."
            mail.send(msg)
            db.session.commit()
            flash("Your recovery password has been sent toy your email.", 'success')
        elif employer is not None:
            new_pwd = token_hex(10)
            hash_pwd = generate_password_hash(new_pwd)
            employer.employer_email = hash_pwd
            sender = ('CareerConnnect Web Team')
            subject = "Recovery Password."
            msg = Message(subject=subject, sender=sender, recipients=[reg_email])
            msg.body = f"Your recovery password is {new_pwd}, please login to your dashboard and change the password.\nRegards! CareerConnect Web Team."
            mail.send(msg)
            db.session.commit()
            flash("Your recovery password has been sent toy your email.", 'success')
        return redirect(url_for('login'))
    else:
        flash("Please provide your registered email.", 'error')
    return redirect(url_for('login'))