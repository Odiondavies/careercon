from functools import wraps
from flask_mail import Message
from datetime import datetime, timedelta
from secrets import compare_digest, token_hex
from flask import render_template, redirect, request, session, flash, url_for
from werkzeug.security import generate_password_hash
from ccapp import app
from ccapp import mail
from ccapp.forms import SignupForm
from ccapp.models import db, Employer, State, Job, Application, Level, Category, Feedback, Type


def check_job_validity():
    job = Job.query.get_or_404(id)
    start_date = job.posted_on
    end_date = job.expires_on
    diff = start_date - end_date
    remaining_days = diff.days
    if remaining_days == 0:
        job.job_status = 'Closed'
        db.session.commit()


def get_employer_by_id(uid):
    user_details = Employer.query.get_or_404(uid)
    return user_details


def login_required(func):
    @wraps(func)
    def check_login(*args, **kwargs):
        if session.get('employeronline') is not None:
            return func(*args, **kwargs)
        else:
            return redirect('/login/')
    return check_login


@app.after_request
def add_no_cache_header(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    return response


# employer homepage
@app.route('/employer/')
def employer():
    return render_template('employer/employer.html', title="Employer")


# employer registration
@app.route('/registration-page/', methods=['GET', 'POST'])
def employer_registration():
    states = db.session.query(State).all()
    types = db.session.query(Type).all()
    form = SignupForm()
    if request.method == 'POST':
        firstname = request.form.get('firstname')
        lastname = request.form.get('lastname')
        phone = request.form.get('phone')
        email = request.form.get('email')
        company_name = request.form.get('company_name')
        company_size = request.form.get('company_size')
        company_type = request.form.get('type')
        lga = request.form.get('lga')
        state = request.form.get('state')
        password = request.form.get('password')
        hashed_pwd = generate_password_hash(password)
        
        if firstname and lastname and phone and email and password and company_name and company_size and state and lga and company_type:
            empid = db.session.query(Employer).filter(Employer.employer_email == email).first()
            if empid:
                flash("Email is already taken.", 'error')
                return redirect(url_for('employer_registration'))
            else:
                employer_details = Employer(employer_firstname=firstname, employer_lastname=lastname, employer_phone=phone,
                                        employer_email=email, employer_company_name=company_name, employer_stateid=state,
                                        employer_password=hashed_pwd, employer_company_size=company_size, employer_lgaid=lga,
                                        employer_typeid=company_type)
                db.session.add(employer_details)
                db.session.commit()
                empid = employer_details.employer_id
                session['employeronline'] = empid
                flash('Notice: Please update your company details.', 'info')
                return redirect(url_for('employer_dashboard'))
        else:
            flash("Please complete all fields to continue.", 'error')
    return render_template('employer/registration.html', form=form, states=states, types=types, title="Registration")


# updating employer profile
@app.route('/employer/update/', methods=['GET', 'POST'])
@login_required
def profile_update():
    uid = session.get('employeronline')
    empid = get_employer_by_id(uid)
    if request.method == 'GET':
        return render_template('employer/profile_settings.html', empid=empid, title='Update Profile')
    else:
        firstname = request.form.get('firstname')
        lastname = request.form.get('lastname')
        phone = request.form.get('phone')

        if firstname and lastname and phone:
            empid.employer_firstname = firstname
            empid.employer_lastname = lastname
            empid.employer_phone = phone
            db.session.commit()
            flash("Profile details has been updated.", 'success')
        else:
            flash("Please complete all filed.", 'error')
    return redirect(url_for('profile'))


# employer profile
@app.route('/employer/profile/', methods=['GET', 'POST'])
@login_required
def profile():
    uid = session.get('employeronline')
    empid = get_employer_by_id(uid)
    if request.method == 'GET':
        states = db.session.query(State).all()
        return render_template('employer/profile_settings.html', empid=empid, states=states, title='Profile')
    else:
        desc = request.form.get('desc')
        address = request.form.get('address')
        email = request.form.get('emp_email')
        logo = request.files.get('logo')

        if desc and address and email and logo:
            allowed = ['png', 'jpeg', 'jpg', 'svg', 'webp']
            file_name = logo.filename
            file_deets = file_name.split('.')
            ext = file_deets[-1]
            if ext in allowed:
                newname = token_hex(16) + '.' + ext
                logo.save('ccapp/static/logos/' + newname)

                empid.employer_company_logo = newname
                empid.employer_company_address = address
                empid.employer_company_description = desc
                empid.employer_company_email = email
                db.session.commit()
                flash("Profile details has been updated.", 'success')
            else:
                flash("Please select a logo with an extension png, jpg, svg, or jpeg.", 'error')

        elif desc and address and email and empid.employer_company_logo:
            empid.employer_company_address = address
            empid.employer_company_description = desc
            empid.employer_company_email = email
            db.session.commit()
            flash("Profile details has been updated.", 'success')

        else:
            flash("Please complete all filed.", 'error')

    return redirect(url_for('profile'))


# employer profile settings
@app.route('/employer/settings/', methods=['GET', 'POST'])
@login_required
def settings():
    uid = session.get('employeronline')
    empid = get_employer_by_id(uid)
    if request.method == 'GET':
        states = db.session.query(State).all()
        return render_template('employer/account_settings.html', empid=empid, states=states, title='Settings')
    else:
        password = request.form.get('password')
        conf_password = request.form.get('confPassword')
        if password and conf_password:
            if compare_digest(password, conf_password) is True:
                hashed_pwd = generate_password_hash(password)
                empid.employer_password = hashed_pwd
                db.session.commit()
                flash("Your password has been updated.", 'success')
            else:
                flash("Passwords do not match.", 'error')
        else:
            flash("Please enter fill-out the password and confirm password filed.", 'error')
        return redirect(url_for('settings'))


# employer dashboard
@app.route('/employer/dashboard/')
@login_required
def employer_dashboard():
    eid = session.get('employeronline')
    empid = get_employer_by_id(eid)
    total_jobs = Job.query.filter(Job.job_employerid == empid.employer_id).count()
    total_applications = Application.query.filter(Application.application_employerid == empid.employer_id).count()
    applications = Application.query.filter(Application.application_employerid == empid.employer_id).all()
    jobs = Job.query.filter(Job.job_employerid == empid.employer_id).all()

    successful_applications = 0
    for application in applications:
        if application.application_status == 'Accepted':
            successful_applications = successful_applications + 1

    closed_jobs = 0
    ongoing_jobs = 0
    for job in jobs:
        if job.job_status == 'Available':
            ongoing_jobs = ongoing_jobs + 1
        else:
            closed_jobs = closed_jobs + 1
    return render_template('employer/employer_dashboard.html', empid=empid, title='Dashboard',
                           total_jobs=total_jobs, total_applications=total_applications, closed_jobs=closed_jobs,
                           successful_applications=successful_applications, ongoing_jobs=ongoing_jobs)


# view jobs
@app.route('/employer/view-jobs/', methods=['GET', 'POST'])
@login_required
def view_jobs():
    uid = session.get('employeronline')
    empid = get_employer_by_id(uid)
    jobs = db.session.query(Job).filter(Job.job_employerid == empid.employer_id).all()
    return render_template('employer/view_jobs.html', jobs=jobs, empid=empid, title='View Jobs')


@app.route('/update_status/<int:id>/', methods=['GET', 'POST'])
@login_required
def update_job_status(id):
    job_deets = Job.query.get_or_404(id)
    status = job_deets.job_status
    if status == 'Available':
        job_deets.job_status = 'Closed'
    else:
        job_deets.job_status = 'Available'
    db.session.commit()
    return redirect(url_for('view_jobs'))


# view applications
@app.route('/employer/view-applications/', methods=['GET', 'POST'])
@login_required
def view_applications():
    uid = session.get('employeronline')
    empid = get_employer_by_id(uid)
    applications = db.session.query(Application).filter(Application.application_employerid == empid.employer_id).all()
    return render_template('employer/view_applications.html', applications=applications, empid=empid,
                           title="View Applications")


# add job
@app.route('/employer/add-jobs/', methods=['GET', 'POST'])
@login_required
def addjob():
    curr_date = datetime.now()
    end_date = curr_date + timedelta(days=30)
    uid = session.get('employeronline')
    empid = get_employer_by_id(uid)
    if request.method == 'GET':
        categories = db.session.query(Category).all()
        levels = db.session.query(Level).all()
        states = db.session.query(State).all()
        return render_template('employer/addjob.html', empid=empid, levels=levels, states=states,
                               categories=categories, title='Add Job')
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
        if title and category and level and state and job_mode and job_type and desc and responsibilities and qualification and lga:
            job_qual = '*'.join(qualification)
            job_resp = '*'.join(responsibilities)
            job = Job(job_title=title, job_type=job_type, job_mode=job_mode, job_levelid=level, job_description=desc, expires_on=end_date,
                      job_salary=salary, language=language, job_lgaid=lga, job_responsibilities=job_resp, job_qualification=job_qual,
                      job_employerid=empid.employer_id, job_categoryid=category, job_stateid=state, job_vacancy=vacancy)
              
            db.session.add(job) 
            db.session.commit()
            
            flash("Job has been successfully added.", 'success')
        else:
            flash("Please complete all fields with * to continue.", 'error')
        return redirect('/employer/add-jobs/')


# delete account
@app.route('/employer/delete-account/<int:id>/', methods=['POST'])
@login_required
def delete_employer_account(id):
    empid = get_employer_by_id(id)
    db.session.delete(empid)
    db.session.commit()
    return redirect(url_for('login'))

# view applicants
@app.route('/applicants/<int:id>', methods=['GET', 'POST'])
@login_required
def applicants(id):
    eid = session.get('employeronline')
    empid = get_employer_by_id(eid)
    application_deets = Application.query.filter(Application.application_jobseekerid == id).first()
    if request.method == 'POST':
        status = request.form.get('status')
        feedback = request.form.get('feedback')

        if status and feedback:
            application_deets.application_status = status         
            message = Feedback(content=feedback, feedback_employerid=empid.employer_id, feedback_jobseekerid=application_deets.application_jobseekerid, feedback_applicationid=application_deets.application_id)
            db.session.add(message)
            
            if empid.employer_company_email:
                email = empid.employer_company_email
            else:
                email = empid.employer_email
                
            sender = (f'{empid.employer_company_name}', f'{email}')
            subject = "Your application has been recieved."
            msg = Message(subject=subject, sender=sender, recipients=[application_deets.application_jobseeker.jobseeker_email])
            msg.body = f"{feedback}\n Regareds, {empid.employer_company_name}"
            mail.send(msg)
            
            db.session.commit()
            flash("Application details has been updated successfully.", 'success')
        else:
            flash("Please select a status and give your feedback.", 'error')
    return render_template('employer/applicant.html', title='Applicants Details',
                           application_deets=application_deets)


# logout
@app.route('/employer/logout/')
@login_required
def employer_logout():
    if session.get('employeronline'):
        session.pop('employeronline')
        session.clear()
    return redirect(url_for('login'))
