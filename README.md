# GymEdge - Gym Management System

A comprehensive gym management system with a React frontend and FastAPI backend. This system helps gym owners manage members, plans, staff, payments, and leads efficiently.

## Features

### 🏠 Dashboard
- Real-time gym statistics
- Overview of total members, plans, staff, and active sessions
- Quick navigation to all sections

### 👥 Members Management
- Add, edit, and delete gym members
- Comprehensive member profiles with personal and health information
- Search and filter members
- Track membership status and expiration dates

### 📋 Plans Management
- Create and manage membership plans
- Set duration and pricing
- Edit and delete existing plans

### 👨‍💼 Staff Management
- Manage gym staff members
- Track staff roles and contact information
- Add, edit, and remove staff

### 💰 Payments Management
- Record member payments
- Track payment history
- View payment statistics

### 📞 Leads Management
- Track potential customers
- Add contact information and notes
- Convert leads to members

## Tech Stack

### Frontend
- **React.js** - JavaScript library for building user interfaces
- **HTML5/CSS3** - Markup and styling
- **Bootstrap** - Responsive design framework
- **Vanilla JavaScript** - Client-side scripting

### Backend
- **FastAPI** - Python web framework
- **PostgreSQL** - Database
- **psycopg2** - PostgreSQL adapter

## Prerequisites

- Python 3.8+
- PostgreSQL database
- Node.js (for development server)
- Modern web browser

## Installation

### 1. Backend Setup

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure database:**
   - Create a PostgreSQL database named `gym`
   - Update database credentials in `config/database.py`

3. **Initialize the database:**
   ```bash
   python config/database.py
   ```

4. **Run the FastAPI server:**
   ```bash
   uvicorn index:app --reload --host 0.0.0.0 --port 8000
   ```

### 2. Frontend Setup

1. **Serve the frontend:**
   - Use any static file server to serve files from the `web/` directory
   - For development, you can use Python's built-in server:
   ```bash
   cd web
   python -m http.server 3000
   ```

2. **Access the application:**
   - Backend API: `http://localhost:8000`
   - Frontend: `http://localhost:3000`

## Usage

### Login
- Use demo credentials: `admin@gym.com` / `admin123`
- The app will remember your login state

### Dashboard
- View gym statistics at a glance
- Navigate to different sections using the top navigation bar

### Managing Members
1. Navigate to the Members section
2. Use the form to add new members
3. View all members in the table
4. Edit or delete members using the action buttons

### Managing Plans
1. Go to the Plans section
2. Use the form to create new plans
3. Set plan name, duration, and price
4. Edit or delete plans using the action buttons

### Managing Staff
1. Navigate to the Staff section
2. Add new staff members with their details
3. Edit or remove staff as needed

### Recording Payments
1. Go to the Payments section
2. Record new payments with member details
3. View payment history in the table

### Managing Leads
1. Navigate to the Leads section
2. Add potential customers
3. Track their information and notes
4. Convert leads to members when ready

## Project Structure

```
.
├── config/
│   └── database.py           # Database configuration
├── routes/                   # API route handlers
│   ├── clients.py
│   ├── dashboard.py
│   ├── leads.py
│   ├── payments.py
│   ├── plans.py
│   └── staffs.py
├── web/                      # React frontend
│   ├── index.html            # Main HTML file
│   ├── styles/               # CSS stylesheets
│   ├── scripts/              # JavaScript files
│   └── components/           # React components
├── index.py                  # FastAPI application entry point
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

## API Endpoints

### Authentication
- `POST /register/` - Register new user
- `POST /login/` - User login
- `GET /me/` - Get current user info

### Dashboard
- `GET /dashboard/stats` - Get gym statistics

### Members
- `GET /clients/` - Get all members
- `POST /clients/` - Create new member
- `PUT /clients/{id}` - Update member
- `DELETE /clients/{id}` - Delete member
- `GET /clients/filter/?status={status}` - Filter members by status

### Plans
- `GET /plans/` - Get all plans
- `POST /plans/` - Create new plan
- `PUT /plans/{id}` - Update plan
- `DELETE /plans/{id}` - Delete plan

### Staff
- `GET /staffs/` - Get all staff
- `POST /staffs/` - Create new staff
- `PUT /staffs/{id}` - Update staff
- `DELETE /staffs/{id}` - Delete staff

### Payments
- `GET /payments/` - Get all payments
- `POST /payments/` - Record new payment
- `PUT /payments/{id}` - Update payment
- `DELETE /payments/{id}` - Delete payment

### Leads
- `GET /leads/` - Get all leads
- `POST /leads/` - Create new lead
- `DELETE /leads/{id}` - Delete lead

## Customization

### Styling
- Modify colors and styles in `web/styles/main.css`
- Update the CSS classes to match your brand

### API Configuration
- Update the base URL in JavaScript fetch calls
- Modify API endpoints as needed

### Database
- Update database schema in `config/database.py`
- Add new tables or modify existing ones

## Troubleshooting

### Common Issues

1. **Connection Error:**
   - Ensure the FastAPI server is running
   - Check the API base URL configuration
   - Verify network connectivity

2. **Database Connection:**
   - Check PostgreSQL service is running
   - Verify database credentials
   - Ensure database exists

3. **Frontend Not Loading:**
   - Ensure all files are in the correct directories
   - Check browser console for errors
   - Verify static file server is running

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support and questions, please open an issue on GitHub or contact the development team.

---

**GymEdge** - Manage your gym like a pro! 💪