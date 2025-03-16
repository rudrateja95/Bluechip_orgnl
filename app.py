from flask import Flask, render_template, request, redirect, url_for, flash, session, Response, send_file, jsonify, make_response
from flask_mail import Mail, Message
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from pytz import timezone
from flask_migrate import Migrate
from sqlalchemy import Column, Integer, String, DateTime, LargeBinary
from sqlalchemy.dialects.mysql import LONGBLOB
from alembic import op
import sqlalchemy as sa
import io
import base64
from io import BytesIO
from flask_socketio import SocketIO, send, emit




app = Flask(__name__)
app.secret_key = 'f3de790ee9c9a9f68f11c45e5d4c9bc4'  # Needed for flashing messages
socketio = SocketIO(app)



# Hardcoded username and password
USERNAME = 'md.bluechip@admin'
PASSWORD = 'Bluechip@1234'

# Configure Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'  
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'brudra95mech@gmail.com'  # Update with environment variable for security
app.config['MAIL_PASSWORD'] = 'xfdkoxbkcholfnbr'  # Update with environment variable for security
app.config['MAIL_DEFAULT_SENDER'] = ''

# MySQL configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:4321@localhost/Student'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Limit to 16 MB


db = SQLAlchemy(app)
migrate = Migrate(app, db)  # Initialize Flask-Migrate here



# Define a function to get the current time in IST
def get_ist_time():
    ist = timezone("Asia/Kolkata")
    return datetime.now(ist)



# Define the Student model
class Student(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)  
    date = db.Column(db.DateTime, default=get_ist_time)
    # Document fields
    country_st = db.Column(db.String(100))
    university_st = db.Column(db.String(100))
    resume = db.Column(LONGBLOB, nullable=True)
    passport_copy = db.Column(LONGBLOB, nullable=True)
    marksheet_10 = db.Column(LONGBLOB, nullable=True)
    marksheet_12 = db.Column(LONGBLOB, nullable=True)
    transcript = db.Column(LONGBLOB, nullable=True)
    pgdm = db.Column(LONGBLOB, nullable=True)
    pdc = db.Column(LONGBLOB, nullable=True) 
    ugc = db.Column(LONGBLOB, nullable=True) 
    lp = db.Column(LONGBLOB, nullable=True)
    sop = db.Column(LONGBLOB, nullable=True)
    lor = db.Column(LONGBLOB, nullable=True)
    el = db.Column(LONGBLOB, nullable=True)
    status = db.Column(db.String(255), nullable=True)  # New status column

    def __repr__(self):
        return f'<Student {self.name}>'
    
    # Define the Agent model
class Agent(db.Model):
    __tablename__ = 'agents'  # Name of the database table
    id = db.Column(db.Integer, primary_key=True)  # Primary key
    name = db.Column(db.String(100), nullable=False)  # Agent's name
    email = db.Column(db.String(120), unique=True, nullable=False)  # Unique email
    phone = db.Column(db.String(15), nullable=False)  # Phone number
    password = db.Column(db.String(255), nullable=False)  # Password (hashed)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())  # Timestamp for when the record was created
    
    adhaar_pasprt = db.Column(db.String(20), nullable=False)  # Aadhar or Passport number
    gst = db.Column(db.String(255), nullable=True)  # GST number
    address = db.Column(db.String(200), nullable=False)  # Agent address
    agents_doc = db.relationship('AgentDoc', back_populates='agent', cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Agent {self.name}>'  # String representation for the model
    
    # Define the Student model
class AgentDoc(db.Model):
    __tablename__ = 'agents_doc'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)  
    date = db.Column(db.DateTime, default=get_ist_time)
    # Document fields
    resume = db.Column(LONGBLOB, nullable=True)
    passport_copy = db.Column(LONGBLOB, nullable=True)
    marksheet_10 = db.Column(LONGBLOB, nullable=True)
    marksheet_12 = db.Column(LONGBLOB, nullable=True)
    transcript = db.Column(LONGBLOB, nullable=True)
    pgdm = db.Column(LONGBLOB, nullable=True)
    pdc = db.Column(LONGBLOB, nullable=True) 
    ugc = db.Column(LONGBLOB, nullable=True) 
    lp = db.Column(LONGBLOB, nullable=True)
    sop = db.Column(LONGBLOB, nullable=True)
    lor = db.Column(LONGBLOB, nullable=True)
    el = db.Column(LONGBLOB, nullable=True)
    status = db.Column(db.String(255), nullable=True)  # New status column
    
    country_agt = db.Column(db.String(100), nullable=False)
    university_agt = db.Column(db.String(100), nullable=False)
    
    agent_id = db.Column(db.Integer, db.ForeignKey('agents.id'), nullable=False)
    
    # Define relationship back to Agent
    agent = db.relationship('Agent', back_populates='agents_doc')

    def __repr__(self):
        return f'<AgentDoc {self.name}>'

class BluechipData(db.Model): 
    __tablename__ = 'bluechip_data'
    id = db.Column(db.Integer, primary_key=True)
    notification = db.Column(db.String(100), nullable=False)  # Text notification
    image = db.Column(LONGBLOB, nullable=True)  # Store image data in binary format
    
    def __repr__(self):
        return f'<BluechipData notification={self.notification}>'
    
# Country model
class Country(db.Model):
    __tablename__ = 'countries'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)  # Unique country name
    universities = db.relationship('University', back_populates='country', cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Country(name={self.name})>"

# University model with fees
class University(db.Model):
    __tablename__ = 'universities'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # University name
    fees = db.Column(LONGBLOB, nullable=True)  # Store fees data in binary format
    country_id = db.Column(db.Integer, db.ForeignKey('countries.id'), nullable=False)  # Foreign key to Country

    country = db.relationship('Country', back_populates='universities')

    def __repr__(self):
        return f"<University(name={self.name}, fees={self.fees}, country={self.country.name})>"
    
 # Chat message model
class ChatMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_type = db.Column(db.String(10), nullable=False)  # 'student' or 'admin'
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<ChatMessage {self.user_type}: {self.message}>'   

# Initialize Mail
mail = Mail(app)

# Initialize the database
with app.app_context():
    #db.drop_all()
    db.create_all() 
    



@app.route('/')
def index():
    # Fetch all notifications from BluechipData
    notifications = BluechipData.query.all()
    return render_template('index.html', notifications=notifications)

@app.route('/add_university', methods=['GET', 'POST'])
def add_university():
    page = request.args.get('page', 1, type=int)  # Get the current page (default is 1)
    
    # Query universities with pagination
    universities = University.query.paginate(page=page, per_page=10, error_out=False)  # Corrected line
    
    if request.method == 'POST':
        # Get form data
        country_name = request.form.get('country_name')
        university_name = request.form.get('university_name')
        fees_image = request.files.get('fees_image')
        
        # Check if the country exists
        country = Country.query.filter_by(name=country_name).first()
        if not country:
            # Create a new country if it does not exist
            country = Country(name=country_name)
            db.session.add(country)
            db.session.commit()
        
        # Check for an existing university in the specified country
        university = University.query.filter_by(name=university_name, country_id=country.id).first()
        if university:
            flash("University already exists in this country.")
            return redirect(url_for('add_university'))
        
        # Process the uploaded image and store it as binary data
        if fees_image:
            fees_data = fees_image.read()  # Read binary data of the image
            new_university = University(name=university_name, fees=fees_data, country_id=country.id)
            db.session.add(new_university)
            db.session.commit()
            flash("University and fees image added successfully!")
            return redirect(url_for('add_university'))

    # Render the form if the request method is GET
    return render_template('add_university.html', universities=universities)


@app.route('/university_fees/<int:university_id>')
def university_fees(university_id):
    university = University.query.get(university_id)
    if not university or not university.fees:
        return "No fees data available for this university."

    # Serve the fees image for inline rendering
    response = make_response(university.fees)
    response.headers.set('Content-Type', 'image/png')  # Change to 'image/jpeg' for JPG files
    response.headers.set(
        'Content-Disposition', f'inline; filename={university.name}_fees.png'  # Adjust file extension
    )
    return response





    

@app.route('/alrt_gllr', methods=['POST', 'GET'])
def alrt_gllr():
    if 'username' not in session:
        return redirect(url_for('login'))  # Redirect to login if not logged in
    
    if request.method == 'POST':
        # Step 1: Clear all old notifications (delete all rows from the table)
        BluechipData.query.delete()
        db.session.commit()

        # Step 2: Add the new notification
        new_notification = request.form['notification']
        notification = BluechipData(notification=new_notification)
        db.session.add(notification)
        db.session.commit()

        flash("Notification updated successfully!", "success")
        return redirect(url_for('alrt_gllr'))  # Redirect back to the page

    # Step 3: Fetch the latest notification to display
    notifications = BluechipData.query.all()
    return render_template('alrt_gllr.html', notifications=notifications)






@app.route('/image/<int:id>')
def image(id):
    image_record = BluechipData.query.get(id)
    if image_record and image_record.image:
        return send_file(BytesIO(image_record.image), mimetype='image/png')  # or 'image/jpeg'
    return "Image not found", 404







@app.route('/agt_register', methods=['POST'])
def agt_register():
    name = request.form.get('name')
    phone = request.form.get('phone')
    email = request.form.get('email')
    adhaar_pasprt = request.form.get('adhaar_pasprt')
    address = request.form.get('address')
    gst = request.form.get('gst')
    password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')

    # Check if passwords match
    if password != confirm_password:
        flash("Passwords do not match.", "danger")
        return redirect(url_for('register_page'))  # Redirect back to registration form

    # Check if email already exists
    existing_agent = Agent.query.filter_by(email=email).first()
    if existing_agent:
        flash("An agent with this email already exists.", "danger")
        return redirect(url_for('register_page'))

    # Hash the password
    hashed_password = generate_password_hash(password)

    # Create new agent
    new_agent = Agent(
        name=name,
        phone=phone,
        email=email,
        adhaar_pasprt=adhaar_pasprt,
        address=address,
        gst=gst,
        password=hashed_password
    )

    # Add to database
    db.session.add(new_agent)
    db.session.commit()
    flash("Agent registered successfully!", "success")

    # Redirect to the bc_admin page
    return redirect(url_for('log2'))

@app.route('/agt_documents', methods=['POST'])
def agt_documents():
    if 'agent_id' not in session:
        flash("You must be logged in to upload documents.", "danger")
        return redirect(url_for('login'))

    agent_id = session['agent_id']
    name = request.form.get('name')
    phone = request.form.get('phone')
    email = request.form.get('email')
    status = request.form.get('status')
    country_agt = request.form.get('country_agt')
    university_agt = request.form.get('university_agt')

    files = {
        'resume': request.files.get('resume'),
        'passport_copy': request.files.get('passport_copy'),
        'marksheet_10': request.files.get('marksheet_10'),
        'marksheet_12': request.files.get('marksheet_12'),
        'transcript': request.files.get('transcript'),
        'pgdm': request.files.get('pgdm'),
        'pdc': request.files.get('pdc'),
        'ugc': request.files.get('ugc'),
        'lp': request.files.get('lp'),
        'sop': request.files.get('sop'),
        'lor': request.files.get('lor'),
        'el': request.files.get('el')
    }

    document_data = {key: file.read() if file else None for key, file in files.items()}

    agent_doc = AgentDoc(
        name=name,
        phone=phone,
        email=email,
        status=status,
        country_agt=country_agt,
        university_agt=university_agt,
        agent_id=agent_id,
        **document_data
    )

    try:
        db.session.add(agent_doc)
        db.session.commit()
        flash("Documents uploaded successfully.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error uploading documents: {str(e)}", "danger")

    return redirect(url_for('agt_upload'))




@app.route('/update_status/<int:student_id>', methods=['POST'])
def update_status(student_id):
    student = Student.query.get_or_404(student_id)
    student.status = request.form['status']
    db.session.commit()
    flash("Status updated successfully!", "success")
    return redirect(url_for('st_documents'))

@app.route('/update_doc_status/<int:doc_id>', methods=['POST'])
def update_doc_status(doc_id):
    doc = AgentDoc.query.get_or_404(doc_id)
    doc.status = request.form['status']
    db.session.commit()
    flash("Document status updated successfully!", "success")
    return redirect(url_for('st_documents'))



@app.route('/verify_reset_request', methods=['POST'])
def verify_reset_request():
    email = request.form['email']
    phone = request.form['phone']
    
    # Check if a student exists with the provided email and phone number
    student = Student.query.filter_by(email=email, phone=phone).first()
    
    if student:
        session['student_id'] = student.id  # Store student ID in session for the reset
        flash("Verification successful. You may reset your password.", "success")
        return redirect(url_for('reset_password'))
    else:
        flash("Verification failed. Please check your email and phone number.", "danger")
        return redirect(url_for('reset_request'))
    
@app.route('/verify_agnt_request', methods=['GET', 'POST'])
def verify_agnt_request():
    if request.method == 'POST':
        email = request.form['email']
        phone = request.form['phone']
        
        # Check if an agent exists with the provided email and phone number
        agent = Agent.query.filter_by(email=email, phone=phone).first()
        
        if agent:
            session['agent_id'] = agent.id  # Store agent ID in session for the reset
            flash("Verification successful. You may reset your password.", "success")
            return redirect(url_for('reset_agent_password'))  # Redirect to password reset page
        else:
            flash("Verification failed. Please check your email and phone number.", "danger")
            return redirect(url_for('verify_agnt_request'))  # Redirect back to verification
        
    return render_template('verify_agnt.html')  # Render the verification form

@app.route('/reset_agent_password', methods=['GET', 'POST'])
def reset_agent_password():
    if 'agent_id' not in session:
        flash("You need to verify your account first.", "warning")
        return redirect(url_for('verify_agnt_request'))
    
    if request.method == 'POST':
        new_password = request.form.get('password')
        agent_id = session['agent_id']
        
        agent = Agent.query.get(agent_id)
        agent.password = generate_password_hash(new_password)  # Hash the new password
        db.session.commit()
        
        flash("Your password has been updated successfully.", "success")
        session.pop('agent_id', None)  # Clear the session
        return redirect(url_for('log2'))  # Redirect to the agent login page
    
    return render_template('reset_agent_password.html')  # Render password update form
    
@app.route('/reset_request', methods=['GET', 'POST'])
def reset_request():
    if request.method == 'POST':
        email = request.form.get('email')
        phone = request.form.get('phone')
        # Find the student by email and phone number
        student = Student.query.filter_by(email=email, phone=phone).first()
        
        if student:
            session['student_id'] = student.id  # Store student ID in session for the reset
            flash("Verification successful. You may reset your password.", "success")
            return redirect(url_for('update_password'))  # Redirect to password update
        else:
            flash("Verification failed. Please check your email and phone number.", "danger")
            return redirect(url_for('reset_request'))  # Redirect back to reset request
    return render_template('reset_request.html')  # Render reset request form

@app.route('/update_password', methods=['POST', 'GET'])
def update_password():
    if 'student_id' not in session:
        flash("You need to request a password reset first.", "danger")
        return redirect(url_for('reset_request'))  # Ensure user is logged in for the reset

    student_id = session['student_id']  # Retrieve student ID from session
    student = Student.query.get(student_id)

    if student is None:
        flash("Student not found. Please request a password reset again.", "danger")
        session.pop('student_id')  # Clear session
        return redirect(url_for('reset_request'))  # Redirect to reset request page

    if request.method == 'POST':
        new_password = request.form.get('password')
        if new_password:  # Check if new password is not empty
            student.password = generate_password_hash(new_password)  # Hash the new password
            db.session.commit()  # Commit changes to the database
            flash("Your password has been updated successfully!", "success")
            session.pop('student_id')  # Clear student ID from session
            return redirect(url_for('log1'))  # Redirect to login
        else:
            flash("Password cannot be empty.", "danger")

    return render_template('reset_password.html')

@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    if 'student_id' not in session:
        flash("You need to verify your identity first.", "danger")
        return redirect(url_for('reset_request'))

    student_id = session['student_id']
    student = Student.query.get(student_id)

    if request.method == 'POST':
        new_password = request.form.get('password')  # Use get() to avoid KeyError
        
        # Check if the new password is not empty
        if new_password:
            student.password = generate_password_hash(new_password)  # Hash the new password
            db.session.commit()
            flash("Your password has been reset successfully!", "success")
            session.pop('student_id')  # Clear the session
            return redirect(url_for('log1'))  # Redirect to login page
        else:
            flash("Password cannot be empty.", "danger")
    
    return render_template('reset_password.html')  # Render the password reset for





@app.route('/upload', methods=['POST'])
def upload_documents():
    if 'student_id' in session:
        student_id = session['student_id']
        student = Student.query.get(student_id)

        if student:
            # Get country and university from form data
            country_st = request.form.get('country_st')
            university_st = request.form.get('university_st')

            # Ensure the data is being correctly received
            print(f"Received country: {country_st}, university: {university_st}")

            # Update the student model with the selected values
            student.country_st = country_st
            student.university_st = university_st

            # Handle document uploads as before
            resume_file = request.files.get('resume')
            if resume_file:
                resume_content = resume_file.read()
                student.resume = resume_content

            passport_file = request.files.get('passport_copy')
            if passport_file:
                passport_content = passport_file.read()
                student.passport_copy = passport_content

            marksheet_10_file = request.files.get('marksheet_10')
            if marksheet_10_file:
                marksheet_content = marksheet_10_file.read()
                student.marksheet_10 = marksheet_content

            marksheet_12_file = request.files.get('marksheet_12')
            if marksheet_12_file:
                marksheet_content = marksheet_12_file.read()
                student.marksheet_12 = marksheet_content

            transcript_file = request.files.get('transcript')
            if transcript_file:
                transcript_content = transcript_file.read()
                student.transcript = transcript_content

            pgdm_file = request.files.get('pgdm')
            if pgdm_file:
                pgdm_content = pgdm_file.read()
                student.pgdm = pgdm_content

            pdc_file = request.files.get('pdc')
            if pdc_file:
                pdc_content = pdc_file.read()
                student.pdc = pdc_content

            ugc_file = request.files.get('ugc')
            if ugc_file:
                ugc_content = ugc_file.read()
                student.ugc = ugc_content

            lp_file = request.files.get('lp')
            if lp_file:
                lp_content = lp_file.read()
                student.lp = lp_content

            sop_file = request.files.get('sop')
            if sop_file:
                sop_content = sop_file.read()
                student.sop = sop_content

            lor_file = request.files.get('lor')
            if lor_file:
                lor_content = lor_file.read()
                student.lor = lor_content

            el_file = request.files.get('el')
            if el_file:
                el_content = el_file.read()
                student.el = el_content

            # Commit changes to the database
            db.session.commit()
            flash("Documents uploaded successfully!", "success")
        else:
            flash("Student not found!", "danger")
    else:
        flash("No student ID in session!", "danger")

    return redirect(url_for('adm_student'))


    
@app.route('/view_document/<string:document_type>/<int:student_id>')
def view_document(document_type, student_id):
    # Get the student by ID
    student = Student.query.get(student_id)
    if not student:
        flash("Student not found!", "danger")
        return redirect(url_for('bc_admin'))

    # Map document types to attributes
    document_mapping = {
        'resume': student.resume,
        'passport': student.passport_copy,
        'marksheet_10': student.marksheet_10,
        'marksheet_12': student.marksheet_12,
        'transcript': student.transcript,
        'pgdm': student.pgdm,
        'pdc': student.pdc,
        'ugc': student.ugc,
        'lp': student.lp,
        'sop': student.sop,
        'lor': student.lor,
        'el': student.el
    }

    # Get the document content and set filename and mimetype
    document_content = document_mapping.get(document_type)
    if not document_content:
        flash("Document not found!", "danger")
        return redirect(url_for('bc_admin'))

    # Set filename and mimetype based on document type
    filename = f"{document_type}.pdf"  # Assuming all files are PDF
    mimetype = 'application/pdf'

    # Create a response to view the document inline
    response = Response(document_content, mimetype=mimetype)
    response.headers['Content-Disposition'] = f'inline; filename={filename}'
    return response


@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/canada')
def canada():
    return render_template('canada.html')

@app.route('/Australia')
def Australia():
    return render_template('Australia.html')

@app.route('/Europe')
def Europe():
    return render_template('Europe.html')

@app.route('/poland')
def poland():
    return render_template('poland.html')

@app.route('/Germani_web')
def Germani_web():
    return render_template('Germani_web.html')

@app.route('/Turkey')
def Turkey():
    return render_template('Turkey.html')

@app.route('/karnataka')
def karnataka():
    return render_template('karnataka.html')

@app.route('/tamilnadu')
def tamilnadu():
    return render_template('tamilnadu.html')

@app.route('/switzerland')
def switzerland():
    return render_template('switzerland.html')

@app.route('/france')
def france():
    return render_template('france.html')

@app.route('/hungary')
def hungary():
    return render_template('hungary.html')

@app.route('/london')
def london():
    return render_template('london.html')

@app.route('/agent_register')
def agent_register():
    return render_template('agent_register.html')

@app.route('/services')
def services():
    return render_template('services.html')

@app.route('/gallery')
def gallery():
    images = BluechipData.query.all()
    return render_template('gallery.html', images=images)



@app.template_filter('b64encode')
def b64encode_filter(data):
    return base64.b64encode(data).decode('utf-8')

@app.route('/mbbs_pg')
def mbbs_pg():
    return render_template('mbbs_pg.html')

@app.route('/malta')
def malta():
    return render_template('malta.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        select1 = request.form['select1']
        message = request.form['message']
        
        # Create the email message
        msg = Message('New lead From Websites',
                      recipients=['rudra95mech@gmail.com'])  # Change to the recipient's email
        msg.body = f"Name: {name}\nEmail: {email}\nPhone: {phone}\nSelection: {select1}\nMessage: {message}"
        
        try:
            mail.send(msg)
            flash('Email sent successfully!', 'success')
        except Exception as e:
            flash(f'Failed to send email: {str(e)}', 'danger')
        
        return redirect(url_for('contact'))

    return render_template('contact.html')

@app.route('/mbbs')
def mbbs():
    return render_template('mbbs.html')

@app.route('/pg')
def pg():
    return render_template('pg.html')

@app.route('/usa')
def usa():
    return render_template('usa.html')

@app.route('/newzealand')
def newzealand():
    return render_template('newzealand.html')

@app.route('/ielts')
def ielts():
    return render_template('ielts.html')

@app.route('/tofel')
def tofel():
    return render_template('tofel.html')

@app.route('/pte')
def pte():
    return render_template('pte.html')

@app.route('/oet')
def oet():
    return render_template('oet.html')

@app.route('/cbt')
def cbt():
    return render_template('cbt.html')

@app.route('/dha')
def dha():
    return render_template('dha.html')

@app.route('/haad')
def haad():
    return render_template('haad.html')

@app.route('/prometric')
def prometric():
    return render_template('prometric.html')

@app.route('/emric')
def emric():
    return render_template('emric.html')

@app.route('/dualingo')
def dualingo():
    return render_template('dualingo.html')

@app.route('/germani')
def germani():
    return render_template('germani.html')

@app.route('/spain')
def spain():
    return render_template('spain.html')

@app.route('/mipr')
def mipr():
    return render_template('mipr.html')

@app.route('/tsampi')
def tsampi():
    return render_template('tsampi.html')

@app.route('/fmiph')
def fmiph():
    return render_template('fmiph.html')



@app.route('/log_sign')
def log_sign():
    return render_template('log_sign.html')

@app.route('/usmle')
def usmle():
    return render_template('usmle.html')

@app.route('/CARMS')
def CARMS():
    return render_template('CARMS.html')

@app.route('/spainpg')
def spainpg():
    return render_template('spainpg.html')

@app.route('/bc_admin', methods=['GET'])
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))  # Redirect to login if not logged in

    # Define the number of items per page
    per_page = 10

    # Get the page number from the URL query parameters
    page = request.args.get('page', 1, type=int)

    # Paginate the students, agents, and countries queries
    students = Student.query.paginate(page=page, per_page=per_page, error_out=False)
    agents = Agent.query.paginate(page=page, per_page=per_page, error_out=False)
    paginated_countries = Country.query.paginate(page=page, per_page=per_page, error_out=False)

    # Query for other statistics (count totals and load all country-university relationships)
    total_students = Student.query.count()
    total_agents = Agent.query.count()
    total_countries = Country.query.count()
    total_universities = University.query.count()
    countries_with_universities = Country.query.options(db.joinedload(Country.universities)).all()

    return render_template(
        'bc_admin.html',
        students=students.items,
        agents=agents.items,
        countries=paginated_countries.items,
        total_students=total_students,
        total_agents=total_agents,
        total_countries=total_countries,
        total_universities=total_universities,
        countries_with_universities=countries_with_universities,
        page=page,
        total_pages=max(students.pages, agents.pages, paginated_countries.pages)
    )





@app.route('/log')
def log():
    return render_template('log.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Check if the credentials match
        if username == USERNAME and password == PASSWORD:
            session['username'] = username  # Save user in session
            return redirect(url_for('dashboard'))
        else:
           return render_template('log.html', error="Invalid credentials, please try again!")
    
    return render_template('log.html')

@app.route('/log1', methods=['GET', 'POST'])
def log1():
    if request.method == 'POST':
        email = request.form['username']  # Use 'username' for email field
        password = request.form['password']

        # Query database to find the student
        student = Student.query.filter_by(email=email).first()

        if student and check_password_hash(student.password, password):
            session['student_id'] = student.id  # Save student ID in session
            flash('Login successful!', 'success')
            return redirect(url_for('adm_student'))  # Redirect to student dashboard
        else:
            flash('Invalid credentials, please try again.', 'danger')
    
    return render_template('log1.html')





@app.route('/adm_student')
def adm_student():
    if 'student_id' not in session:  # Check if student_id is in session
        return redirect(url_for('log1'))  # Redirect to login if not logged in

    student_id = session['student_id']  # Get student ID from session
    student = Student.query.get(student_id)  # Retrieve the student from the database

    # Check if the student was found
    if not student:
        flash("Student not found.", "danger")
        return redirect(url_for('log1'))
    
        # Fetch countries from the database
    countries = Country.query.all()



    # Render the adm_student.html page with the student, country, and university data
    return render_template('adm_student.html', student=student, countries=countries,user_type='student')

@app.route('/get_universities/<int:country_id>')
def get_universities(country_id):
    universities = University.query.filter_by(country_id=country_id).all()
    university_list = [{"id": uni.id, "name": uni.name} for uni in universities]
    return jsonify(university_list)






@app.route('/log2')
def log2():
    return render_template('log2.html')

@app.route('/agent_login', methods=['GET', 'POST'])
def agent_login():
    if request.method == 'POST':
        username_or_email = request.form['username']
        password = request.form['password']
        


        # Query the database to check for the agent by username or email
        agent = Agent.query.filter((Agent.email == username_or_email) | (Agent.name == username_or_email)).first()

        if agent and check_password_hash(agent.password, password):
            # Password is correct; log the agent in
            session['agent_id'] = agent.id  # Store agent ID in session
            flash("Login successful!", "success")
            return redirect(url_for('agent_admin'))  # Redirect to the admin dashboard or agent page
        else:
            flash("Invalid username or password.", "danger")

    # GET request - render the login form
    return render_template('log2.html')



@app.route('/agent_admin')
def agent_admin():
    if 'agent_id' not in session:
        flash("Please log in to access this page.", "warning")
        return redirect(url_for('agent_login'))

    agent_id = session['agent_id']
    agent = Agent.query.get(agent_id)  # Retrieve the agent data from the database
    
    # Pagination logic
    page = request.args.get('page', 1, type=int)  # Get the current page number (default is 1)
    per_page = 10  # Number of records per page
    agents_doc = AgentDoc.query.filter_by(agent_id=agent_id).paginate(page=page, per_page=per_page, error_out=False)

    return render_template('agent_admin.html', agent=agent, agents_doc=agents_doc)


@app.route('/agt_upload')
def agt_upload():
    if 'agent_id' not in session:
        flash("Please log in to access this page.", "warning")
        return redirect(url_for('agent_login'))
    
    agent_id = session['agent_id']
    agent = Agent.query.get(agent_id)  # Retrieve the agent data from the database
    countries = Country.query.all()
    return render_template('agt_upload.html', agent=agent, countries=countries)

@app.route('/agent_reg')
def agent():
    return render_template('agent_reg.html')

@app.route('/registration')
def registration():
    return render_template('registration.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Get form data
        name = request.form['username']
        phone = request.form['phone']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # Check if passwords match
        if password != confirm_password:
            flash("Passwords do not match!", "danger")
            return redirect(url_for('register'))

        # Check if email already exists
        existing_user = Student.query.filter_by(email=email).first()
        if existing_user:
            flash("Email already registered. Please log in.", "danger")
            return redirect(url_for('register'))

        # Hash password
        hashed_password = generate_password_hash(password)

        # Create new student and add to the database
        new_student = Student(
            name=name,
            phone=phone,
            email=email,
            password=hashed_password,
            date=get_ist_time()
        )
        db.session.add(new_student)
        db.session.commit()
        
        flash("Registration successful!", "success")
        return redirect(url_for('log1'))  # Redirect to login page after registration
    
    return render_template('registration.html')





@app.route('/st_documents')
def st_documents():
    if 'username' not in session:
        return redirect(url_for('login'))  # Redirect to login if not logged in

    # Pagination for students
    page = request.args.get('page', 1, type=int)  # Get the current page number (default is 1)
    per_page = 10  # Number of records per page
    students = Student.query.paginate(page=page, per_page=per_page, error_out=False)  # Corrected pagination call
    total_students = Student.query.count()

    # Pagination for agent documents
    agent_docs_page = request.args.get('agent_docs_page', 1, type=int)  # Get the current page for agent documents
    agent_docs = AgentDoc.query.paginate(page=agent_docs_page, per_page=per_page, error_out=False)  # Corrected pagination call

    return render_template('st_documents.html', students=students, total_students=total_students, agent_docs=agent_docs,user_type='admin')


@app.route('/view_doc/<int:doc_id>/<doc_type>')
def view_doc(doc_id, doc_type):
    # Fetch the agent document by ID
    doc = AgentDoc.query.get_or_404(doc_id)
    
    # Retrieve the document data by type
    document_data = getattr(doc, doc_type, None)
    
    if document_data:
        # Return the document content directly to view in the browser
        return Response(document_data, mimetype='application/pdf')
    else:
        flash("Document not found.", "danger")
        return redirect(url_for('bc_admin'))

@app.route('/status')
def status():
    if 'student_id' not in session:  # Check if student_id is in session
        
        return redirect(url_for('log1'))  # Redirect to login if not logged in

    student_id = session['student_id']  # Get student ID from session
    student = Student.query.get(student_id)  # Retrieve the student from the database

    # Check if the student was found
    if not student:
        flash("Student not found.", "danger")
        return redirect(url_for('log1'))
    
    return render_template('status.html', student=student, user_type='student')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/logout_st')
def logout_st():
    session.pop('student_password', None)  # Remove only the student password
    flash("You have been logged out.", "info")
    return redirect(url_for('log1'))

# Optional: Add a logout route to clear the session
@app.route('/logout_agent')
def logout_agent():
    session.pop('agent_password', None)
    flash("Logged out successfully.", "success")
    return redirect(url_for('agent_login'))


# Handle incoming messages
@socketio.on('send_message')
def handle_send_message(data):
    print(f"Received message: {data}")  # Debugging
    user_type = data.get('user_type')
    message = data.get('message')
    timestamp = datetime.utcnow()
    
    # Debug logs
    print(f"user_type: {user_type}, message: {message}, timestamp: {timestamp}")
    
    # Save the message to the database
    chat_message = ChatMessage(user_type=user_type, message=message, timestamp=timestamp)
    db.session.add(chat_message)
    db.session.commit()
    
    # Broadcast the message
    emit('receive_message', {
        'user_type': user_type,
        'message': message,
        'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S')
    }, broadcast=True)


if __name__ == '__main__':
    socketio.run(app, debug=True)
