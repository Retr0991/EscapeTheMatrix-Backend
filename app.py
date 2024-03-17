from flask import Flask, jsonify, request, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://database_etm_8dms_user:z0jbTb9cQ6CDFkJDYTVivaZz5J5AhOcy@dpg-cnr2vt21hbls73dtptcg-a/database_etm_8dms'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Counter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    leader_id = db.Column(db.String(50))
    ip_address = db.Column(db.String(50), unique=True)
    team_name = db.Column(db.String(50), unique=True)
    count = db.Column(db.Integer, default=0)

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
    ip_address = request.form["ipAddress"]
    team_name = request.form["teamName"]
    leader_id = request.form["leaderID"]
    ip_entry = Counter.query.filter_by(ip_address=ip_address).first()
    if ip_entry is None:
        new_entry = Counter(leader_id=leader_id, team_name=team_name, ip_address=ip_address, count = 0)
        db.session.add(new_entry)
        db.session.commit()
        return jsonify({"Success":"Created"})
    else:
        return jsonify({"Already":"Exists"})

@app.route('/increment_counter', methods=['GET'])
def increment_counter():
    try:
        # Get the IP address of the requester
        ip_address = request.remote_addr
        # Check if IP address exists in the database
        ip_entry = Counter.query.filter_by(ip_address=ip_address).first()
        if ip_entry:
            ip_entry.count += 1
        
        db.session.commit()
        Counter.query.order_by(Counter.count.desc()).all()
        
        return 'Counter incremented for IP: {}'.format(ip_address)
    except Exception as e:
        return f"An error occurred: {str(e)}"


@app.route('/get_counter', methods=['GET'])
def get_counter():
    # Get the IP address of the requester
    ip_address = request.remote_addr
    
    # Get the counter value for this IP address
    ip_entry = Counter.query.filter_by(ip_address=ip_address).first()
    if ip_entry:
        count = ip_entry.count
    else:
        count = 0
    
    return 'Counter value for IP {}: {}'.format(ip_address, count)

@app.route('/view_counter', methods=['GET'])
def view_counter():
    # Get all entries from the Counter table
    entries = Counter.query.all()
    return render_template('counter.html', entries=entries)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
