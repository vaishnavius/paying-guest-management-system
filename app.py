from flask import Flask, render_template, flash, request, redirect, session, jsonify
from models import db, PGRoom, Tenant, Booking, Owner, BookingHistory

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Manvith123@localhost/pg-management'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

@app.route('/')
def home():
    return render_template('home.html')

# Tenant Registration
@app.route('/register_tenant', methods=['GET', 'POST'])
def register_tenant():
    if request.method == 'POST':
        name = request.form['name']
        contact_number = request.form['contact_number']
        email = request.form['email']
        occupation = request.form['occupation']
        password = request.form['password']

        # Check if tenant already exists
        if Tenant.query.filter_by(email=email).first():
            return render_template('register_tenant.html', error="Email already registered!")

        # Register new tenant
        tenant = Tenant(name=name, contact_number=contact_number, email=email, occupation=occupation, password=password)
        db.session.add(tenant)
        db.session.commit()
        return redirect('/login_tenant')

    return render_template('register_tenant.html')

# Tenant Login
@app.route('/login_tenant', methods=['GET', 'POST'])
def login_tenant():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        tenant = Tenant.query.filter_by(email=email).first()
        if tenant and tenant.password == password:
            session['tenant_id'] = tenant.tenant_id
            session['tenant_name'] = tenant.name
            return redirect('/tenant')

        return render_template('login_tenant.html', error="Invalid credentials!")

    return render_template('login_tenant.html')

# Tenant Dashboard
@app.route('/tenant')
def tenant_page():
    if 'tenant_id' not in session:
        return redirect('/login_tenant')  # Redirect if not logged in

    rooms = PGRoom.query.filter_by(availability_status='available').all()
    return render_template('tenant.html', rooms=rooms, tenant_name=session['tenant_name'])

@app.route('/tenant_dashboard')
def tenant_dashboard():
    # Get tenant ID from the session
    current_tenant_id = session.get('tenant_id')
    
    if not current_tenant_id:
        return redirect('/login')  # Redirect to login if tenant is not logged in
    
    # Fetch bookings for the current tenant
    bookings = Booking.query.filter_by(tenant_id=current_tenant_id).all()
    
    # Render the tenant dashboard page with bookings
    return render_template('tenant_dashboard.html', bookings=bookings)

@app.route('/cancel_booking', methods=['POST'])
def cancel_booking():
    # Get booking ID from the form data
    booking_id = request.form.get('booking_id')
    
    # Fetch the booking from the database
    booking = Booking.query.get(booking_id)
    
    if booking:
        current_tenant_id = session.get('tenant_id')
        
        # Ensure the booking belongs to the current tenant
        if booking.tenant_id == current_tenant_id:
            # Delete the booking if it belongs to the current tenant
            db.session.delete(booking)
            db.session.commit()

    # After cancellation, redirect back to the tenant dashboard
    return redirect('/tenant_dashboard')

# Book Room
@app.route('/book_room', methods=['POST'])
def book_room():
    if 'tenant_id' not in session:
        return redirect('/login_tenant')

    room_id = request.form['room_id']
    tenant_id = session['tenant_id']
    check_in_date = request.form['check_in_date']
    check_out_date = request.form['check_out_date']

    room = PGRoom.query.get(room_id)
    if not room or room.availability_status != 'available':
        return jsonify({"error": "Room not available"}), 400

    booking = Booking(
        room_id=room_id,
        tenant_id=tenant_id,
        check_in_date=check_in_date,
        check_out_date=check_out_date,
        status='booked'
    )
    room.availability_status = 'booked'
    db.session.add(booking)
    db.session.commit()
    return redirect('/tenant')

# Tenant Logout
@app.route('/logout_tenant')
def logout_tenant():
    session.pop('tenant_id', None)
    session.pop('tenant_name', None)
    return redirect('/')

# Owner Registration
@app.route('/register_owner', methods=['GET', 'POST'])
def register_owner():
    if request.method == 'POST':
        name = request.form['name']
        contact_number = request.form['contact_number']
        password = request.form['password']

        # Check if owner already exists
        if Owner.query.filter_by(contact_number=contact_number).first():
            return render_template('register_owner.html', error="Contact number already registered!")

        # Register new owner
        owner = Owner(name=name, contact_number=contact_number, password=password)
        db.session.add(owner)
        db.session.commit()
        return redirect('/login_owner')

    return render_template('register_owner.html')

# Owner Login Route
@app.route('/login_owner', methods=['GET', 'POST'])
def login_owner():
    if request.method == 'POST':
        contact_number = request.form['contact_number']
        password = request.form['password']

        # Fetch owner by contact_number
        owner = Owner.query.filter_by(contact_number=contact_number).first()
        
        # Check if owner exists and password is correct
        if owner and owner.password == password:
            session['owner_id'] = owner.owner_id
            session['owner_name'] = owner.name
            return redirect('/add_room')

        return render_template('login_owner.html', error="Invalid credentials!")

    return render_template('login_owner.html')


# Owner # Add Room Route (for Owner)
@app.route('/add_room', methods=['GET', 'POST'])
def add_room():
    if 'owner_id' not in session:
        return redirect('/login_owner')  # Redirect to login if not logged in

    owner_id = session['owner_id']

    # Query to get all rooms owned by the logged-in owner
    rooms = PGRoom.query.filter_by(owner_id=owner_id).all()

    if request.method == 'POST':
        room_type = request.form['room_type']
        price = request.form['price']
        facilities = request.form['facilities']
        location_id = request.form['location_id']

        # Create a new room and add to the database
        room = PGRoom(
            room_type=room_type,
            price=price,
            facilities=facilities,
            location_id=location_id,
            owner_id=owner_id,
            availability_status='available'  # Default status as available
        )
        db.session.add(room)
        db.session.commit()

        flash('Room added successfully!', 'success')  # Flash success message
        return redirect('/add_room')  # Redirect to the add_room page after adding

    return render_template('add_room.html', owner_name=session['owner_name'], rooms=rooms)

# Update Room Route (for Owner)
@app.route('/update_room/<room_id>', methods=['GET', 'POST'])
def update_room(room_id):
    room = PGRoom.query.get_or_404(room_id)

    if request.method == 'POST':
        room.room_type = request.form['room_type']
        room.price = request.form['price']
        room.facilities = request.form['facilities']
        room.location_id = request.form['location_id']
        db.session.commit()

        flash('Room updated successfully!', 'success')  # Flash success message
        return redirect('/add_room')  # Redirect to the add_room page after updating

    return render_template('update_room.html', room=room)

#booking hsitory 
@app.route('/booking-history')
def booking_history():
    try:
        bookings = BookingHistory.query.order_by(BookingHistory.action_date.desc()).all()
        booking_list = []
        
        for booking in bookings:
            booking_list.append({
                'booking_id': booking.booking_id,
                'room_id': booking.room_id,
                'tenant_id': booking.tenant_id,
                'action_type': booking.action_type,
                'action_date': booking.action_date.strftime('%Y-%m-%d %H:%M:%S'),
                'old_status': booking.old_status,
                'new_status': booking.new_status
            })
            
        return render_template('booking_history.html', bookings=booking_list)
        
    except Exception as e:
        return f"An error occurred: {str(e)}"

#Logout Route
@app.route('/logout_owner')
def logout_owner():
    # Remove owner_id and owner_name from session
    session.pop('owner_id', None)
    session.pop('owner_name', None)
    return redirect('/')  # Redirect to home page or login page

if __name__ == '__main__':
    app.run(debug=True)
