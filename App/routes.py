from App import app, db
from App.forms import EmployeeForm, TaskForm, loginForm, RegisterForm,AddProjectForm,loginFormEmp
from flask import render_template, redirect, url_for, flash, request
from App.models import task, admin, directeur, employee,projet
from flask_login import login_user, logout_user, login_required, current_user
from flask import session
import secrets
import string

ROW_PER_PAGE = 3
@app.route('/home', methods=['GET', 'POST'])
@app.route('/', methods=['GET', 'POST'])
def Hompage():
    return render_template("HomePage/index.html")


@app.route('/login', methods=['GET', 'POST'])
def login_direc():
    if session.get('user_type'):
        if session.get('user_type') == 'admin':
            flash("Please logout to access this page", category='danger')
            return redirect(url_for('Dashboard_admin'))
        elif session.get('user_type') == 'employee':
            flash("Please logout to access this page", category='danger')
            return redirect(url_for('dash_emp'))
        elif session['user_type']=='directeur':
            flash('You are already loged in',category='info')
            return redirect(url_for('Dashboard_direc'))
    form = loginForm()
    if form.validate_on_submit():
        session.clear()
        attempted_user = directeur.query.filter_by(username=form.username.data).first()
        if attempted_user and attempted_user.check_password_correction(attempted_password=form.password.data):
            if int(attempted_user.get_state()) == 0:
                flash(f'Your account is awaiting Admin decision to accept',category='info')
                return  render_template('directeur/Login_direc.html', form=form)
            login_user(attempted_user)
            session['user_type'] = 'directeur'
            if attempted_user.Projects:
                session['selected_projetc_id'] = attempted_user.Projects[0].id
            flash(f'Success! Your are loged in as: {attempted_user.username} ', category='success')
            return redirect(url_for('Dashboard_direc'))
        else:
            flash('Username and password are not match! Please try again', category='danger')

    return render_template('directeur/Login_direc.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register_direc():
    if session.get('user_type'):
        if session.get('user_type') == 'admin':
            flash("Please logout to access this page", category='danger')
            return redirect(url_for('Dashboard_admin'))
        elif session.get('user_type') == 'employee':
            flash("Please logout to access this page", category='danger')
            return redirect(url_for('dash_emp'))
        elif session.get('user_type') == 'directeur':
            flash('You are already loged in',category='info')
            return redirect(url_for('Dashboard_direc'))
    form = RegisterForm()
    if form.validate_on_submit():
        user_to_create = directeur(email_adress=form.email_adress.data,
                                  firstName = form.nom.data,
                                  lastName = form.lastName.data,
                                  phone = form.phone.data,
                                  departement = form.phone.data,
                                  poste = form.poste.data,
                                  username=form.username.data,
                                  password=form.password1.data,
                                  state = 0)
        db.session.add(user_to_create)
        db.session.commit()
        flash(f'Account created successfuly! You are loged in as : {user_to_create.username} ', category='success')
        return redirect(url_for('login_direc'))
    if form.errors != {}:
        for err_msg in form.errors.values():
            flash(f'There was an error with creating a user: {err_msg}', category='danger')
    return render_template('directeur/Register_direc.html', form=form)


@app.route('/dashboard',methods=['GET', 'POST'])
@login_required
def Dashboard_direc():
    #bug sooner i'll fixe it
    if session.get('user_type') == 'admin':
        flash("You cannot access this page", category='danger')
        return redirect(url_for('Dashboard_admin'))
    elif session.get('user_type') == 'employee':
        flash("You cannot access this page", category='danger')
        return redirect(url_for('dash_emp'))

    selectedProjectId = session.get('selected_projetc_id')
    # fetch users Number
    usersNumber = employee.query.filter_by(projet_id=selectedProjectId).count()
    # fetch nombre Tasks Totale
    totalTasks = task.query.filter_by(projet_id=selectedProjectId).count()
    # fetch nombre task valide
    validTasks = task.query.filter_by(projet_id=selectedProjectId, status=1).count()
    # fetch nombre task in progress(not valid yet)
    inValidTasks = task.query.filter_by(projet_id=selectedProjectId, status=0).count()
    # fetch list of employees
    employeesList = employee.query.filter_by(projet_id=selectedProjectId).all()

    return render_template('directeur/Dashboard_direc.html',usersNumber = usersNumber,totalTasks=totalTasks,validTasks = validTasks,inValidTasks = inValidTasks,employeesList=employeesList)

@app.route('/space/<id>/<nextUrl>')
@login_required
def changeProjectSpace(id,nextUrl):
    # sooner i'll add middleware golabaly
    session['selected_projetc_id'] = int(id)
    return redirect('/'+nextUrl)

@app.route('/projet',methods=['GET', 'POST'])
@login_required
def projetPage():
    if session.get('user_type') == 'admin':
        flash("You cannot access this page", category='danger')
        return redirect(url_for('Dashboard_admin'))
    elif session.get('user_type') == 'employee':
        flash("You cannot access this page", category='danger')
        return redirect(url_for('dash_emp'))
    form=AddProjectForm()
    page = request.args.get('page',1,type=int)
    projetData = projet.query.filter(projet.direct_id == current_user.id,projet.id != session.get('selected_projetc_id')).paginate(page = page,per_page=ROW_PER_PAGE)
    if request.method == 'POST':
        if form.validate_on_submit():
            projetToCreate = projet(projet_title = form.project_title.data,projet_description=form.project_description.data,direct_id=current_user.id)
            db.session.add(projetToCreate)
            db.session.commit()
            flash('Projet Added Succeflully!',category='success')
            return redirect(url_for('projetPage'))
        else:
            flash('Error submitting the form',category='error')
            
    return render_template('directeur/Projets.html',form = form,projetData=projetData)

@app.route('/actionProjet/<name>/<id>')
@login_required
def actionProjet(name,id):
    if session.get('user_type') == 'admin':
        flash("You cannot access this page", category='danger')
        return redirect(url_for('Dashboard_admin'))
    elif session.get('user_type') == 'employee':
        flash("You cannot access this page", category='danger')
        return redirect(url_for('dash_emp'))
    if name == '':
        flash('Invalid Action name!',category='error')
        redirect(url_for('projetPage'))
    if name == 'delete':
        if request.method != 'GET':
            flash('Error deleting projet',category='error')
        else:
            projetToDelete = projet.query.filter_by(id = id).first()
            flash('Projet deleted succefully',category='info')
            db.session.delete(projetToDelete)
            db.session.commit()
    return redirect(url_for('projetPage'))



@app.route('/employees',methods=['GET', 'POST'])
@login_required
def employeePage():
    if session.get('user_type') == 'admin':
        flash("You cannot access this page", category='danger')
        return redirect(url_for('Dashboard_admin'))
    elif session.get('user_type') == 'employee':
        flash("You cannot access this page", category='danger')
        return redirect(url_for('dash_emp'))
    form=EmployeeForm()
    page = request.args.get('page',1,type=int)
    employeeData = employee.query.filter(employee.projet_id == session.get('selected_projetc_id')).paginate(page = page,per_page=ROW_PER_PAGE)
    if form.validate_on_submit():
        #Generate password
        alphabets = string.ascii_letters + string.digits
        password = ''.join(secrets.choice(alphabets) for i in range(8))
        if current_user.Projects :
            employeeToCreate = employee(
                firstName=form.firstName.data,
                lastName=form.lastName.data,
                phone = form.phone.data,
                poste = form.poste.data,
                email_adress = form.email_adress.data,
                password = password,
                projet_id = session.get('selected_projetc_id')
                )
            db.session.add(employeeToCreate)
            db.session.commit()
            flash('Email send it to '+str(form.firstName.data+' !'),category='success')
            return redirect(url_for('employeePage'))
        else:
            flash("You have to add a project first",category="info")
    if form.errors != {}:
        for err_msg in form.errors.values():
            flash(f'There was an error with creating a user: {err_msg}', category='danger')
    return render_template('directeur/Employees.html',form = form,employeeData=employeeData)

@app.route('/actionEmployee/<name>/<id>')
@login_required
def actionEmployee(name,id):
    if session.get('user_type') == 'admin':
        flash("You cannot access this page", category='danger')
        return redirect(url_for('Dashboard_admin'))
    elif session.get('user_type') == 'employee':
        flash("You cannot access this page", category='danger')
        return redirect(url_for('dash_emp'))
    if name == '':
        flash('Invalid Action name!',category='error')
        redirect(url_for('employeePage'))
    if name == 'delete':
        if request.method != 'GET':
            flash('Error deleting employee',category='error')
        else:
            employeeToDelete = employee.query.filter_by(id = id).first()
            flash('Employee deleted succefully',category='info')
            db.session.delete(employeeToDelete)
            db.session.commit()
    return redirect(url_for('employeePage'))

@app.route('/employee/<id>' ,methods=['GET', 'POST'])
@login_required
def getEmployeeById(id):
    if session.get('user_type') == 'admin':
        flash("You cannot access this page", category='danger')
        return redirect(url_for('Dashboard_admin'))
    elif session.get('user_type') == 'employee':
        flash("You cannot access this page", category='danger')
        return redirect(url_for('dash_emp'))

    #verify if employee 
    page = request.args.get('page',1,type=int)
    form = TaskForm()
    try:
        employeeDetail = employee.query.filter_by(id = id).first()
        projetData = projet.query.filter_by(id=employeeDetail.projet_id).first()
        projetTitle = projetData.projet_title
    except:
        flash('Employee not found!',category='info')
        return redirect(url_for('employeePage')) 
    
    tasksData = task.query.filter_by(employee_id = id).paginate(page = page,per_page=ROW_PER_PAGE)
    if current_user.id != projetData.direct_id:
        flash('Acces denied!',category='info')
        return redirect(url_for('employeePage'))
    if request.method == 'POST':
        if form.validate_on_submit():
            taskToCreate = task(
                task_title = form.taskTitle.data,
                task_description = form.description.data,
                status = 0,
                employee_id = id,
                projet_id = session.get('selected_projetc_id')
            )
            db.session.add(taskToCreate)
            db.session.commit()
            flash('new task on the list',category='info')
            return redirect(url_for('getEmployeeById',id=id))
        else:
            flash('all field required!',category='warning')
            return redirect(url_for('getEmployeeById',id=id))


    return render_template('directeur/Employee_detail.html',form=form,employeeDetail=employeeDetail,projetTitle=projetTitle,tasksData=tasksData)
 

@app.route('/actionTask/<name>/<id>/<idEmployee>')
@login_required
def actionTask(name,id,idEmployee):
    if session.get('user_type') == 'admin':
        flash("You cannot access this page", category='danger')
        return redirect(url_for('Dashboard_admin'))
    elif session.get('user_type') == 'employee':
        flash("You cannot access this page", category='danger')
        return redirect(url_for('dash_emp'))
    if name == '':
        flash('Invalid Action name!',category='danger')
        return redirect(url_for('getEmployeeById',id=idEmployee))

    if name == 'delete':
        if request.method != 'GET':
            flash('Error deleting employee',category='danger')
        else:
            taskToDelete = task.query.filter_by(id = id).first()
            flash('Task deleted succefully',category='info')
            db.session.delete(taskToDelete)
            db.session.commit()
    return redirect(url_for('getEmployeeById',id=idEmployee))


#-------------------------------------------------------------------END OF DIRECTOR ROUTES












#Admin routes
@app.route('/admin/',methods=['GET', 'POST'])
@app.route('/admin/login', methods=['GET', 'POST'])
def login_admin():
    if session.get('user_type'):
        if session.get('user_type') == 'admin':
            flash('You are already loged in',category='info')
            return redirect(url_for('Dashboard_admin'))
        elif session.get('user_type') == 'employee':
            flash("Please logout to access this page", category='danger')
            return redirect(url_for('dash_emp'))
        elif session['user_type']=='directeur':
            flash("Please logout to access this page", category='danger')
            return redirect(url_for('Dashboard_direc'))
    form = loginForm()
    if form.validate_on_submit():
        print("hi")
        ad = admin.query.filter_by(username=form.username.data).first()
        if ad and ad.check_password_correction(attempted_password=form.password.data):
            login_user(ad)
            session['user_type'] = 'admin'
            flash(f'Success! Your are loged in as: {ad.username} ', category='success')
            return redirect(url_for('Dashboard_admin'))
        else:
            flash('Username and password are not match! Please try again', category='danger')

    return render_template('admin/Login_admin.html', form=form)


@app.route('/admin/dashboard')
@login_required
def Dashboard_admin():
    if session.get('user_type') == 'directeur':
        flash("You cannot access this page", category='danger')
        return redirect(url_for('Dashboard_direc'))
    elif session.get('user_type') == 'employee':
        flash("You cannot access this page", category='danger')
        return redirect(url_for('dash_emp'))

    inProgressAccounts = directeur.query.filter_by(state = 0).all()
    return render_template('admin/Dashboard_admin.html',inProgressAccounts = inProgressAccounts)

@app.route('/admin/DeleteDirecteur')#***************
@login_required
def Delete_directeur():
    if session.get('user_type') == 'directeur':
        flash("You cannot access this page", category='danger')
        return redirect(url_for('Dashboard_direc'))
    elif session.get('user_type') == 'employee':
        flash("You cannot access this page", category='danger')
        return redirect(url_for('dash_emp'))

    Directeur_accounts=directeur.query.filter_by(state=1).all()
    return render_template('admin/Delete_direc.html',Directeur_accounts=Directeur_accounts)


@app.route('/admin/<decision>/<idDirecteur>/')
@login_required
def direcMakeDecision(decision,idDirecteur):
    if session.get('user_type') == 'directeur':
        flash("You cannot access this page", category='danger')
        return redirect(url_for('Dashboard_direc'))
    elif session.get('user_type') == 'employee':
        flash("You cannot access this page", category='danger')
        return redirect(url_for('dash_emp'))
    dirctrToUpdateState = directeur.query.filter_by(id = idDirecteur ).first()
    if decision == 'accept':
       dirctrToUpdateState.state = 1
       db.session.commit()
    elif decision == 'refuse':
       db.session.delete(dirctrToUpdateState)
       db.session.commit()
    return redirect(url_for('Dashboard_admin'))



@app.route('/logout')
def logout_page():
    if(session.get('user_type') == 'admin'):
        logout_user()
        flash("You have been logged out!", category='info')
        if session.get('user_type') != None : session.pop('user_type')
        return redirect(url_for("login_admin"))
    if(session.get('user_type') == 'employee'):
        logout_user()
        flash("You have been logged out!", category='info')
        if session.get('user_type') != None : session.pop('user_type')
        return redirect(url_for("LoginEmp"))
    else:
        logout_user()
        flash("You have been logged out!", category='info')
        session.pop('user_type') if session.get('user_type') != None else None
        return redirect(url_for("login_direc"))

#-------------------------------------------------------------------END OF admin ROUTES


@app.route("/loginEmp",methods=['GET', 'POST'])
def LoginEmp():
    if session.get('user_type'):
        if session.get('user_type') == 'admin':
            flash("Please logout to access this page", category='danger')
            return redirect(url_for('Dashboard_admin'))
        elif session.get('user_type') == 'employee':
            flash('You are already loged in',category='info')
            return redirect(url_for('dash_emp'))
        elif session['user_type'] == 'directeur':
            flash("Please logout to access this page", category='danger')
            return redirect(url_for('Dashboard_direc'))
    form=loginFormEmp()
    if form.validate_on_submit():
        emp=employee.query.filter_by(email_adress=form.email_adress.data).first()
        if emp and emp.check_password_correction(attempted_password=form.password.data):
            login_user(emp)
            session['user_type'] = 'employee'
            return redirect(url_for("dash_emp"))
            flash("login succes", category="success")

        else:
            flash('Username and password are not match! Please try again', category='danger')
    return render_template("Employee/login_emp.html",form=form)




@app.route("/dashboardEmp",methods=['GET', 'POST'])
@login_required
def dash_emp():
    if session.get('user_type') == 'directeur' :
        flash("You cannot access this page", category='danger')
        return redirect(url_for('Dashboard_direc'))
    elif session.get('user_type')=='admin':
        flash("You cannot access this page", category='danger')
        return redirect(url_for('Dashboard_admin'))
    validTasks=task.query.filter_by(employee_id=current_user.id,status=1).count()

    invalidTasks=task.query.filter_by(employee_id=current_user.id,status=0).count()

    TotalTasks=task.query.filter_by(employee_id=current_user.id).count()
    tasks=task.query.filter_by(employee_id=current_user.id,status=0)
    selectedprojet=projet.query.filter_by(id=current_user.projet_id).first()
    Employees=employee.query.filter_by(projet_id=selectedprojet.id).count()

    print(Employees)

    return render_template("Employee/Dashboard_employee.html",tasks=tasks,validTasks=validTasks,invalidTasks=invalidTasks,TotalTasks=TotalTasks,Employees=Employees)


@app.route("/dashboardEmp/<taskID>/")
@login_required
def changeState(taskID):
    if session.get('user_type') == 'directeur':
        flash("You cannot access this page", category='danger')
        return redirect(url_for('Dashboard_direc'))
    elif session.get('user_type') == 'admin':
        flash("You cannot access this page", category='danger')
        return redirect(url_for('Dashboard_admin'))
    taskToUpdate=task.query.filter_by(id=taskID).first()
    taskToUpdate.status=1
    db.session.commit()
    # task.status=1
    # db.session.commit()
    flash("Task completed",category="info")
    # tasktoUpdate=task.query.filter_by()
    return redirect(url_for('dash_emp'))


@app.route("/completedTask")
@login_required
def completedTask():
    if session.get('user_type') == 'directeur':
        flash("You cannot access this page", category='danger')
        return redirect(url_for('Dashboard_direc'))
    elif session.get('user_type') == 'admin':
        flash("You cannot access this page", category='danger')
        return redirect(url_for('Dashboard_admin'))
    validTasks = task.query.filter_by(employee_id=current_user.id, status=1).count()

    invalidTasks = task.query.filter_by(employee_id=current_user.id, status=0).count()

    TotalTasks = task.query.filter_by(employee_id=current_user.id).count()
    completedTask=task.query.filter_by(status=1,employee_id=current_user.id)

    selectedprojet = projet.query.filter_by(id=current_user.projet_id).first()
    Employees = employee.query.filter_by(projet_id=selectedprojet.id).count()
    return render_template("Employee/completedTask.html",completedTask=completedTask,validTasks=validTasks,invalidTasks=invalidTasks,TotalTasks=TotalTasks,Employees=Employees)
