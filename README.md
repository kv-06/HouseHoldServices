# Household Services Application

## Demo Video
[Watch the Demo Video](https://drive.google.com/file/d/1ELBzMk3yK9odCjGEUdU6Tr0uZvImM3UY/view)


## Overview
The **Household Services Application** is a multi-user platform designed to provide comprehensive home servicing and solutions. The project implements efficient service management, service requests, and role-based dashboards.
It supports three user roles each with specific functionalities. : 
1. **Admin**
2. **Service Professionals**
3. **Customers**

## Frameworks and Technologies Used

### **Tech Stack Used**
- **Backend**: Flask, Python
- **Frontend**: HTML, CSS, Bootstrap, Jinja2
- **Database**: SQLite.

### **Libraries**
1. **SQLAlchemy**: ORM for handling database operations.
2. **Matplotlib**: For generating visualizations like pie charts.
3. **Datetime**: For managing date and time-related tasks.
4. **os**: For handling file operations.
5. **io**: For in-memory file management.


## **Architecture**
The project follows an **MVC (Model-View-Controller)** architecture:
- **Controllers**: Logic and route handlers in Flask 
- **Models**: Database models using SQLAlchemy ORM.
- **Views/Templates**: Dynamic HTML rendering with Jinja2.
- **Static Files**: CSS and uploaded documents for styling and user submissions.


## **Roles**

#### **1. Admin**
- Admin is the superuser with root access (no registration required).
- Key functionalities:
  - Login redirects to the Admin Dashboard.
  - Monitor and manage users (Customers and Service Professionals).
  - Create, update, or delete services with a base price.
  - Approve service professionals after verification of profile documents.
  - Block users (Customers/Professionals) based on fraudulent activity or poor reviews.

#### **2. Service Professional**
- Individuals providing specific services (e.g., plumbing, cleaning).
- Key functionalities:
  - Register and upload profile documents for admin approval.
  - Accept or reject assigned service requests.
  - Complete service requests and update the status.

#### **3. Customer**
- Individuals who book service requests.
- Key functionalities:
  - Login and search for services by name, location, or pin code.
  - Create, edit, or close service requests.
  - Post reviews and ratings for completed services.






## **How to Run the Application**
1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/household-services-app.git
   cd household-services-app
2. Install required dependencies
3. Run the application:
   ```bash
   python app.py
4. Open the application in your browser at http://127.0.0.1:5000.

## License
This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.
