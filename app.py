from flask import Flask, jsonify, request, render_template
from flask_sqlalchemy import SQLAlchemy
import random, os
from dotenv import load_dotenv

load_dotenv()

db_pass = os.getenv("RENDER_POSTGRESQL")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = db_pass
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Counter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    team_name = db.Column(db.String(50), unique=True)
    count = db.Column(db.Integer, default=0)
    unique_id = db.Column(db.String(50), unique=True)
    leader_id = db.Column(db.String(50), unique=True)

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
    unique_id = "ieee_"+str(random.randint(0, 999))
    entry = Counter.query.filter_by(unique_id=unique_id).first()
    if entry is None:
        new_entry = Counter(leader_id=leader_id, team_name=team_name, unique_id=unique_id, count = 0)
        db.session.add(new_entry)
        db.session.commit()
        return jsonify({"Success. Your ID is":unique_id})
    else:
        return jsonify({"Already":"Exists"})

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
        if entry:
            entry.count += 1
        
        db.session.commit()
        Counter.query.order_by(Counter.count.desc()).all()
        
        return 'Counter incremented for UID: {}'.format(unique_id)
    except Exception as e:
        return f"An error occurred: {str(e)}"


@app.route('/view_counter', methods=['GET'])
def view_counter():
    # Get all entries from the Counter table
    entries = Counter.query.all()
    return render_template('counter.html', entries=entries)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
