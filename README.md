# GymBook - Gym Management App

A comprehensive cross-platform gym management application built with Flutter and FastAPI. This app helps gym owners manage members, plans, staff, and leads efficiently.

## Features

### 🏠 Dashboard
- Real-time gym statistics
- Overview of total, active, expiring, and expired members
- Quick action buttons for common tasks

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

### 📞 Leads Management
- Track potential customers
- Add contact information and notes
- Convert leads to members

## Tech Stack

### Frontend
- **Flutter** - Cross-platform mobile app development
- **Provider** - State management
- **HTTP** - API communication
- **Shared Preferences** - Local data storage

### Backend
- **FastAPI** - Python web framework
- **PostgreSQL** - Database
- **psycopg2** - PostgreSQL adapter

## Prerequisites

- Flutter SDK (3.0.0 or higher)
- Dart SDK
- Python 3.8+
- PostgreSQL database
- Android Studio / VS Code

## Installation

### 1. Backend Setup

1. **Install Python dependencies:**
   ```bash
   pip install fastapi uvicorn psycopg2-binary pydantic
   ```

2. **Configure database:**
   - Create a PostgreSQL database named `gym`
   - Update database credentials in `config/database.py`

3. **Run the FastAPI server:**
   ```bash
   cd backend
   uvicorn index:app --reload --host 0.0.0.0 --port 8000
   ```

### 2. Frontend Setup

1. **Install Flutter dependencies:**
   ```bash
   flutter pub get
   ```

2. **Configure API endpoint:**
   - Update the `baseUrl` in `lib/services/api_service.dart`
   - For Android emulator: `http://10.0.2.2:8000`
   - For iOS simulator: `http://localhost:8000`
   - For physical device: `http://your-ip:8000`

3. **Run the Flutter app:**
   ```bash
   flutter run
   ```

## Usage

### Login
- Use demo credentials: `admin@gym.com` / `admin123`
- The app will remember your login state

### Dashboard
- View gym statistics at a glance
- Click on stat cards to see detailed information
- Use quick action buttons for common tasks

### Managing Members
1. Navigate to the Members tab
2. Use the search bar to find specific members
3. Use filter chips to view members by status
4. Tap the + button to add new members
5. Use the menu on member cards to edit or delete

### Managing Plans
1. Go to the Plans tab
2. Tap + to create new plans
3. Set plan name, duration, and price
4. Use the menu to edit or delete plans

### Managing Staff
1. Navigate to the Staff tab
2. Add new staff members with their details
3. Edit or remove staff as needed

### Managing Leads
1. Go to the Leads tab
2. Add potential customers
3. Track their information and notes
4. Convert leads to members when ready

## Project Structure

```
lib/
├── main.dart                 # App entry point
├── models/                   # Data models
│   ├── client.dart
│   ├── plan.dart
│   ├── staff.dart
│   └── lead.dart
├── providers/                # State management
│   ├── auth_provider.dart
│   └── gym_provider.dart
├── screens/                  # UI screens
│   ├── splash_screen.dart
│   ├── login_screen.dart
│   ├── main_screen.dart
│   ├── dashboard_screen.dart
│   ├── members_screen.dart
│   ├── add_member_screen.dart
│   ├── plans_screen.dart
│   ├── staff_screen.dart
│   └── leads_screen.dart
├── services/                 # API services
│   └── api_service.dart
├── utils/                    # Utilities
│   └── theme.dart
└── widgets/                  # Reusable widgets
    ├── stat_card.dart
    └── member_card.dart
```

## API Endpoints

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

### Leads
- `GET /leads/` - Get all leads
- `POST /leads/` - Create new lead
- `DELETE /leads/{id}` - Delete lead

## Customization

### Theme
- Modify colors and styles in `lib/utils/theme.dart`
- Update the `AppTheme` class to match your brand

### API Configuration
- Update the base URL in `lib/services/api_service.dart`
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

3. **Flutter Build Issues:**
   - Run `flutter clean` and `flutter pub get`
   - Check Flutter and Dart versions
   - Update dependencies if needed

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

**GymBook** - Manage your gym like a pro! 💪


