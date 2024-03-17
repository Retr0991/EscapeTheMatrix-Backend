from flask import Flask, jsonify, request, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import random, os
from flask import Flask, request
# from dotenv import load_dotenv

# load_dotenv()

db_pass = 'postgresql://database_etm_eetz_user:z0EA3oLJXzxSAOw96W8e97wDOhFvHfEJ@dpg-cnr7s8sf7o1s73cmd0f0-a.singapore-postgres.render.com/database_etm_eetz'

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = db_pass
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Counter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    team_name = db.Column(db.String(50))
    count = db.Column(db.Integer, default=0)
    unique_id = db.Column(db.String(50), unique=True)
    leader_id = db.Column(db.String(50))
    lives = db.Column(db.Integer)

# Create the database tables
with app.app_context():
    db.create_all()


@app.route('/delete_all_data', methods=['GET'])
def delete_all_data():
    try:
        # Delete all records from the Counter table
        db.session.query(Counter).delete()
        db.session.commit()
        return jsonify({"message": "All data deleted successfully."}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500
    finally:
        db.session.close()


@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')


@app.route('/create_new', methods=['POST'])
def create_new():
    team_name = request.form["teamName"]
    leader_id = request.form["leaderID"]
    existing_entry = Counter.query.filter_by(team_name=team_name).first()
    if existing_entry:
        return render_template("index.html", alr="Team already Exists")
    unique_id = "ieee_"+str(random.randint(0, 999999))
    entry = Counter.query.filter_by(unique_id=unique_id).first()
    if entry is None:
        new_entry = Counter(leader_id=leader_id, team_name=team_name, unique_id=unique_id, count = 0, lives = 3)
        db.session.add(new_entry)
        db.session.commit()
        return render_template("index.html", alr="Your ID is {}".format(unique_id))
    else:
        return render_template("index.html", alr="Team already Exists")

@app.route('/increment', methods=['GET'])
def increment():
    return render_template("increment.html")

@app.route('/increment_counter', methods=['POST'])
def increment_counter():
    try:
        # Get the UID of the requester
        unique_id = request.form["unique_id"]
        # Check if unique_id exists in the database
        entry = Counter.query.filter_by(unique_id=unique_id).first()
        if entry and entry.lives > 0:
            entry.count += 1
        
        db.session.commit()
        return 'Leaderboard updated for UID: {}'.format(unique_id)
    except Exception as e:
        return f"An error occurred: {str(e)}"
    
@app.route('/d', methods=['GET'])
def lossed():
    return render_template("decrement.html")

@app.route('/dec', methods=['POST'])
def decreased():
    unique_id = request.form["unique_id"]
    entry = Counter.query.filter_by(unique_id=unique_id).first()
    if entry:
        entry.lives = entry.lives - 1
        db.session.commit()
        return 'Lives Remaining: {}'.format(entry.lives)
    else:
        return render_template("decrement.html", invalid_alert="Invalid unique ID entered.")



@app.route('/view_counter', methods=['GET'])
def view_counter():
    # Get all entries from the Counter table
    entries = Counter.query.order_by(Counter.count.desc()).all()
    return render_template('counter.html', entries=entries)

@app.route('/admin_ieee', methods=['GET'])
def admin():
    return render_template("admin.html", entries=Counter.query.all())

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)