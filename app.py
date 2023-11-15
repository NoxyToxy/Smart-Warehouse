from flask import Flask, redirect, render_template, request, session, url_for, jsonify
from flask_bcrypt import Bcrypt
from pymongo import MongoClient
from datetime import datetime
from bson.objectid import ObjectId


app = Flask(__name__)
app.secret_key = 'your_seret_key'
bcrypt = Bcrypt(app)

login = 'your_login'
password = 'your_password'
client = MongoClient(f'mongodb+srv://{login}:{password}@cluster0.u1crvda.mongodb.net/?retryWrites=true&w=majority')

@app.route('/')
def redirect_to_login():
    if 'username' in session:
        return redirect('/dashboard')
    else:
        return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'username' in session:
        return redirect('/dashboard')

    db = client["Users"]
    collection = db["user_auth"]

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = collection.find_one({'login': username})
        if user and bcrypt.check_password_hash(user['password'], password):
            session['username'] = username
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Invalid username or password!')
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        db = client["Users"]
        users_collection = db["users"]
        user_auth_collection = db["user_auth"]
        username = session['username']
        user = user_auth_collection.find_one({'login': username})
        user_data = users_collection.find_one({'id': user['user_id']})
        fullname = user_data["fullname"]
        age = user_data["age"]
        specialization = user_data["specialization"]

        db = client['Materials']
        collection = db['accounting']

        result = {}
        for doc in collection.find():
            date = doc['date']
            issuance = doc['issuance']
            total = sum(item['amount'] for item in issuance)
            if date in result:
                result[date] += total
            else:
                result[date] = total

        db = client['Materials']
        collection = db['inStock']
        materials = list(collection.find())

        return render_template("dashboard.html", fullname=fullname, age=age,
                               specialization=specialization, result=result, materials=materials)
    return redirect(url_for('login'))

@app.route('/account')
def account():
    if 'username' in session:
        db = client["Users"]
        users_collection = db["users"]
        addresses_collection = db["addresses"]
        contact_collection = db["contact_info"]
        user_auth_collection = db["user_auth"]
        username = session['username']
        user = user_auth_collection.find_one({'login': username})
        user_data = users_collection.find_one({'id': user['user_id']})
        fullname = user_data["fullname"]
        age = user_data["age"]
        specialization = user_data["specialization"]
        address_id = user_data["address"]
        address_doc = addresses_collection.find_one({"_id": address_id})
        address = address_doc["address"]

        phone_number_id = user_data["phone_number"]
        phone_number_doc = contact_collection.find_one({"_id": phone_number_id})
        phone_number = phone_number_doc["phone_number"]

        email_id = user_data["email"]
        email_doc = contact_collection.find_one({"_id": email_id})
        email = email_doc["email"]

        return render_template("account.html", fullname=fullname, age=age, specialization=specialization, address=address, phone_number=phone_number, email=email)
    return redirect(url_for('login'))

@app.route('/warehouse')
def warehouse():
    if 'username' in session:
        db = client['Materials']
        collection = db['inStock']
        materials = list(collection.find())
        return render_template("warehouse.html", materials=materials)
    return redirect(url_for('login'))

@app.route('/delete/<id>', methods=['DELETE'])
def delete(id):
    db = client['Materials']
    collection = db['inStock']

    material = collection.find_one({"_id": ObjectId(id)})
    name = material['name']
    amount = material['amount']
    took_amount = int(request.get_json().get('amount'))

    if amount > 1 and took_amount != amount:
        collection.update_one({"_id": ObjectId(id)}, {"$inc": {"amount": -took_amount}})
    elif took_amount > amount:
        return redirect(url_for('dashboard'))
    else:
        collection.delete_one({"_id": ObjectId(id)})

    db = client["Users"]
    users_collection = db["users"]
    user_auth_collection = db["user_auth"]
    username = session['username']
    user = user_auth_collection.find_one({'login': username})
    user_data = users_collection.find_one({'id': user['user_id']})
    fullname = user_data["fullname"]

    db = client['Materials']
    collection = db['accounting']
    query = {"date": datetime.now().strftime("%d.%m.%Y")}
    doc = collection.find_one(query)

    if not doc:
        doc = {
            "date": datetime.now().strftime("%d.%m.%Y"),
            "receipt": [],
            "issuance": []
        }
        collection.insert_one(doc)

    # Обновление документа
    new_values = {"$push": {"issuance": {"name": name, "amount": amount, "fullname": fullname}}}
    collection.update_one(query, new_values)

    return 'ok'




@app.route('/store')
def store():
    if 'username' in session:
        db = client['Materials']
        collection = db['materials']
        materials = list(collection.find())
        return render_template("store.html", materials=materials)
    return redirect(url_for('login'))

@app.route('/buy/<id>', methods=['POST'])
def buy_material(id):
    db = client['Materials']
    collection = db['materials']
    material = collection.find_one({"_id": ObjectId(id)})
    name = material['name']
    amount = int(request.json['amount'])
    collection = db['inStock']
    document = collection.find_one({"name": name})
    current_date = datetime.now().strftime('%d.%m.%Y')
    if document:
        new_amount = document['amount'] + amount
        collection.update_one({"name": name}, {"$set": {"amount": new_amount, "receipt_date": current_date}})
    else:
        new_document = {
            "name": name,
            "amount": amount,
            "receipt_date": current_date
        }
        collection.insert_one(new_document)

    collection = db['accounting']
    query = {"date": datetime.now().strftime("%d.%m.%Y")}
    doc = collection.find_one(query)

    if not doc:
        doc = {
            "date": datetime.now().strftime("%d.%m.%Y"),
            "receipt": [],
            "issuance": []
        }
        collection.insert_one(doc)

    # Обновление документа
    new_values = {"$push": {"receipt": {"name": name, "amount": amount, "receipt_date": current_date}}}
    collection.update_one(query, new_values)

@app.route('/accounting', methods=['GET', 'POST'])
def accounting():
    if 'username' in session:
        if request.method == 'POST':
            db = client['Materials']
            collection = db['accounting']

            date = request.form['receipt_date']
            date_obj = datetime.strptime(date, '%Y-%m-%d')
            receipt_date = date_obj.strftime('%d.%m.%Y')

            results = collection.find({'date': receipt_date})

            data = []
            for result in results:
                data.append({'receipt': result['receipt'], 'issuance': result['issuance']})

            return jsonify(data)
        return render_template('accounting.html')
    return redirect(url_for('login'))

@app.route('/receipt', methods=['GET', 'POST'])
def receipt():
    if 'username' in session:
        if request.method == 'POST':
            db = client['Materials']
            collection = db['accounting']

            date = request.form['receipt_date']
            date_obj = datetime.strptime(date, '%Y-%m-%d')
            receipt_date = date_obj.strftime('%d.%m.%Y')

            data = []

            for doc in collection.find({'date': receipt_date}):
                receipt = doc['receipt']

                for i in receipt:
                    data.append({'material_name': i['name'], 'quantity': i['amount'],
                             'receipt_date': i['receipt_date']})

            return jsonify(data)
        return render_template('receipt.html')
    return redirect(url_for('login'))

@app.route('/invoices', methods=['GET', 'POST'])
def invoices():
    if 'username' in session:
        if request.method == 'POST':
            db = client['Materials']
            collection = db['accounting']

            date = request.form['receipt_date']
            date_obj = datetime.strptime(date, '%Y-%m-%d')
            receipt_date = date_obj.strftime('%d.%m.%Y')

            data = []

            for doc in collection.find({'date': receipt_date}):
                receipt = doc['receipt']

                for i in receipt:
                    data.append({'material_name': i['name'], 'quantity': i['amount'],
                             'receipt_date': i['receipt_date']})

            return jsonify(data)
        return render_template("invoices.html")
    return redirect(url_for('login'))

@app.route('/analysis')
def analysis():
    if 'username' in session:
        db = client['Materials']
        collection = db['accounting']

        result = {}
        for doc in collection.find():
            date = doc['date']
            issuance = doc['issuance']
            total = sum(item['amount'] for item in issuance)
            if date in result:
                result[date] += total
            else:
                result[date] = total

        return render_template("analysis.html", result=result)
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))


if __name__ == "__main__":
    app.run(debug=True)
