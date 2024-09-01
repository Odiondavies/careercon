from functools import wraps
from flask_mail import Message
from datetime import datetime, timedelta
from flask import render_template, redirect, request, session, flash, url_for, jsonify
from ccapp import app, mail
from ccapp.forms import SignupForm
from ccapp.models import db, Jobseeker, State, Skill, Category, JobseekerSkill, Level, Application, Job, Bookmark, Feedback, Lga
from werkzeug.security import generate_password_hash
from secrets import compare_digest, token_hex


@app.after_request
def add_no_cache_header(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    return response


def get_user_by_id(uid):
    user_details = db.session.query(Jobseeker).get(uid)
    return user_details


def login_required(func):
    @wraps(func)
    def check_login(*args, **kwargs):
        if session.get('useronline') is not None:
            return func(*args, **kwargs)
        else:
            return redirect('/login/')

    return check_login


@login_required
def get_progress(uid):
    if uid.jobseeker_cv and uid.jobseeker_dp and uid.jobseeker_phone and uid.jobseeker_lgaid and uid.dob:
        progress = 100
        color = "text-success"
    elif uid.jobseeker_cv and uid.jobseeker_phone and uid.jobseeker_lgaid and uid.dob:
        progress = 95
        color = "text-warning"
    elif uid.jobseeker_phone and uid.jobseeker_lgaid and uid.dob:
        progress = 80
        color = "text-warning"
    else:
        progress = 70
        color = "text-danger"
    return {"progress": progress, "color": color}


@app.route('/')
def home():
   
    jobs = Job.query.order_by(Job.posted_on.desc()).limit(8).all()
    return render_template('jobseeker/index.html', title="Home", jobs=jobs)


@app.route('/registration/', methods=['GET', 'POST'])
def jobseeker_registration():
    form = SignupForm()
    levels = db.session.query(Level).all()
    categories = db.session.query(Category).all()
    states = db.session.query(State).all()
    
    if request.method == 'POST':
        cat = request.form.get('category')
        user_skill = request.form.get('skill')
        state = request.form.get('state')
        lga = request.form.get('lga')
        firstname = request.form.get('firstname')
        lastname = request.form.get('lastname')
        email = request.form.get('email')
        gender = request.form.get('gender')
        level = request.form.get('level')
        password = request.form.get('password')
        hash_pass = generate_password_hash(password)
        
        userid = db.session.query(Jobseeker).filter(Jobseeker.jobseeker_email == email).first()
        if userid:
            flash("Email is already taken", 'error')
            return redirect(url_for('jobseeker_registration'))
        else:
            jobseeker = Jobseeker(jobseeker_fname=firstname, jobseeker_lname=lastname, jobseeker_password=hash_pass,
                                jobseeker_email=email, jobseeker_gender=gender, jobseeker_levelid=level,
                                jobseeker_stateid=state, jobseeker_categoryid=cat, jobseeker_lgaid=lga)
            db.session.add(jobseeker)
            db.session.commit()
            userid = jobseeker.jobseeker_id
            session['useronline'] = userid
            u_skill = JobseekerSkill(skill_skillid=user_skill, jobseeker_skill_jobseekerid=userid)
            db.session.add(u_skill)
            db.session.commit()
            flash('Info: You need to complete your profile to be able to apply for jobs.', 'info')
            return redirect(url_for('jobseeker_dashboard'))

    return render_template('jobseeker/jobseeker-registration.html', form=form, levels=levels,
                           categories=categories, states=states)
    
    
@app.route('/show_skill/<int:cid>')
def show_skill(cid):
    skills = Skill.query.filter_by(skill_categoryid=cid).all()
    skills_list = [{'skill_id': skill.skill_id, 'skill_name': skill.skill_name} for skill in skills]
    return jsonify(skills_list)


@app.route('/show_lga/<int:lid>')
def show_lga(lid):
    lgas = Lga.query.filter_by(lga_stateid=lid).all()
    lgas_list = [{'lga_id': lga.lga_id, 'lga_name': lga.lga_name} for lga in lgas]
    return jsonify(lgas_list)


@app.route('/jobseeker/dashboard/')
@login_required
def jobseeker_dashboard():
    uid = session.get('useronline')
    userid = get_user_by_id(uid)
    user_progress = get_progress(userid)
    matching_jobs = db.session.query(Job).filter(Job.job_categoryid == userid.jobseeker_categoryid).order_by(Job.posted_on.desc()).limit(6).all()
    jobs = Job.query.order_by(Job.posted_on.desc()).limit(8).all()
    return render_template('jobseeker/jobseeker_dashboard.html', matching_jobs=matching_jobs,
                           jobs=jobs, userid=userid, page='dashboard', title='Dashboard', user_progress=user_progress)


@app.route('/jobseeker/profile-setting/', methods=['GET', 'POST'])
@login_required
def profile_settings():
    uid = session.get('useronline')
    userid = get_user_by_id(uid)

    states = db.session.query(State).all()
    categories = db.session.query(Category).all()
    levels = db.session.query(Level).all()
    skills = Skill.query.filter_by(skill_categoryid=userid.jobseeker_categoryid)
    user_skills = JobseekerSkill.query.filter_by(jobseeker_skill_jobseekerid=userid.jobseeker_id)
    lgas = Lga.query.filter_by(lga_stateid=userid.jobseeker_stateid)

    if request.method == 'GET':
        return render_template('jobseeker/profile_settings.html', userid=userid, categories=categories,
                               levels=levels, states=states, skills=skills, user_skills=user_skills,
                               title='Profile Settings', lgas=lgas)
    else:
        allowed = ['pdf', 'doc', 'docx', 'txt']
        cat = request.form.get('category')
        level = request.form.get('level')
        user_skills = request.form.getlist('skill')
        cv = request.files.get('cv')

        if cat and level and cv:
            file_name = cv.filename
            file_deets = file_name.split('.')
            ext = file_deets[-1]
            if ext in allowed:
                newname = token_hex(8) + '.' + ext
                cv.save('ccapp/static/cv/' + newname)
                userid.jobseeker_categoryid = cat
                userid.jobseeker_levelid = level
                userid.jobseeker_cv = newname

                if user_skills:
                    for skill in user_skills:
                        u_skills = JobseekerSkill(skill_skillid=skill, jobseeker_skill_jobseekerid=userid.jobseeker_id)
                        db.session.add(u_skills)
                db.session.commit()
                flash("Profile was updated successfully.", 'success')
            else:
                flash("Please select a file with an extension pdf, doc, docx or txt.", 'error')

        elif cat and level and userid.jobseeker_cv:
            userid.jobseeker_categoryid = cat
            userid.jobseeker_levelid = level
            if user_skills:
                for skill in user_skills:
                    u_skills = JobseekerSkill(skill_skillid=skill, jobseeker_skill_jobseekerid=userid.jobseeker_id)
                    db.session.add(u_skills)
            db.session.commit()
            flash("Profile was updated successfully.", 'success')

        else:
            flash("Please complete all fields.", 'error')

        return redirect(url_for('profile_settings'))


@app.route('/add-skill/', methods=['POST', 'GET'])
@login_required
def add_skill():
    uid = session.get('useronline')
    userid = get_user_by_id(uid)
    if request.method == 'POST':
        skills = request.form.getlist('skill_id')
        for skill in skills:
            existing_skill = JobseekerSkill.query.filter_by(
                skill_skillid=skill,
                jobseeker_skill_jobseekerid=userid.jobseeker_id
            ).first()

            if not existing_skill:
                user_skill = JobseekerSkill(
                    skill_skillid=skill,
                    jobseeker_skill_jobseekerid=userid.jobseeker_id
                )
                db.session.add(user_skill)
                db.session.commit()
        flash("Your skill list has been updated.")
    return redirect(url_for('profile_settings'))
    
    
@app.route('/jobseeker/personal-information/', methods=['GET', 'POST'])
@login_required
def personal_information():
    uid = session.get('useronline')
    userid = get_user_by_id(uid)

    if request.method == 'POST':
        firstname = request.form.get('firstname')
        lastname = request.form.get('lastname')
        phone = request.form.get('phone')
        state = request.form.get('state')
        dp = request.files.get('photo')
        dob = request.form.get('dob')
        lga = request.form.get('lga')

        if firstname and lastname and phone and state and dp and lga and dob:
            allowed = ['png', 'jpeg', 'jpg']
            file_name = dp.filename
            file_deets = file_name.split('.')
            ext = file_deets[-1]
            if ext in allowed:
                newname = token_hex(16) + '.' + ext
                dp.save('ccapp/static/photos/' + newname)
                userid.jobseeker_fname = firstname
                userid.jobseeker_lname = lastname
                userid.jobseeker_phone = phone
                userid.jobseeker_stateid = state
                userid.jobseeker_lgaid = lga
                userid.dob = dob
                userid.jobseeker_dp = newname
                db.session.commit()
                flash("Your personal information has been updated.", 'success')
            else:
                flash("Please select a photo with an extension png, jpg or jpeg.", 'error')
                
        elif firstname and lastname and phone and state and lga and dob:
            userid.jobseeker_fname = firstname
            userid.jobseeker_lname = lastname
            userid.jobseeker_phone = phone
            userid.jobseeker_stateid = state
            userid.jobseeker_lgaid = lga
            userid.dob = dob
            db.session.commit()
            flash("Your personal information has been updated.", 'success')
       
        else:
            flash("Please complete all filed.", 'error')
        return redirect(url_for('profile_settings'))
    else:
        render_template('jobseeker/profile_settings.html', userid=userid)


@app.route('/jobseeker/settings/', methods=['GET', 'POST'])
@login_required
def account_settings():
    uid = session.get('useronline')
    userid = get_user_by_id(uid)
    if request.method == 'GET':
        return render_template('jobseeker/account_settings.html', userid=userid, title='Account Settings')
    else:
        password = request.form.get('password')
        conf_password = request.form.get('confPassword')
        if password and conf_password:
            if compare_digest(password, conf_password) is True:
                hashed_pwd = generate_password_hash(password)
                userid.jobseeker_password = hashed_pwd
                db.session.commit()
                flash("Your password has been updated.", 'success')
            else:
                flash("Passwords do not match.", 'error')
        else:
            flash("Please complete the password and confirm password filed.", 'error')

        return redirect(url_for('account_settings'))


@app.route('/jobseeker/delete-account/<int:id>/', methods=['POST'])
@login_required
def delete_account(id):
    user = db.session.query(Jobseeker).get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('login'))


@app.route('/jobseeker/bookmarked-jobs/')
@login_required
def bookmarked_jobs():
    uid = session.get('useronline')
    userid = get_user_by_id(uid)
    user_progress = get_progress(userid)
    bkmd_jobs = db.session.query(Bookmark).filter(Bookmark.bookmark_jobseekerid == userid.jobseeker_id).all()
    total_bookmarks = db.session.query(Bookmark).filter(Bookmark.bookmark_jobseekerid == userid.jobseeker_id).count()
    return render_template('jobseeker/bookmark.html', page='bookmark', userid=userid, total_bookmarks=total_bookmarks,
                           bookmarked_jobs=bkmd_jobs, title='My Bookmarks', user_progress=user_progress)


@app.route('/add-bookmark/<int:jobid>/<title>/')
def add_bookmark(jobid, title):
    uid = session.get('useronline')
    userid = get_user_by_id(uid)
    job = Job.query.get_or_404(jobid)
    bkmds = db.session.query(Bookmark).filter(Bookmark.bookmark_jobseekerid == userid.jobseeker_id).all()
    if bkmds:
        for bkmd in bkmds:
            if bkmd.bookmark_jobid != job.job_id:       
                bookmark = Bookmark(bookmark_jobid=job.job_id, bookmark_jobseekerid=userid.jobseeker_id)
                db.session.add(bookmark)
    else:
        bookmark = Bookmark(bookmark_jobid=job.job_id, bookmark_jobseekerid=userid.jobseeker_id)
        db.session.add(bookmark)
    db.session.commit()
    
    if title == 'Dashboard':
        return redirect(url_for('jobseeker_dashboard'))
    elif title == 'My Bookmarks':
        return redirect(url_for('bookmarked_jobs'))
    else:
        return redirect(url_for('job_details', id=job.job_id))


@app.route('/remove-bookmark/<int:jobid>/<title>/')
def remove_bookmark(jobid, title):
    uid = session.get('useronline')
    userid = get_user_by_id(uid)
    job = Job.query.get_or_404(jobid)
    bkmd = Bookmark.query.filter_by(bookmark_jobid=job.job_id).first()
    if bkmd:
        db.session.delete(bkmd)
        db.session.commit()
    
    if title == 'Dashboard':
        return redirect(url_for('jobseeker_dashboard'))
    elif title == 'My Bookmarks':
        return redirect(url_for('bookmarked_jobs'))
    else:
        return redirect(url_for('job_details', id=job.job_id))


@app.route('/jobseeker/applications/')
@login_required
def applications():
    uid = session.get('useronline')
    userid = get_user_by_id(uid)
    user_progress = get_progress(userid)
    feedbacks = db.session.query(Feedback).filter(Feedback.feedback_jobseekerid == userid.jobseeker_id).all()
    total_applications = db.session.query(Application).filter(Application.application_jobseekerid == userid.jobseeker_id).count()
    applica = db.session.query(Application).filter(Application.application_jobseekerid == userid.jobseeker_id).all()
    return render_template('jobseeker/applications.html', page='applications', userid=userid, total_applications=total_applications,
                           applications=applica, title='My Application', feedbacks=feedbacks, user_progress=user_progress)


@app.route('/job-details/<int:id>/')
def job_details(id):
    uid = session.get('useronline')
    userid = get_user_by_id(uid)
    job = Job.query.get_or_404(id)
    qual_list = job.job_qualification.split('*')
    resp_list = job.job_responsibilities.split('*')
    return render_template('jobseeker/job_details.html', userid=userid, title='Job details', job=job, responsibilities=resp_list, qualifications=qual_list)


@app.route('/application-details/<int:id>', methods=['GET', 'POST'])
@login_required
def apply(id):
    uid = session.get('useronline')
    userid = get_user_by_id(uid)
    job = db.session.query(Job).filter(Job.job_id == id).first()
    application = Application.query.filter(Application.application_jobseekerid == userid.jobseeker_id).all()

    if request.method == 'POST':
        cv = userid.jobseeker_cv
        motivation = request.form.get('motivation')
        sign = request.form.get('sign')
        for applic in application:
            if applic.application_jobid == job.job_id:
                flash("You have already applied for this job.", 'error')
                return redirect(url_for('apply', id=job.job_id))

        if cv and motivation and sign:
            app_deets = Application(application_jobseeker_cv=cv, application_jobid=job.job_id,
                                    application_jobseekerid=userid.jobseeker_id,
                                    application_employerid=job.job_employer.employer_id)
            db.session.add(app_deets)
            
            if job.job_employer.employer_company_email:
                email = job.job_employer.employer_company_email
            else:
                email = job.job_employer.employer_email
                
            sender = ('CareerConnnect', f'{userid.jobseeker_email}')
            subject = f"Application by {userid.jobseeker_fname} from CareerConnect."
            msg = Message(subject=subject, sender=sender, recipients=[email])
            msg.body = f"Applicant's motivation\n {motivation}.\n Fullname: {userid.jobseeker_fname}{userid.jobseeker_lname}"
            mail.send(msg)
            
            db.session.commit()
            flash("Your application was submitted successfully", 'success')
            return redirect(url_for('applications'))
        else:
            flash(f"PLease ensure your profile is 90% completed and you have complete this application.", 'error')
        return redirect(url_for('apply', id=job.job_id))

    return render_template('jobseeker/apply.html', userid=userid, title='Application details', job=job)
    

@app.route('/jobseeker/delete-skill/<int:id>/')
@login_required
def delete_skill(id):
    skill = db.session.query(JobseekerSkill).filter(JobseekerSkill.jobseeker_skill_id == id).first()
    db.session.delete(skill)
    db.session.commit()
    flash("Skill has been deleted.", 'success')
    return redirect(url_for('profile_settings'))


@app.route('/jobseeker/logout/')
def jobseeker_logout():
    if session.get('useronline'):
        session.pop('useronline')
        session.clear()
    return redirect(url_for('login'))


@app.route('/search-job/<page>/', methods=['GET', 'POST'])
def search_job(page):
    uid = session.get('useronline')
    userid = get_user_by_id(uid)
    user_progress = get_progress(userid)
    if request.method == 'POST':
        try:
            total_jobs = 0
            keyword = request.form.get('searchInput')
            if keyword:
                found_jobs = Job.query.join(Category).join(Level).join(State).join(Lga).filter(
                    Job.job_title.ilike(f'%{keyword}%') |
                    Job.job_type.ilike(f'%{keyword}%') |
                    Job.job_mode.ilike(f'%{keyword}%') |
                    Category.category_name.ilike(f'%{keyword}%') |
                    State.state_name.ilike(f'%{keyword}%') |
                    Level.level_name.ilike(f'%{keyword}%') |
                    Lga.lga_name.ilike(f'%{keyword}%')
                ).order_by(Job.posted_on).all()
                if found_jobs:
                    for job in found_jobs:
                        total_jobs = total_jobs + 1
        except:
            pass
    if page == 'Home':
        return render_template('utilities/searchresult.html', userid=userid, user_progress=user_progress, jobs=found_jobs, keyword=keyword,
                        total_jobs=total_jobs, title='Search Result')
    else:
        return render_template('jobseeker/search.html', userid=userid, user_progress=user_progress, jobs=found_jobs, keyword=keyword,
                           total_jobs=total_jobs, title='Search Result')

