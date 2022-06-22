from App import app, db
from flask import jsonify, request,json
from App.models import directeur, employee,projet
from App import bcrypt
import jwt


jwt_secret_key = "ahmed"
#Return response
def jsonResponse(jsonRes,responseCode):
    return app.response_class(
        response=json.dumps(jsonRes),
        status = responseCode,
        mimetype='application/json'
    )


@app.route('/api/login',methods=['POST'])
def loginEmployee():
    body = request.get_json()
    try:
        email = body["email"]
        password = body["password"]
    except:
        return jsonResponse({"error":"missing body"},400)
    
    try:
        findByEmail =  employee.query.filter_by(email_adress = email).first()
        if findByEmail == None:
            return jsonResponse({"error":"LOGIN FAILED (Email not found)"},401) #UNAUTHORIZED RESPONSE
        #verify password
        verifyPassword = bcrypt.check_password_hash(findByEmail.password_hash,password)
        if verifyPassword == False:
         return jsonResponse({"error":"password incorrect!"},401)  

        #return jwt in json response and GG WP
        projetOfEmployee = projet.query.filter_by(id = findByEmail.projet_id).first()
        bossOfEmployee = directeur.query.filter_by(id = projetOfEmployee.direct_id).first()
        payload = {
            "firstName":findByEmail.firstName,
            "lastName":findByEmail.lastName,
            "phone":findByEmail.phone,
            "email":findByEmail.email_adress,
            # "projet_id":findByEmail.projet_id,
            # "projet_title":projetOfEmployee.projet_title,
            # "projet_description":projetOfEmployee.projet_description
            "poste":findByEmail.poste,        
            }
        #Generate jwt
        token = jwt.encode(payload=payload,key=jwt_secret_key,algorithm="HS256")
        ResponseJson = [{
            "projet_id":findByEmail.projet_id,
            "projet_title":projetOfEmployee.projet_title,
            "projet_description":projetOfEmployee.projet_description,
            "projet_boss_firstName":bossOfEmployee.firstName,
            "projet_boss_lastName":bossOfEmployee.lastName,
            "projet_boss_id":bossOfEmployee.id,
            "Tasks":[ obj.toJson() for obj in findByEmail.Tasks]
        }]
        ResponseJson.append({"token":token})

        return jsonResponse(ResponseJson,200)

    except Exception as e:
        return jsonResponse({"error":str(e)},500) #in case of exception 

    return 'h'

