import io
import os
import json
import uuid
import base64
import glob

import logging
from logging.config import dictConfig
from logging import INFO
from datetime import datetime, timedelta
from pathlib import Path


from flask import Flask, session, g,     redirect, url_for, render_template, request, send_file, send_from_directory, request, flash 
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from flask.templating import render_template
#from flask_mail import message


from imp_calc import app
from imp_calc.forms import RegisterForm, LoginForm, ResetPasswordForm, ResetPasswordRequestForm, ChangePasswordForm
from imp_calc.models import User
from imp_calc import db, mail, s
from imp_calc.email import send_password_reset_email

import RS_creator
import RS_creator_acyclo
import area_norm
import imp_vs_imp
import assay
import L_cysteine
# from imp_calc import app
# from flask import Flask, render_template, url_for,redirect, flash, request
# from imp_calc.forms import RegisterForm, LoginForm
# from imp_calc.models import User
# from imp_calc import db
# from flask_login import login_user, logout_user, login_required
# import os

# DEBUG: Detailed information, typically of interest only when diagnosing problems.

# info: Confirmation that things are working as expected.

# WARNING: An indication that something unexpected happened, or indicative of some problem in the near future (e.g. ‘disk space low’). The software is still working as expected.

# ERROR: Due to a more serious problem, the software has not been able to perform some function.

# CRITICAL: A serious error, indicating that the program itself may be unable to continue running.


#log = logging.getLogger('werkzeug') #These two lines is to keep aside the unwanted get and post request manipulations that comes
#log.disabled=True # This one works with the above live to prevent get/Post request to coming in the logs 
#logging.basicConfig(filename='example.log', level=logging.info,format='%(asctime)s:%(levelname)s:%(message)s')  
# logging.basicConfig(filename='log/flask_server.log' ,level=logging.info)
# formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
# handler = logging.FileHandler(filename='log/flask_server.log')
# handler.setFormatter(formatter)
# logger = logging.getLogger()
# logger.setLevel(logging.info)
# logger.addHandler(handler)

# file_handler = FileHandler('errorlog.txt')
# file_handler.setLevel(info)
# logger = logging.getLogger()
# app.logger.addHandler(file_handler)   

## Approach given by stack overflow Question## i.e. dict config approach
'''
dictConfig({
    'version': 1,
    'loggers': {
        # root logger
        '': {
            'level': 'INFO',
            'handlers': ['console_handler'],
        },
        'imp_calc': {
            'level': 'INFO',
            'handlers': ['console_handler', 'file_handler'],
            'propagate': False,
        },
        # this logger will write logs into file
        'debug': {
            'level': 'INFO',
            'handlers': ['console_handler', 'file_handler'],
            'propagate': False,
        },
    },
    'handlers': {
        'console_handler': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',
            'formatter': 'simple'
        },
        'file_handler': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'debug.log',
            'maxBytes': 1024,
            'backupCount': 3,
            'formatter': 'simple',
        }
    },
    'formatters': {
        'simple': {
            'format': '%(pathname)s:%(lineno)d %(name)s %(asctime)s - %(levelname)s - %(message)s',
        },
    },
})
'''

#hiding werkzeug and pdfminer logs from the console
werk_log = logging.getLogger('werkzeug')
werk_log.setLevel(logging.ERROR)
logging.getLogger("pdfminer").setLevel(logging.WARNING)

# logging.basicConfig(
#      filename='log_file_name.log',
#      level=logging.INFO, 
#      format= '[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s',
#      datefmt='%H:%M:%S'
#  )

console = logging.StreamHandler()
console.setLevel(logging.INFO)
# set a format which is simpler for console use
formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
console.setFormatter(formatter)
# add the handler to the root logger
logging.getLogger('imp_calc').addHandler(console)

logger = logging.getLogger(__name__)


# def expiry_check(checking_password_expiration):
#     def wrapper_func():
#         def checking_password_expiration():
#             time_between_insertion = datetime.now() - attempted_user.created_at
#             if time_between_insertion.days>30:
#                 flash('Sorry for the inconvenience but it seeems that your password expired,please create a new password using the expired ones')
#                 return redirect(url_for('change_password'))
#             else:
#                 if time_between_insertion.days<5:
#                     flash('Your password is about to expire within few days please change it.')
#     return wrapper_func

@app.route('/', methods = ['GET','POST'])
#@expiry_check
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        attempted_user = User.query.filter_by(username=form.username.data).first()
        #time_between_insertion = datetime.now() - attempted_user.created_at
        #print("This is the remaining time",time_between_insertion)
        #remaining_days = 30 - time_between_insertion.days
        #print("This is the remaining days",remaining_days)
        # if time_between_insertion.days>30:
        #     flash('Sorry for the inconvenience but it seeems that your password expired,please create a new password using the expired ones')
        #     return redirect(url_for('change_password'))
        # elif time_between_insertion.days>25:
        #         flash('Your password is about to expire within few days please change it.')
        # else:
        #     pass
        if attempted_user and attempted_user.check_password_correction(
                attempted_password=form.password.data
        ):
            login_user(attempted_user)
            flash(f'Success! You are logged in as: {attempted_user.username}', category='success')
            print(attempted_user.created_at)
            app.logger.info(attempted_user.username)
            app.logger.info('is logged in')
            return redirect(url_for('index'))
            
            logger.info(attempted_user.username," logged in successfully")
            session.permanent= True
        else:
            flash('Username and password are not match! Please try again', category='danger')
    return render_template('login.html', form = form)


@app.route('/index')
@login_required
def index():
    if current_user.is_authenticated:
        time_between_insertion = datetime.now() - current_user.created_at
        remaining_days = 30 - time_between_insertion.days
        if time_between_insertion.days>30:
            flash('Sorry for the inconvenience but it seeems that your password expired,please create a new password using the expired ones')
            return redirect(url_for('change_password'))
        elif time_between_insertion.days>25:
            flash('Your password is about to expire within few days please change it.')
        else:
            pass
        return render_template('index.html', remaining_days=remaining_days)
    else:
        return render_template('index.html')

@app.route('/register',methods=['GET', 'POST']) 
def register_page():
    form = RegisterForm()
    if form.validate_on_submit():
        user_to_create = User(username=form.username.data,
                              email_address=form.email_address.data,
                              password=form.password1.data)
        db.session.add(user_to_create)
        db.session.commit()
        login_user(user_to_create)
        flash(f"Account created successfully! You are now logged in as {user_to_create.username}", category='success')
        #app.logger.info("User Account:{user_to_create.username} created")
        return redirect(url_for('index')) #home is the function defined for '/'url just above this code
    if form.errors !={}: #if there are no errors from the validators
        for err_msg in form.errors.values():
            flash(f'There was an error while creating user:{err_msg}')

    return render_template('register.html', form=form)

#This one request to reset the password - https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-x-email-support
@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
        flash('You have to logout First')
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email_address=form.email.data).first()
        if user:
            send_password_reset_email(user)
            
        flash('Check your email for the instructions to reset your password')
        return redirect(url_for('login'))
    return render_template('reset_password_request.html',
                           title='Reset Password', form=form)
#This one will reset the passwordd
@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data) #WILL TRY THIS ONE IF CU DOESN'T WORK
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)

# @app.route('/login', methods=['GET', 'POST'])
# def login_page():
#     form = LoginForm()
#     if form.validate_on_submit():
#         attempted_user = User.query.filter_by(username=form.username.data).first()
#         if attempted_user and attempted_user.check_password_correction(
#                 attempted_password=form.password.data
#         ):
#             login_user(attempted_user)
#             flash(f'Success! You are logged in as: {attempted_user.username}', category='success')
#             return redirect(url_for('home'))
            
#             logger.info(attempted_user.username," logged in successfully")
#             session.permanent= True
#         else:
#             flash('Username and password are not match! Please try again', category='danger')

#     return render_template('login.html', form=form)

# @app.route('/login', methods =['GET','POST'])
# def login_page():
#     form = LoginForm()
#     if form.validate_on_submit():
#         attempted_user = User.query.filter_by(username=form.username.data).first()
#         if attempted_user and attempted_user.check_password_correction(
#             attempted_password = form.password.data
#         ):
#             login_user(attempted_user)
#             flash('Success! You are logged in as: {attempted_user.username}', category='success')
#             return redirect(url_for('home'))
#         else:
#             flash('Username and password does not match please try again', category='danger')

#     return render_template('login.html', form=form)
@app.route('/change_password',methods=['GET','POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    print(current_user)
    if form.validate_on_submit():
        #current_user = User.query.filter_by(id=curret_user.getid()).first()
        if current_user and current_user.check_password_correction(
                attempted_password=form.password_old.data
        ):
            id = current_user.get_id()
            user = User.query.filter_by(id=id).first_or_404()
            user.password=form.password_new2.data
            user.created_at= datetime.now()
            db.session.add(user)
            db.session.commit()
            logger.info(current_user.username)
            logger.info("changed password")
            logout_user()
            return redirect(url_for('index'))
    if form.errors !={}: #if there are no errors from the validators
        for err_msg in form.errors.values():
            flash(f'There was an error while creating user:{err_msg}',category='danger')
            #login_user(attempted_user)
    return render_template('change_password.html',form = form)        

@app.route('/logout',methods=['GET','POST'])
@login_required    
def logout_page():  
    logger.info(current_user.username)
    logger.info("logged out successfully")
    logout_user()
    #flash("You Have been logged out!", category= 'info')
    return redirect(url_for('login')) 


@app.route('/file_download/<path:output_folder>/<output_file>')
def file_download(output_folder, output_file):
    logger.info(current_user.username)
    logger.info("did a file file_download")
    file_location = os.path.join('/', output_folder, output_file)
    print(file_location)
    return send_file(file_location, as_attachment = True)
    #return send_file(file_location, as_attachment = True, cache_timeout=0)

@app.route('/RScalc',methods=['GET', 'POST'])
@login_required
def RScalc():
    logging.getLogger('imp_calc').info(current_user.username)
    logging.getLogger('imp_calc').info("Open RScalc")
    #logging.getLogger().info('log from root logger')
    #logging.getLogger('imp_calc').info('log from imp_calc logger')
    #app.logger.info('log from app logger')
    if request.method == "GET":
        return render_template('rsscreen.html')
    if request.method == "POST":
        process_impurities = request.form.getlist('process_impurities[]')
        if(len(process_impurities) ==1 and process_impurities[0] == ''):
            process_impurities = []
        UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)),
         'files', 'RS')
        [f.unlink() for f in Path(os.path.join(UPLOAD_FOLDER)).glob("*") if f.is_file()]
        print("This is pwd",os.getcwd())
        app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
        upload_files = []
        input_list = []
        input_list_fields =["software","compound","concentration","sampleweight","v1", "v2", "v3", "v4", "v5","v6", "v7","factor1","factor2","potency","doa","mor","wsid","ubd"]
        if request.files:
            upload_files = request.files.getlist('files')
        for file in upload_files:
            original_filename = file.filename
            # extension = original_filename.rsplit('.', 1)[1].lower()
            # filename = str(uuid.uuid1()) + '.' + extension
            # print("#######y###########",UPLOAD_FOLDER)
            filename = original_filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            file_list = os.path.join(UPLOAD_FOLDER, 'files.json')

        for field in input_list_fields:
            input_list.append(request.form[field])
        input_list[2:14] = [float(input) for input in input_list[2:14]]
        compound = input_list[1]
        area_input = os.path.join(UPLOAD_FOLDER, "{}-areas.pdf".format(compound))
        chrom_inputs = glob.glob(os.path.join(UPLOAD_FOLDER,'*.pdf'))
        try:
            chrom_inputs.remove(area_input)
        except ValueError as ve:
            print("Check the name of the RSD file. Make sure it is in the format: <compound name>-areas")
            return render_template('rsscreen.html')

        rs_output = RS_creator.initiate_report_creation(chrom_inputs, area_input, input_list, process_impurities)
        logging.getLogger('imp_calc').info(current_user.username)
        logging.getLogger('imp_calc').info("Used RS Calculation")
        rs_output.save(os.path.join(UPLOAD_FOLDER, "{}-RS.xls".format(compound)))
        return render_template('rsscreen.html', output_folder= UPLOAD_FOLDER, output_file =  "{}-RS.xls".format(compound))

@app.route('/RSacyclovir',methods=['GET', 'POST'])
@login_required
def RSacyclovir():
    logging.getLogger('imp_calc').info(current_user.username)
    logging.getLogger('imp_calc').info("Used RSacyclovir")
    if request.method == "GET":
        return render_template('rsacyclo.html')

    if request.method == "POST":
        UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)),
         'files', 'RS')
        [f.unlink() for f in Path(os.path.join(UPLOAD_FOLDER)).glob("*") if f.is_file()]
        upload_files = []
        input_list = []
        input_list_fields =["software","compound","concentration","sampleweight","v1", "v2", "v3", "v4", "v5","v6", "v7","factor1","factor2","potency","doa","mor","wsid","ubd", "compound-two","concentration-two","sampleweight-two","v1-two", "v2-two", "v3-two", "v4-two", "v5-two","v6-two", "v7-two","factor1-two","factor2-two","potency-two","doa-two","mor-two","wsid-two","ubd-two" ]
        app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
        if request.files:
            upload_files = request.files.getlist('files')
        for file in upload_files:
            original_filename = file.filename
            # extension = original_filename.rsplit('.', 1)[1].lower()
            # filename = str(uuid.uuid1()) + '.' + extension
            filename = original_filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            file_list = os.path.join(UPLOAD_FOLDER, 'files.json')
        for field in input_list_fields:
            input_list.append(request.form[field])
        input_list[2:14] = [float(input) for input in input_list[2:14]]
        input_list[19:31] = [float(input) for input in input_list[19:31]]

        area_input = os.path.join(UPLOAD_FOLDER, "Acyclovir-areas.pdf")
        area_input_imp_b = os.path.join(UPLOAD_FOLDER, "Impurity-B-areas.pdf")
        chrom_inputs = glob.glob(os.path.join(UPLOAD_FOLDER,'*.pdf'))
        chrom_inputs.remove(area_input)
        chrom_inputs.remove(area_input_imp_b)

        rs_output, imp_b_rs_output = RS_creator_acyclo.initiate_report_creation(chrom_inputs, area_input, area_input_imp_b, input_list)
        rs_output.save(os.path.join(UPLOAD_FOLDER, "Acyclovir-RS.xls"))
        imp_b_rs_output.save(os.path.join(UPLOAD_FOLDER, "Imp-B-RS.xls"))
        return render_template('rsacyclo.html', output_folder= UPLOAD_FOLDER, output_file1 =  "Acyclovir-RS.xls", output_file2 = "Imp-B-RS.xls")

@app.route('/Areanorm',methods=['GET', 'POST'])
@login_required
def Areanorm():
    logging.getLogger('imp_calc').info(current_user.username)
    logging.getLogger('imp_calc').info("Used Areanorm")
    if request.method == "GET":
        return render_template('area-normalization.html')
    if request.method == "POST":
        UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)),
         'files', 'Area-norm')
        [f.unlink() for f in Path(os.path.join(UPLOAD_FOLDER)).glob("*") if f.is_file()]
        upload_files = []
        input_list = []
        app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
        if request.files:
            upload_files = request.files.getlist('files')
        for file in upload_files:
            original_filename = file.filename
            # extension = original_filename.rsplit('.', 1)[1].lower()
            # filename = str(uuid.uuid1()) + '.' + extension
            filename = original_filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            file_list = os.path.join(UPLOAD_FOLDER, 'files.json')

        input_list_fields =["software","compound","dilution-factor-1","dilution-factor-2","doa"]
        mpa_fields = ["mpa"+ str(no) for no in range(0, len(upload_files))]
        input_list_fields += mpa_fields
        for field in input_list_fields:
            input_list.append(request.form[field])
        input_list[2] = float(input_list[2])
        input_list[3] = float(input_list[3])
        input_list[5:] = [float(mp) for mp in input_list[5:]]

        chrom_inputs = glob.glob(os.path.join(UPLOAD_FOLDER,'*.pdf'))

        compound = input_list[1]
        area_norm_output = area_norm.initiate_report_creation(chrom_inputs, input_list)
        area_norm_output.save(os.path.join(UPLOAD_FOLDER, "{}-area-norm.xls".format(compound)))

        return render_template('area-normalization.html', output_folder = UPLOAD_FOLDER, output_file =  "{}-area-norm.xls".format(compound))

@app.route('/Impvsimp',methods=['GET', 'POST'])
@login_required
def Impvsimp():
    logging.getLogger('imp_calc').info(current_user.username)
    logging.getLogger('imp_calc').info("Used Impvsimp")
    if request.method == "GET":
        return render_template('imp-vs-imp.html')

    if request.method == "POST":
        UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)),
         'files', 'Imp-vs-Imp')
        inputs = {
         'Ketorolac Tromethamine':{
         'Ketorolac Tromethamine': [],
         'Related Compound-A': [],
         'Related Compound-B': [],
         'Related Compound-C': [],
         'Related Compound-D': [],
         },
         'Propofol':{
         'Propofol':[],
         'Related Compound-A':[],
         'Related Compound-B':[]
         }
         }
        [f.unlink() for f in Path(os.path.join(UPLOAD_FOLDER)).glob("*") if f.is_file()]
        upload_files = []
        input_list = []
        app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
        if request.files:
            upload_files = request.files.getlist('files')
        for file in upload_files:
            original_filename = file.filename
            # extension = original_filename.rsplit('.', 1)[1].lower()
            # filename = str(uuid.uuid1()) + '.' + extension
            filename = original_filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            file_list = os.path.join(UPLOAD_FOLDER, 'files.json')

        compound = request.form["compound"]
        input_list_fields =["software","doa","mehtodofreference"]
        common_input_list =[]
        for field in input_list_fields:
            common_input_list.append(request.form[field])       
        if(compound == 'Ketorolac'):
            compound = 'Ketorolac Tromethamine'
            inputs = inputs[compound]
            fields = ["sampleweight", "v1", "v2", "v3", "v4", "v5", "potency", "wsid"]
            sub_compounds = {'k': 'Ketorolac Tromethamine', 'a':'Related Compound-A', 'b':'Related Compound-B', 'c':'Related Compound-C', 'd':'Related Compound-D'}
            for sub_compound in sub_compounds.keys():
                for field in fields:
                    input_field = field + "-" + sub_compound
                    inputs[sub_compounds[sub_compound]].append(request.form[input_field])
        elif(compound == 'Propofol'):
            inputs = inputs[compound]
            fields = ["sampleweight", "v1", "v2", "v3", "v4", "v5", "potency", "wsid"]
            sub_compounds = {'p': 'Propofol', 'pa':'Related Compound-A', 'pb':'Related Compound-B'}
            for sub_compound in sub_compounds.keys():
                for field in fields:
                    input_field = field + "-" + sub_compound
                    inputs[sub_compounds[sub_compound]].append(request.form[input_field])
        inputs['Details'] = common_input_list + [compound]
        chrom_inputs = glob.glob(os.path.join(UPLOAD_FOLDER,'*.pdf'))
        area_inputs = glob.glob(os.path.join(UPLOAD_FOLDER, '*standard*.pdf'))
        chrom_inputs = [chrom_input for chrom_input in chrom_inputs if chrom_input not in area_inputs]




        # assay_output = assay.initiate_report_creation(chrom_inputs, area_input, input_list, rt_range)
        # assay_output.save(os.path.join(UPLOAD_FOLDER, "{}-Assay.xls".format(compound)))

        

        ivi_output = imp_vs_imp.initiate_report_creation(chrom_inputs, area_inputs, inputs)
        ivi_output.save(os.path.join(os.path.join(os.path.dirname(os.path.abspath(__file__)),'files', 'Imp-vs-Imp'),
         "{}-imp-vs-imp.xls".format(compound)))



        return render_template('imp-vs-imp.html', output_folder = UPLOAD_FOLDER, output_file =  "{}-imp-vs-imp.xls".format(compound))

@app.route('/Assay',methods=['GET', 'POST'])
@login_required
def Assay():
    logging.getLogger('imp_calc').info(current_user.username)
    logging.getLogger('imp_calc').info("Used Assay")
    if request.method == "GET":
        return render_template('assay.html')

    if request.method == "POST":
        UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)),
         'files', 'Assay')
        [f.unlink() for f in Path(os.path.join(UPLOAD_FOLDER)).glob("*") if f.is_file()]
        upload_files = []
        input_list = []
        app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
        if request.files:
            upload_files = request.files.getlist('files')
        for file in upload_files:
            original_filename = file.filename
            # extension = original_filename.rsplit('.', 1)[1].lower()
            # filename = str(uuid.uuid1()) + '.' + extension
            filename = original_filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            file_list = os.path.join(UPLOAD_FOLDER, 'files.json')

        input_list_fields =["software","compound","product","concentration","sampleweight","v1", "v2", "v3", "v4", "v5","v6", "v7","factor1","factor2","potency","doa","mor","wsid","ubd"]
        for field in input_list_fields:
            input_list.append(request.form[field])
        input_list[3:15] = [float(input) for input in input_list[3:15]]
        compound = input_list[1]
        area_input = os.path.join(UPLOAD_FOLDER, "{}-areas.pdf".format(compound))
        chrom_inputs = glob.glob(os.path.join(UPLOAD_FOLDER,'*.pdf'))
        try:
            chrom_inputs.remove(area_input)
        except ValueError as ve:
            print("Check the name of the RSD file. Make sure it is in the format: <compound name>-areas")
            return render_template('assay.html')

        rt_range = []
        if(compound.lower() == 'methyl paraben'):
            rt_range = [7,10.7]
        if(compound.lower() == 'propyl paraben'):
            rt_range = [11,17]
        if(compound.lower() == 'p-hydroxy benzoic acid'):
            rt_range = [4,6.5]
        if(compound.lower() == 'benzaldehyde'):
            rt_range = [14,20]
        if(compound.lower() == 'benzoic acid'):
            rt_range = [8,13.5]
        assay_output = assay.initiate_report_creation(chrom_inputs, area_input, input_list, rt_range)
        assay_output.save(os.path.join(UPLOAD_FOLDER, "{}-Assay.xls".format(compound)))
        return render_template('assay.html', output_folder= UPLOAD_FOLDER, output_file =  "{}-Assay.xls".format(compound))

@app.route('/Lcysteine',methods=['GET', 'POST'])
@login_required
def Lcysteine():
    logging.getLogger('imp_calc').info(current_user.username)
    logging.getLogger('imp_calc').info("Used Lcysteine")
    if request.method == "GET":
        return render_template('lcysteine.html')

    if request.method == "POST":
        UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)),
         'files', 'Assay')
        [f.unlink() for f in Path(os.path.join(UPLOAD_FOLDER)).glob("*") if f.is_file()]
        upload_files = []
        input_list = []
        app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
        if request.files:
            upload_files = request.files.getlist('files')
        for file in upload_files:
            original_filename = file.filename
            # extension = original_filename.rsplit('.', 1)[1].lower()
            # filename = str(uuid.uuid1()) + '.' + extension
            filename = original_filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            file_list = os.path.join(UPLOAD_FOLDER, 'files.json')
        input_list_fields =["software","compound", "product", "concentration","sampleweight","v1", "v2", "v3", "v4", "v5","v6", "v7","factor1","factor2","potency","doa","mor","wsid","ubd"]
        density_feilds = ["density" + str(n) for n in range(len(upload_files)-1)]
        smplqty_fields = ["smplqty"+ str(n) for n in range(len(upload_files)-1)]
        input_list_fields += density_feilds
        input_list_fields += smplqty_fields
        for field in input_list_fields:
            input_list.append(request.form[field])
        input_list[3:15] = [float(input) for input in input_list[3:15]]
        input_list[19:] = [float(input) for input in input_list[19:]]
        compound = input_list[1]
        area_input = os.path.join(UPLOAD_FOLDER, "{}-areas.pdf".format(compound))
        chrom_inputs = glob.glob(os.path.join(UPLOAD_FOLDER,'*.pdf'))
        try:
            chrom_inputs.remove(area_input)
        except ValueError as ve:
            print("Check the name of the RSD file. Make sure it is in the format: <compound name>-areas")
            return render_template('lcysteine.html')

        l_cysteine_output = L_cysteine.initiate_report_creation(chrom_inputs, area_input, input_list)
        l_cysteine_output.save(os.path.join(UPLOAD_FOLDER, "{}-Assay.xls".format(compound)))
        return render_template('lcysteine.html', output_folder= UPLOAD_FOLDER, output_file =  "{}-Assay.xls".format(compound))
