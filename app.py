from flask import Flask, render_template, request, redirect, session, jsonify, url_for
from flask_cors import CORS
import os
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta
from chatbot import chat_with_gpt
import os
from flask import Flask, render_template, request, redirect, session, url_for
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, redirect, session, jsonify, url_for, flash

app = Flask(__name__, static_folder="static")
app.secret_key = os.urandom(24)
CORS(app)
app.permanent_session_lifetime = timedelta(minutes=10)

# Users with english routing name + Arabic display_name
users = {
    "montassar@example.com": {
        "password": generate_password_hash("father1234"),
        "name": "jennifer",
        "display_name": "جنيفر",
        "balance": 2450.00,
        "spending": {"Clothes": 300, "Food": 500, "Internet": 200, "Sport": 100},
        "weekly_spent": 250
    },
    "mohamed@example.com": {
        "password": generate_password_hash("mohamed123"),
        "name": "mohamed",
        "display_name": "محمد",
        "balance": 1500.00,
        "spending": {"Clothes": 300, "Food": 500, "Internet": 200, "Sport": 100},
        "weekly_spent": 180
    },
    "mustapha@example.com": {
        "password": generate_password_hash("mustapha123"),
        "name": "mustapha",
        "display_name": "مصطفى",
        "balance": 2100.00,
        "spending": {"Clothes": 450, "Food": 600, "Internet": 300, "Sport": 150},
        "weekly_spent": 220
    }
}

@app.route('/')
def home():
    if 'user' in session:
        u = users[session['user']]
        return render_template('index.html',
                               username=u['name'],
                               display_name=u['display_name'],
                               balance=u['balance'])
    return redirect('/login')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method=='POST':
        email = request.form['email']
        pw = request.form['password']
        u = users.get(email)
        if u and check_password_hash(u['password'], pw):
            session['user']=email
            session.permanent=True
            return redirect('/')
        return render_template('login.html', error="Invalid credentials")
    return render_template('login.html')

@app.route('/user/<username>', methods=['GET','POST'])
def user_page(username):
    # find by name
    user = next((u for u in users.values() if u['name']==username), None)
    if not user: return "User not found",404

    if request.method=='POST':
        try:
            amt = float(request.form['amount'])
            if amt>0: user['balance']+=amt
            flash(f"تمت إضافة ${amt:.2f} إلى رصيد {user['display_name']}")
        except: pass
        return redirect(url_for('user_page',username=username))

    return render_template('user.html',
                           display_name=user['display_name'],
                           balance=user['balance'],
                           spending=user['spending'],
                           weekly_spent=user['weekly_spent'])

@app.route('/chatbot', methods=['POST'])
def chatbot():
    data = request.json
    msg = data.get('message','')
    resp = chat_with_gpt(msg, users)
    return jsonify(response=resp)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')
UPLOAD_FOLDER = 'static/proofs'
ALLOWED_EXT = {'png','jpg','jpeg','gif','mp4','mov'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(fname):
    return '.' in fname and fname.rsplit('.',1)[1].lower() in ALLOWED_EXT

@app.route('/missions', methods=['GET', 'POST'])
def missions():
    if 'user' not in session:
        return redirect('/login')

    # init session counters
    session.setdefault('pray_count', 0)
    session.setdefault('gym_done', False)
    session.setdefault('completed_missions', [])

    if request.method == 'POST':
        mission = request.form.get('mission')
        file = request.files.get('proof')
        if mission == 'pray':
            if file and allowed_file(file.filename) and session['pray_count'] < 5:
                # save proof
                user = session['user']
                folder = os.path.join(app.config['UPLOAD_FOLDER'], user, 'pray')
                os.makedirs(folder, exist_ok=True)
                fn = secure_filename(file.filename)
                file.save(os.path.join(folder, fn))
                # increment
                session['pray_count'] += 1
                # reward if reached 5
                if session['pray_count'] == 5 and 'pray' not in session['completed_missions']:
                    users["mohamed@example.com"]['balance'] += 200
                    session['completed_missions'].append('pray')
                    flash("🎉 مبروك! أكملت الصلوات الخمس وتمت إضافة 200$ إلى رصيدك ")
        elif mission == 'gym':
            if file and allowed_file(file.filename) and not session['gym_done']:
                user = session['user']
                folder = os.path.join(app.config['UPLOAD_FOLDER'], user, 'gym')
                os.makedirs(folder, exist_ok=True)
                fn = secure_filename(file.filename)
                file.save(os.path.join(folder, fn))
                session['gym_done'] = True
                if 'gym' not in session['completed_missions']:
                    users["mohamed@example.com"]['balance'] += 200
                    session['completed_missions'].append('gym')
                    flash("🎉 مبروك! أكملت الذهاب إلى النادي وتمت إضافة 200$ إلى رصيدك ")

        session.modified = True

    return render_template('missions.html',
                           pray_count=session['pray_count'],
                           gym_done=session['gym_done'],
                           completed=session['completed_missions'])

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
