from flask import render_template, redirect, url_for, request, flash, Response, session, send_from_directory
from main import app
from applications.model import *
from datetime import datetime
from sqlalchemy import or_, and_, func
import io
import matplotlib.pyplot as plt
import matplotlib
import os
matplotlib.use('Agg')


@app.route('/customer/login', methods=['GET', 'POST'])
def customer_login():
    if request.method == "GET":
        return render_template('customer_login.html')

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        customer = Customer.query.filter_by(username=username).first() 
      
        if customer and customer.password == password:
            if customer.status == "active":
                return redirect(f'/customer/dashboard/{customer.customer_id}')
            else:
                flash('Your account is blocked')
        else:
            flash('Invalid username or password')
    
    return render_template('customer_login.html')


@app.route('/customer/signup', methods=['GET', 'POST'])
def customer_signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        name = request.form['name']
        email = request.form['email']
        phnum = request.form['phnum']
        add = request.form['add']



        if Customer.query.filter_by(username=username).first():
            flash('Username already exists')
        elif Customer.query.filter_by(email=email).first():
            flash('Email already exists')
        else:
            new_user = Customer(username=username, password=password, name = name, address = add, email = email, phone = phnum)
            db.session.add(new_user)
            db.session.commit()
            flash('Account created')
            return redirect(url_for('customer_login'))
    
    return render_template('customer_signup.html')


@app.route('/customer/profile/<int:customer_id>', methods=['GET', 'POST'])
def edit_cust_profile(customer_id):
    customer = db.session.query(Customer).filter_by(customer_id=customer_id).first()
    if request.method == 'POST':
        customer.password = request.form['password']
        customer.name = request.form['name']
        customer.email = request.form['email']
        customer.phone = request.form['phone']
        customer.address = request.form['address']

        db.session.commit()
        flash('Profile updated')
        return redirect(f'/customer/dashboard/{customer_id}')
    
    return render_template('edit_cust_profile.html', customer = customer)


@app.route('/professional/login', methods=['GET', 'POST'])
def professional_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        professional = Professional.query.filter_by(username=username).first()
        if professional and professional.password ==password:
            if professional.status == 'active':
                if professional.approved == 'Yes':
                    return redirect(f"/professional/dashboard/{professional.professional_id}")
                else:
                    flash('Your profile is not approved')
            else:
                flash('Your account is blocked')
        else:
            flash('Invalid username or password')
    return render_template('professional_login.html')


@app.route('/professional/signup', methods=['GET', 'POST'])
def professional_signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        service_id = request.form['service']
        experience = request.form['experience']
        file = request.files.get('proof')

        

        if Professional.query.filter_by(username=username).first():
            flash('Username already exists')

        elif Professional.query.filter_by(email=email).first():
            flash('Email already exists')
        else:

            if file:
                filename = username + file.filename
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
            else:
                filename = None

            new_professional = Professional(
                username=username, password=password, name=name,
                email=email, phone=phone, service_id=service_id,
                experience=experience, approved = False, proof = filename
            )
            db.session.add(new_professional)
            db.session.commit()
            flash('Account created. Please wait for approval')
            return redirect('/professional/login')
    services = Service.query.all()
    return render_template('professional_signup.html', services = services)


@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if "123" ==password and username == 'ad':
                return redirect('/admin/dashboard')
            
        else:
            flash('Invalid username or password')
    return render_template('admin_login.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    #professionals = Professional.query.all()
    customers = Customer.query.all()
    services = Service.query.all()

    professionals = db.session.query(
        Professional.professional_id,
        Professional.username,
        Professional.name,
        Professional.email,
        Professional.phone,
        Professional.approved,
        Professional.status,
        Professional.experience,
        Professional.proof,
        Service.name.label('service_name') 
    ).join(Service, Service.service_id == Professional.service_id).all()
    
    requests = db.session.query(
        ServiceRequest.date_of_completion,
        ServiceRequest.date_of_request,
        ServiceRequest.request_id,
        ServiceRequest.service_status,
        Customer.username.label('customer_username'),
        Professional.username.label('professional_username'),
        Service.name.label('service_name'),
    ).join(
        Service, Service.service_id == ServiceRequest.service_id,        
        ).join(
            Customer, Customer.customer_id == ServiceRequest.customer_id,
        ).join(
            Professional, Professional.professional_id == ServiceRequest.professional_id,
        ).all()
        
    return render_template('admin_dash.html', professionals=professionals, customers=customers, services=services, requests = requests)

@app.route('/admin/block_cust/<int:user_id>')
def block_cust(user_id):
    user = Customer.query.get(user_id)
    if user:
        user.status = 'blocked'
        db.session.commit()
    return redirect('/admin/dashboard')

@app.route('/admin/unblock_cust/<int:user_id>')
def unblock_cust(user_id):
    user = Customer.query.get(user_id)
    if user:
        user.status = 'active'
        db.session.commit()
    return redirect('/admin/dashboard')

@app.route('/admin/unblock_prof/<int:user_id>')
def unblock_prof(user_id):
    user = Professional.query.get(user_id)
    if user:    
        user.status = 'active'
        db.session.commit()
    return redirect('/admin/dashboard')

@app.route('/admin/block_prof/<int:user_id>')
def block_prof(user_id):
    user = Professional.query.get(user_id)
    if user:
        user.status = 'blocked'
        db.session.commit()
    return redirect('/admin/dashboard')


@app.route('/admin/approve_professional/<int:user_id>')
def approve_user(user_id):
    user = Professional.query.get(user_id) 
    if user:
        user.approved = "Yes"
        db.session.commit()
    return redirect('/admin/dashboard')

@app.route('/admin/unapprove_professional/<int:user_id>')
def unapprove_user(user_id):
    user = Professional.query.get(user_id) 
    if user:
        user.approved = "No"
        db.session.commit()
    return redirect('/admin/dashboard')



@app.route('/admin/search', methods=['GET', 'POST'])
def admin_search():
    query = request.form.get('query', '').strip()  
    date_filter = request.form.get('date_filter', '')

    results = {
        "customers": [],
        "professionals": [],
        "services": [],
        "requests": []
    }

    if query:
        if not date_filter:
            results["customers"] = Customer.query.filter(
                    or_(
                        Customer.name.ilike(f"%{query}%"),
                        Customer.username.ilike(f"%{query}%"),
                        Customer.phone.ilike(f"%{query}%"),
                        Customer.email.ilike(f"%{query}%"),
                        Customer.address.ilike(f"%{query}%")
                    )
                    ).all()

            results["professionals"] = db.session.query(
                        Professional.professional_id,
                        Professional.username,
                        Professional.name,
                        Professional.email,
                        Professional.phone,
                        Professional.approved,
                        Professional.status,
                        Professional.proof,
                        Professional.experience,
                        Service.name.label('service_name')
                            ).join(Service, Service.service_id == Professional.service_id
                                ).filter(
                                        or_(
                                            Professional.name.ilike(f"%{query}%"),
                                            Professional.username.ilike(f"%{query}%"),
                                            Professional.phone.ilike(f"%{query}%"),
                                            Professional.email.ilike(f"%{query}%")
                                        )
                                    ).all()

            results["services"] = Service.query.filter(
                    or_(
                        Service.name.ilike(f"%{query}%"),
                        Service.description.ilike(f"%{query}%")
                    )
                ).all()

    if query or date_filter:
        results["requests"] = db.session.query(
                    ServiceRequest.date_of_completion,
                    ServiceRequest.date_of_request,
                    ServiceRequest.request_id,
                    ServiceRequest.service_status,
                    Customer.username.label('customer_username'),
                    Professional.username.label('professional_username'),
                    Service.name.label('service_name')
                ).join(
                    Service, Service.service_id == ServiceRequest.service_id
                ).join(
                    Customer, Customer.customer_id == ServiceRequest.customer_id
                ).join(
                    Professional, Professional.professional_id == ServiceRequest.professional_id
                ).filter(
                    and_(
                        or_(
                            ServiceRequest.service_status.ilike(f"%{query}%") if query else True,
                            Service.name.ilike(f"%{query}%") if query else True,
                            Customer.username.ilike(f"%{query}%") if query else True,
                            Professional.username.ilike(f"%{query}%") if query else True,
                        ),
                        or_(
                            ServiceRequest.date_of_request == date_filter if date_filter else True,
                            ServiceRequest.date_of_completion == date_filter if date_filter else True
                        )
                    )
                ).all()
    if not query:
        query = "Search"
    return render_template('admin_search.html', query=query, results=results)


@app.route('/admin/summary')
def admin_summary():
    total_customers = Customer.query.count()
    total_professionals = Professional.query.count()
    total_services = Service.query.count()
    total_requests = ServiceRequest.query.count()

    status_counts = db.session.query(
            ServiceRequest.service_status,
            func.count(ServiceRequest.request_id).label('count')
        ).group_by(ServiceRequest.service_status).all()


    overall_rating = db.session.query(
            func.avg(Reviews.rating)
        ).join(
            ServiceRequest, ServiceRequest.request_id == Reviews.request_id
        ).filter(
            Reviews.rating.isnot(None)
        ).scalar()
    
    overall_rating = db.session.query(
            func.avg(Reviews.rating)
        ).filter(
            Reviews.rating.isnot(None)
        ).scalar()
    status_counts = [(row.service_status, row.count) for row in status_counts]
    session['status_counts'] = status_counts


    return render_template('admin_summary.html', customers=total_customers, professionals=total_professionals,
                           services=total_services, requests=total_requests, status_counts = status_counts, overall_rating = overall_rating)


@app.route('/admin/create_service', methods=['GET', 'POST'])
def create_service():
    if request.method == 'POST':
        try:
            name = request.form['name']
            base_price = int(request.form['base_price'])
            time_required = int(request.form['time_required'])
            description = request.form['description']

            new_service = Service(name=name, base_price=base_price, time_required=time_required, description=description)

            db.session.add(new_service)
            db.session.commit()

            flash('Service added')
            return redirect('/admin/dashboard')
        
        except Exception as e:
            db.session.rollback()
            flash(f'Error {e}')
            return redirect('/admin/create_service')
    return render_template('create_service.html')


@app.route('/admin/delete_service/<int:service_id>')
def delete_service(service_id):
    service = Service.query.get(service_id)
    if service:
        db.session.delete(service)
        db.session.commit()
    return redirect('/admin/dashboard')

@app.route('/admin/update_service/<int:service_id>', methods=['GET', 'POST'])
def update_service(service_id):
    service = Service.query.get(service_id)
    
    if request.method == 'POST':
        try:
            service.name = request.form['name']
            service.base_price = int(request.form['base_price'])
            service.time_required = int(request.form['time_required'])
            service.description = request.form['description']

            db.session.commit()
            flash('Service updated')
            return redirect('/admin/dashboard')

        except Exception as e:
            db.session.rollback()
            flash(f'Error {e}')
            return redirect(f'/admin/update_service/{service_id}')
    
    return render_template('update_service.html', service=service)


@app.route('/professional/dashboard/<int:professional_id>', methods=['GET', 'POST'])
def prof_dashboard(professional_id):

    professional = db.session.query(
            Professional.professional_id,
            Professional.username,
            Professional.name,
            Professional.password,
            Professional.email,
            Professional.phone,
            Professional.approved,
            Professional.status,
            Professional.experience,
            Service.name.label('service_name') 
        ).join(Service, Service.service_id == Professional.service_id
               ).filter(Professional.professional_id == professional_id).first()
    
    today_date = datetime.now().strftime('%Y-%m-%d')
    todays_services = db.session.query(
        ServiceRequest.date_of_completion,
        ServiceRequest.date_of_request,
        ServiceRequest.request_id,
        ServiceRequest.location,
        Customer.name.label('cust_name'),
        Service.name.label('service_name'),
    ).join(
        Service, Service.service_id == ServiceRequest.service_id,
    ).join(
        Customer, Customer.customer_id == ServiceRequest.customer_id,
    ).filter(
        ServiceRequest.professional_id == professional_id,  
        ServiceRequest.service_status == 'accepted',
        #ServiceRequest.date_of_request == today_date
    ).all()    

    closed_services = db.session.query(
        ServiceRequest.date_of_completion,
        ServiceRequest.date_of_request,
        ServiceRequest.request_id,
        ServiceRequest.location,
        Customer.name.label('cust_name'),
        Service.name.label('service_name'),
    ).join(
        Service, Service.service_id == ServiceRequest.service_id,
    ).join(
        Customer, Customer.customer_id == ServiceRequest.customer_id,
    ).filter(
        ServiceRequest.professional_id == professional_id,  
        ServiceRequest.service_status == 'closed',
    ).all()
  
    requested_services = db.session.query(
        ServiceRequest.date_of_completion,
        ServiceRequest.date_of_request,
        ServiceRequest.request_id,
        ServiceRequest.location,
        Customer.name.label('cust_name'),
        Service.name.label('service_name'),
    ).join(
        Service, Service.service_id == ServiceRequest.service_id,
    ).join(
        Customer, Customer.customer_id == ServiceRequest.customer_id,
    ).filter(
        ServiceRequest.professional_id == professional_id,  
        ServiceRequest.service_status == 'requested',
    ).all()
    
    other_services = db.session.query(
        ServiceRequest.date_of_completion,
        ServiceRequest.date_of_request,
        ServiceRequest.request_id,
        ServiceRequest.location,
        Customer.name.label('cust_name'),
        Service.name.label('service_name'),
    ).join(
        Service, Service.service_id == ServiceRequest.service_id,
    ).join(
        Customer, Customer.customer_id == ServiceRequest.customer_id,
    ).filter(
        ServiceRequest.professional_id == professional_id,
        ServiceRequest.service_status == 'rejected',
    ).all()

    return render_template( 'prof_dashboard.html', professional=professional, todays_services=todays_services, closed_services=closed_services, requested_services=requested_services, other_services = other_services )


@app.route('/professional/profile/<int:professional_id>', methods=['GET', 'POST'])
def edit_professional_profile(professional_id):
    professional = Professional.query.get(professional_id)
    service_name = (
        db.session.query(Service.name.label('service_name'))
        .join(Professional, Service.service_id == Professional.service_id)
        .filter(Professional.professional_id == professional_id)
        .first()
    )

    if request.method == 'POST':
        professional.name = request.form['name']
        professional.password = request.form['password']
        professional.email = request.form['email']
        professional.phone = request.form['phone']
        professional.experience = request.form['experience']
        professional.service_id = request.form['service']

        db.session.commit()
        return redirect(f'/professional/dashboard/{professional_id}')

    services = Service.query.all()
    return render_template('edit_professional_profile.html', professional=professional, services = services, service_name = service_name)

@app.route("/customer/dashboard/<int:customer_id>", methods = ["get", "post"])
def cust_dashboard(customer_id):
    customer = Customer.query.get(customer_id)
    current_services = db.session.query(
        ServiceRequest.request_id,
        ServiceRequest.service_status,
        Service.name.label('service_name'),
        ServiceRequest.date_of_request,
        Professional.name.label('professional_name'),
        Professional.phone.label('professional_phone')
    ).join(Service, Service.service_id == ServiceRequest.service_id
           ).join(
                Professional, ServiceRequest.professional_id == Professional.professional_id
            ).filter(
                    ServiceRequest.customer_id == customer_id,
                    ServiceRequest.service_status != 'closed',
                    ServiceRequest.service_status != 'rejected'
                ).all()

    service_history = db.session.query(
        ServiceRequest.request_id,
        ServiceRequest.service_status,
        Service.name.label('service_name'),
        ServiceRequest.date_of_request,
        ServiceRequest.date_of_completion,
        Professional.name.label('professional_name'),
        Professional.phone.label('professional_phone')
    ).join(Service, Service.service_id == ServiceRequest.service_id
           ).join(
                Professional, ServiceRequest.professional_id == Professional.professional_id
            ).filter(
                    ServiceRequest.customer_id == customer_id,
                    ServiceRequest.service_status != 'accepted',
                    ServiceRequest.service_status != 'requested'
                ).all()

    return render_template("customer_dashboard.html", customer = customer, current_services=current_services, service_history=service_history)



@app.route('/customer/book_service/<int:customer_id>', methods=['GET', 'POST'])
def book_service(customer_id):
    if request.method == 'POST':
        search_query = request.form.get('search')
        services = Service.query.filter(
            Service.name.ilike(f'%{search_query}%') |
            Service.description.ilike(f'%{search_query}%')
        ).all()
        return render_template('book_service.html', services=services, customer_id=customer_id)

    return render_template('book_service.html',customer_id = customer_id)


@app.route('/customer/<int:customer_id>/service/<int:service_id>', methods=['GET', 'POST'])
def view_service_professionals(service_id, customer_id):
    professionals = db.session.query(
            Professional.professional_id,
            Professional.name,
            Professional.phone,
            Professional.email,
            Professional.experience,
            func.avg(Reviews.rating).label("ratings")
        ).outerjoin(
            ServiceRequest, ServiceRequest.professional_id == Professional.professional_id
        ).outerjoin(
            Reviews, Reviews.request_id == ServiceRequest.request_id
        ).filter(
            Professional.service_id == service_id
        ).group_by(
            Professional.professional_id,
            Professional.name,
            Professional.phone,
            Professional.email,
            Professional.experience,
        ).all()
    
    if request.method == 'POST':
        search_query = request.form.get('search')
        if search_query:

            professionals = db.session.query(
                Professional.professional_id,
                Professional.name,
                Professional.phone,
                Professional.email,
                Professional.experience,
                func.avg(Reviews.rating).label("ratings")
            ).outerjoin(
                ServiceRequest, ServiceRequest.professional_id == Professional.professional_id
            ).outerjoin(
                Reviews, Reviews.request_id == ServiceRequest.request_id
            ).filter(
                Professional.service_id == service_id,
                (Professional.name.ilike(f'%{search_query}%') |
                Professional.phone.ilike(f'%{search_query}%') |
                Professional.email.ilike(f'%{search_query}%'))
            ).group_by(
                Professional.professional_id,
                Professional.name,
                Professional.phone,
                Professional.email,
                Professional.experience,
            ).all()
        
    service = Service.query.get(service_id)
    return render_template('view_professionals.html', service=service, professionals=professionals, customer_id = customer_id)


@app.route('/customer/<int:customer_id>/book/<int:professional_id>', methods=['POST'])
def book_service_request(customer_id, professional_id):
    try:
        professional = Professional.query.get(professional_id)
        customer = Customer.query.get(customer_id)
        new_request = ServiceRequest(
            customer_id=customer_id,  
            service_id=professional.service_id,
            professional_id=professional_id,
            date_of_request=datetime.now().strftime('%Y-%m-%d'), 
            service_status='requested',  
            location=customer.address  
        )

        db.session.add(new_request)
        db.session.commit()
        flash("Service request booked")

    except Exception as e:
        db.session.rollback() 
        flash(f"Frror {e}")

    professional = Professional.query.get(professional_id)
    #return redirect(f'customer/{customer_id}/service/{professional.service_id}')
    return redirect(f'/customer/dashboard//{customer_id}')


@app.route('/customer/search/<int:customer_id>', methods=['POST', "GET"])
def search_services(customer_id):
    search_query = request.form.get('search')
    date_filter = request.form.get('date_filter')

    results = db.session.query(
        Service.name.label('service_name'),
        Service.description,
        Professional.name.label('professional_name'),
        Professional.phone,
        Professional.email,
        ServiceRequest.date_of_request,
        ServiceRequest.date_of_completion,
        ServiceRequest.service_status,
    ).join(ServiceRequest, Service.service_id == ServiceRequest.service_id
           ).join(
        Professional, ServiceRequest.professional_id == Professional.professional_id
    ).filter(
        (Service.name.ilike(f'%{search_query}%') |
         Service.description.ilike(f'%{search_query}%') |
         Professional.name.ilike(f'%{search_query}%') |
         Professional.phone.ilike(f'%{search_query}%') |
         Professional.email.ilike(f'%{search_query}%')|
         (ServiceRequest.service_status.ilike(f"%{search_query}%") if search_query else True)) &
        ((ServiceRequest.date_of_request.ilike(f'%{date_filter}%') if date_filter else True)|
         (ServiceRequest.date_of_completion.ilike(f'%{date_filter}%') if date_filter else True))
         ).all()

    return render_template('customer_search.html', results=results, customer_id = customer_id)


@app.route('/professional/accept_req/<int:request_id>')
def accept_req(request_id):
    req = ServiceRequest.query.get(request_id)
    if req:
        req.service_status = 'accepted'
        db.session.commit()
    return redirect(f'/professional/dashboard/{req.professional_id}')

@app.route('/professional/reject_req/<int:request_id>')
def reject_req(request_id):
    req = ServiceRequest.query.get(request_id)
    if req:
        req.service_status = 'rejected'
        db.session.commit()
    return redirect(f'/professional/dashboard/{req.professional_id}')


@app.route('/customer/<int:customer_id>/close_request/<int:request_id>', methods=['GET', 'POST'])
def close_service_request(customer_id, request_id):
    service_request = ServiceRequest.query.get(request_id)

    results = db.session.query(
        Service.name.label('service_name'),
        Service.description,
        Professional.name.label('professional_name'),
        Professional.phone,
        Professional.email,
        ServiceRequest.date_of_request,
        ServiceRequest.date_of_completion,
        ServiceRequest.request_id,
        ServiceRequest.service_status,
    ).join(ServiceRequest, Service.service_id == ServiceRequest.service_id).join(
        Professional, ServiceRequest.professional_id == Professional.professional_id
    ).filter(
        ServiceRequest.request_id == request_id
    ).first()

    if request.method == 'POST':
        try:
            rating = int(request.form.get('rating'))
            remarks = request.form.get('remarks')
            service_request.service_status = 'closed'
            service_request.date_of_completion = datetime.now().strftime('%Y-%m-%d')

            review = Reviews(
                request_id=request_id,
                rating=rating,
                review=remarks
            )
            db.session.add(review)
            db.session.commit()
            flash("Service closed")
        except Exception as e:
            db.session.rollback()
            flash(f"Error {e}")
        return redirect(f'/customer/dashboard/{customer_id}')

    return render_template( 'close_servicereq.html',   customer_id=customer_id, service_request=results)


@app.route('/customer/<int:customer_id>/review/<int:request_id>', methods=['GET', 'POST'])
def view_review_cust(customer_id, request_id):
    service_request = ServiceRequest.query.get(request_id)
    results = db.session.query(
        Service.name.label('service_name'),
        Service.description,
        Professional.name.label('professional_name'),
        Professional.phone,
        Professional.email,
        ServiceRequest.date_of_request,
        ServiceRequest.date_of_completion,
        ServiceRequest.request_id,
        ServiceRequest.service_status,
    ).join(ServiceRequest, Service.service_id == ServiceRequest.service_id).join(
        Professional, ServiceRequest.professional_id == Professional.professional_id
    ).filter(
        ServiceRequest.request_id == request_id
    ).first()

    try:
        
        review = Reviews.query.filter_by(request_id=request_id).first()

        if request.method == 'POST':
            rating = int(request.form.get('rating'))
            remarks = request.form.get('remarks')

            if not review:
                review = Reviews(
                    request_id=request_id,
                    rating=rating,
                    review=remarks
                )
                db.session.add(review)
            else:
                review.rating = rating
                review.review = remarks

            db.session.commit()
            flash("Review updated")
            return redirect(url_for('view_review_cust', customer_id=customer_id, request_id=request_id))

        return render_template('view_review_cust.html',customer_id=customer_id,service_request=results,review=review)
    except Exception as e:
        flash(f"E {e}")
        print(e)
        return redirect(f'/customer/dashboard/{customer_id}')        



@app.route('/professional/<int:professional_id>/review/<int:request_id>', methods=['GET'])
def view_review_prof(professional_id, request_id):
    try:
        results = db.session.query(
                Service.name.label('service_name'),
                ServiceRequest.date_of_request,
                ServiceRequest.date_of_completion,
                Customer.name.label('customer_name'),
                ServiceRequest.location,
                ServiceRequest.request_id,
                ServiceRequest.professional_id,
            ).join(ServiceRequest, Service.service_id == ServiceRequest.service_id).join(
                Customer, Customer.customer_id == ServiceRequest.customer_id
            ).filter(ServiceRequest.request_id == request_id
                ).first()
       
        review = Reviews.query.filter_by(request_id=request_id).first()

        return render_template('view_review_prof.html',service_request=results,review=review)
    except Exception as e:
        flash(f"Error {e}")
        return redirect(url_for('prof_dashboard', professional_id=professional_id))


@app.route('/professional/search/<int:professional_id>', methods=['GET', 'POST'])
def professional_search(professional_id):
    query = request.form.get('query', '').strip()  
    date_filter = request.form.get('date_filter', '').strip()  

    search_results = []

    if query or date_filter:
        search_results = db.session.query(
            ServiceRequest.request_id,
            ServiceRequest.date_of_request,
            ServiceRequest.date_of_completion,
            ServiceRequest.service_status,
            Customer.name.label('customer_name'),
            Customer.address.label('customer_location'),
        ).join(
            Customer, Customer.customer_id == ServiceRequest.customer_id
        ).filter(
            and_(
                ServiceRequest.professional_id == professional_id, 
                or_(
                    Customer.name.ilike(f"%{query}%") if query else True,
                    Customer.username.ilike(f"%{query}%") if query else True,
                    Customer.address.ilike(f"%{query}%") if query else True,
                    ServiceRequest.service_status.ilike(f"%{query}%") if query else True,
                ),
                or_(
                    ServiceRequest.date_of_request == date_filter if date_filter else True,
                    ServiceRequest.date_of_completion == date_filter if date_filter else True,
                )
            )
        ).all()
    return render_template('prof_search.html',query=query,date_filter=date_filter,results=search_results, professional_id = professional_id)



@app.route('/chart/piechart')
def generate_piechart():

    status_counts = session.get('status_counts', [])
    if not status_counts:
        return "No data for chart generation"
    
    labels = []
    sizes = []

    for lab, siz in status_counts:
        labels.append(lab)
        sizes.append(siz)

    fig, ax = plt.subplots()
    ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)

    img = io.BytesIO()
    plt.savefig(img, format='png')
    plt.close(fig)
    img.seek(0)


    return Response(img, mimetype='image/png')


@app.route('/professional/summary/<int:professional_id>')
def professional_summary(professional_id):
    status_counts = db.session.query(
        ServiceRequest.service_status,
        func.count(ServiceRequest.request_id).label('count')
    ).filter(ServiceRequest.professional_id == professional_id
             ).group_by(ServiceRequest.service_status).all()

    average_rating = db.session.query(
        func.avg(Reviews.rating)
    ).join(
        ServiceRequest, ServiceRequest.request_id == Reviews.request_id
    ).filter(
        ServiceRequest.professional_id == professional_id,
        Reviews.rating.isnot(None)
    ).scalar()

    average_rating = average_rating if average_rating else 0.0 
    
    status_counts = [(row.service_status, row.count) for row in status_counts]
    session['status_counts'] = status_counts

    return render_template('professional_summary.html', status_counts=status_counts, average_rating=average_rating,professional_id = professional_id)

@app.route('/customer/summary/<int:customer_id>')
def customer_summary(customer_id):
    status_counts = db.session.query(
        ServiceRequest.service_status,
        func.count(ServiceRequest.request_id).label('count')
    ).filter(ServiceRequest.customer_id == customer_id
             ).group_by(ServiceRequest.service_status).all()

    status_counts = [(row.service_status, row.count) for row in status_counts]
    session['status_counts'] = status_counts

    return render_template('customer_summary.html', status_counts=status_counts, customer_id = customer_id)


@app.route('/admin/view_proof/<path:file_path>')
def view_proof(file_path):
    return send_from_directory(app.config['UPLOAD_FOLDER'], file_path)
