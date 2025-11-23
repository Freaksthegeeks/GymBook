// Main entry point for the React application

const { useState, useEffect } = React;

// API base URL - assuming backend runs on port 8000
const API_BASE_URL = 'http://localhost:8001';

// Utility function for API calls
const apiCall = async (endpoint, options = {}) => {
    try {
        // Get token from localStorage
        const token = localStorage.getItem('token');
        
        // Add authorization header if token exists
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers
        };
        
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }
        
        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
            headers,
            ...options
        });
        
        if (!response.ok) {
            if (response.status === 401) {
                // Token expired or invalid, logout user
                localStorage.removeItem('token');
                localStorage.removeItem('username');
                localStorage.removeItem('user_id');
                window.location.reload();
                throw new Error('Authentication required');
            }
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error(`API call failed for ${endpoint}:`, error);
        throw error;
    }
};

// Login component
function Login({ onLogin }) {
    const [loginForm, setLoginForm] = useState({
        email: '',
        password: ''
    });
    const [registerForm, setRegisterForm] = useState({
        username: '',
        email: '',
        password: ''
    });
    const [isRegistering, setIsRegistering] = useState(false);
    const [error, setError] = useState(null);
    const [loading, setLoading] = useState(false);

    const handleLoginChange = (e) => {
        const { name, value } = e.target;
        setLoginForm(prev => ({
            ...prev,
            [name]: value
        }));
    };

    const handleRegisterChange = (e) => {
        const { name, value } = e.target;
        setRegisterForm(prev => ({
            ...prev,
            [name]: value
        }));
    };

    const handleLogin = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError(null);
        
        try {
            const response = await apiCall('/login/', {
                method: 'POST',
                body: JSON.stringify(loginForm)
            });
            
            // Save token to localStorage
            localStorage.setItem('token', response.access_token);
            localStorage.setItem('username', response.username);
            localStorage.setItem('user_id', response.user_id);
            
            // Notify parent component
            onLogin(response);
        } catch (err) {
            setError('Invalid email or password');
        } finally {
            setLoading(false);
        }
    };

    const handleRegister = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError(null);
        
        try {
            await apiCall('/register/', {
                method: 'POST',
                body: JSON.stringify(registerForm)
            });
            
            // Switch to login form after successful registration
            setIsRegistering(false);
            setError('Registration successful! Please login.');
        } catch (err) {
            setError('Registration failed: ' + (err.message || 'Unknown error'));
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="container mt-5">
            <div className="row justify-content-center">
                <div className="col-md-6">
                    <div className="card">
                        <div className="card-header">
                            <h3 className="text-center">
                                {isRegistering ? 'Register' : 'Login'} to GymEdge
                            </h3>
                        </div>
                        <div className="card-body">
                            {error && <div className="alert alert-danger">{error}</div>}
                            
                            {isRegistering ? (
                                <form onSubmit={handleRegister}>
                                    <div className="mb-3">
                                        <label className="form-label">Username</label>
                                        <input
                                            type="text"
                                            className="form-control"
                                            name="username"
                                            value={registerForm.username}
                                            onChange={handleRegisterChange}
                                            required
                                        />
                                    </div>
                                    <div className="mb-3">
                                        <label className="form-label">Email</label>
                                        <input
                                            type="email"
                                            className="form-control"
                                            name="email"
                                            value={registerForm.email}
                                            onChange={handleRegisterChange}
                                            required
                                        />
                                    </div>
                                    <div className="mb-3">
                                        <label className="form-label">Password</label>
                                        <input
                                            type="password"
                                            className="form-control"
                                            name="password"
                                            value={registerForm.password}
                                            onChange={handleRegisterChange}
                                            required
                                        />
                                    </div>
                                    <button
                                        type="submit"
                                        className="btn btn-primary w-100"
                                        disabled={loading}
                                    >
                                        {loading ? 'Registering...' : 'Register'}
                                    </button>
                                </form>
                            ) : (
                                <form onSubmit={handleLogin}>
                                    <div className="mb-3">
                                        <label className="form-label">Email</label>
                                        <input
                                            type="email"
                                            className="form-control"
                                            name="email"
                                            value={loginForm.email}
                                            onChange={handleLoginChange}
                                            required
                                        />
                                    </div>
                                    <div className="mb-3">
                                        <label className="form-label">Password</label>
                                        <input
                                            type="password"
                                            className="form-control"
                                            name="password"
                                            value={loginForm.password}
                                            onChange={handleLoginChange}
                                            required
                                        />
                                    </div>
                                    <button
                                        type="submit"
                                        className="btn btn-primary w-100"
                                        disabled={loading}
                                    >
                                        {loading ? 'Logging in...' : 'Login'}
                                    </button>
                                </form>
                            )}
                            
                            <div className="mt-3 text-center">
                                <button
                                    className="btn btn-link"
                                    onClick={() => setIsRegistering(!isRegistering)}
                                >
                                    {isRegistering 
                                        ? 'Already have an account? Login' 
                                        : "Don't have an account? Register"}
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}

// Simple component to demonstrate React functionality
function App() {
    const [isLoggedIn, setIsLoggedIn] = useState(false);
    const [currentUser, setCurrentUser] = useState(null);
    const [currentPage, setCurrentPage] = useState('dashboard');
    const [clients, setClients] = useState([]);
    const [plans, setPlans] = useState([]);
    const [staffs, setStaffs] = useState([]);
    const [dashboardStats, setDashboardStats] = useState({
        total_members: 0,
        active_members: 0,
        expiring_in_10_days: 0,
        expired_in_last_30_days: 0
    });
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    // Check if user is already logged in
    useEffect(() => {
        const token = localStorage.getItem('token');
        const username = localStorage.getItem('username');
        const userId = localStorage.getItem('user_id');
        
        if (token && username && userId) {
            setIsLoggedIn(true);
            setCurrentUser({
                username,
                user_id: userId
            });
        }
    }, []);

    // Fetch data from the backend API
    const fetchData = async () => {
        setLoading(true);
        setError(null);
        try {
            // Fetch all data
            const clientsData = await apiCall('/clients/');
            const plansData = await apiCall('/plans/');
            const staffsData = await apiCall('/staffs/');
            const dashboardData = await apiCall('/dashboard/stats');
            
            setClients(clientsData.clients || []);
            setPlans(plansData.plans || []);
            setStaffs(staffsData.staffs || []);
            setDashboardStats(dashboardData);
        } catch (err) {
            setError('Failed to fetch data: ' + err.message);
            console.error('Fetch error:', err);
        } finally {
            setLoading(false);
        }
    };

    // Initial data load when logged in
    useEffect(() => {
        if (isLoggedIn) {
            fetchData();
        }
    }, [isLoggedIn]);

    // Handle login
    const handleLogin = (userData) => {
        setIsLoggedIn(true);
        setCurrentUser(userData);
    };

    // Handle logout
    const handleLogout = () => {
        localStorage.removeItem('token');
        localStorage.removeItem('username');
        localStorage.removeItem('user_id');
        setIsLoggedIn(false);
        setCurrentUser(null);
        setCurrentPage('dashboard');
    };

    // Navigation handler
    const handleNavigation = (page) => {
        setCurrentPage(page);
        // Refresh data when navigating to a page
        if (isLoggedIn) {
            fetchData();
        }
    };

    // If not logged in, show login page
    if (!isLoggedIn) {
        return <Login onLogin={handleLogin} />;
    }

    // Render current page based on state
    const renderPage = () => {
        switch (currentPage) {
            case 'dashboard':
                return <Dashboard 
                    stats={dashboardStats} 
                    clients={clients} 
                    plans={plans} 
                    staffs={staffs} 
                    loading={loading} 
                    error={error} 
                    onNavigate={handleNavigation}
                />;
            case 'clients':
                return <Clients clients={clients} plans={plans} onRefresh={fetchData} loading={loading} error={error} />;
            case 'plans':
                return <Plans plans={plans} onRefresh={fetchData} loading={loading} error={error} />;
            case 'staff':
                return <Staff staffs={staffs} onRefresh={fetchData} loading={loading} error={error} />;
            case 'payments':
                return <Payments onRefresh={fetchData} loading={loading} error={error} />;
            default:
                return <Dashboard 
                    stats={dashboardStats} 
                    clients={clients} 
                    plans={plans} 
                    staffs={staffs} 
                    loading={loading} 
                    error={error} 
                    onNavigate={handleNavigation}
                />;
        }
    };

    return (
        <div>
            <Navbar onNavigate={handleNavigation} onLogout={handleLogout} currentUser={currentUser} />
            <div className="container mt-4">
                {loading && <div className="alert alert-info">Loading data...</div>}
                {error && <div className="alert alert-danger">Error: {error}</div>}
                {renderPage()}
            </div>
            <Footer />
        </div>
    );
}

// Navbar component
function Navbar({ onNavigate, onLogout, currentUser }) {
    return (
        <nav className="navbar navbar-expand-lg navbar-dark">
            <div className="container">
                <a className="navbar-brand" href="#">GymEdge</a>
                <button className="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                    <span className="navbar-toggler-icon"></span>
                </button>
                <div className="collapse navbar-collapse" id="navbarNav">
                    <ul className="navbar-nav me-auto">
                        <li className="nav-item">
                            <button className="nav-link btn" onClick={() => onNavigate('dashboard')}>Dashboard</button>
                        </li>
                        <li className="nav-item">
                            <button className="nav-link btn" onClick={() => onNavigate('clients')}>Clients</button>
                        </li>
                        <li className="nav-item">
                            <button className="nav-link btn" onClick={() => onNavigate('plans')}>Plans</button>
                        </li>
                        <li className="nav-item">
                            <button className="nav-link btn" onClick={() => onNavigate('staff')}>Staff</button>
                        </li>
                        <li className="nav-item">
                            <button className="nav-link btn" onClick={() => onNavigate('payments')}>Payments</button>
                        </li>
                    </ul>
                    <ul className="navbar-nav">
                        <li className="nav-item me-3">
                            <span className="navbar-text">
                                Welcome, {currentUser?.username || 'User'}
                            </span>
                        </li>
                        <li className="nav-item">
                            <button className="nav-link btn" onClick={onLogout}>Logout</button>
                        </li>
                    </ul>
                </div>
            </div>
        </nav>
    );
}

// Dashboard component
function Dashboard({ stats, clients, plans, staffs, loading, error, onNavigate }) {
    if (loading) return <div>Loading dashboard...</div>;
    if (error) return <div className="alert alert-danger">Error: {error}</div>;

    return (
        <div>
            <div className="dashboard-header text-center">
                <h1>Welcome to GymEdge</h1>
                <p className="lead">Manage your gym efficiently</p>
            </div>
            
            {/* Statistics Cards */}
            <div className="row mb-4">
                <div className="col-md-3 mb-4">
                    <div 
                        className="stat-card blue clickable" 
                        onClick={() => onNavigate('clients')}
                        style={{ cursor: 'pointer' }}
                    >
                        <h3>{stats.total_members}</h3>
                        <p>Total Members</p>
                    </div>
                </div>
                <div className="col-md-3 mb-4">
                    <div 
                        className="stat-card green clickable" 
                        onClick={() => onNavigate('clients')}
                        style={{ cursor: 'pointer' }}
                    >
                        <h3>{stats.active_members}</h3>
                        <p>Active Members</p>
                    </div>
                </div>
                <div className="col-md-3 mb-4">
                    <div 
                        className="stat-card orange clickable" 
                        onClick={() => onNavigate('clients')}
                        style={{ cursor: 'pointer' }}
                    >
                        <h3>{stats.expiring_in_10_days}</h3>
                        <p>Expiring in 10 Days</p>
                    </div>
                </div>
                <div className="col-md-3 mb-4">
                    <div 
                        className="stat-card red clickable" 
                        onClick={() => onNavigate('clients')}
                        style={{ cursor: 'pointer' }}
                    >
                        <h3>{stats.expired_in_last_30_days}</h3>
                        <p>Expired in 30 Days</p>
                    </div>
                </div>
            </div>
            
            <div className="row">
                <div className="col-md-6">
                    <div className="card">
                        <div className="card-header">
                            <h5>Recent Clients</h5>
                        </div>
                        <div className="card-body">
                            <table className="table table-striped">
                                <thead>
                                    <tr>
                                        <th>Name</th>
                                        <th>Email</th>
                                        <th>Plan</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {clients.slice(0, 5).map(client => (
                                        <tr key={client.id}>
                                            <td>{client.clientname}</td>
                                            <td>{client.email}</td>
                                            <td>{client.planname}</td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
                
                <div className="col-md-6">
                    <div className="card">
                        <div className="card-header">
                            <h5>Membership Plans</h5>
                        </div>
                        <div className="card-body">
                            <table className="table table-striped">
                                <thead>
                                    <tr>
                                        <th>Plan</th>
                                        <th>Duration</th>
                                        <th>Amount</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {plans.slice(0, 5).map(plan => (
                                        <tr key={plan.id}>
                                            <td>{plan.planname}</td>
                                            <td>{plan.days} days</td>
                                            <td>${plan.amount}</td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}

// Clients component
function Clients({ clients, plans, onRefresh, loading, error }) {
    const [clientForm, setClientForm] = useState({
        clientname: '',
        email: '',
        phonenumber: '',
        dateofbirth: '',
        gender: '',
        bloodgroup: '',
        address: '',
        notes: '',
        height: '',
        weight: '',
        plan_id: '',
        start_date: new Date().toISOString().split('T')[0]
    });

    const handleClientFormChange = (e) => {
        const { name, value } = e.target;
        setClientForm(prev => ({
            ...prev,
            [name]: value
        }));
    };

    const handleAddClient = async (e) => {
        e.preventDefault();
        try {
            // Convert form data to correct types
            const clientData = {
                ...clientForm,
                height: parseFloat(clientForm.height),
                weight: parseFloat(clientForm.weight),
                plan_id: parseInt(clientForm.plan_id)
            };
            
            await apiCall('/clients/', {
                method: 'POST',
                body: JSON.stringify(clientData)
            });
            
            // Reset form
            setClientForm({
                clientname: '',
                email: '',
                phonenumber: '',
                dateofbirth: '',
                gender: '',
                bloodgroup: '',
                address: '',
                notes: '',
                height: '',
                weight: '',
                plan_id: '',
                start_date: new Date().toISOString().split('T')[0]
            });
            
            // Refresh data
            onRefresh();
            
            alert('Client added successfully!');
        } catch (err) {
            alert('Failed to add client: ' + err.message);
        }
    };

    const handleDeleteClient = async (clientId) => {
        if (!window.confirm('Are you sure you want to delete this client?')) return;
        
        try {
            await apiCall(`/clients/${clientId}`, {
                method: 'DELETE'
            });
            
            // Refresh data
            onRefresh();
            
            alert('Client deleted successfully!');
        } catch (err) {
            alert('Failed to delete client: ' + err.message);
        }
    };

    if (loading) return <div>Loading clients...</div>;
    if (error) return <div className="alert alert-danger">Error: {error}</div>;

    return (
        <div>
            <h2>Clients Management</h2>
            <div className="form-container">
                <h4>Add New Client</h4>
                <form onSubmit={handleAddClient}>
                    <div className="row">
                        <div className="col-md-6 mb-3">
                            <label className="form-label">Full Name</label>
                            <input 
                                type="text" 
                                className="form-control" 
                                name="clientname"
                                value={clientForm.clientname}
                                onChange={handleClientFormChange}
                                placeholder="Enter full name" 
                                required
                            />
                        </div>
                        <div className="col-md-6 mb-3">
                            <label className="form-label">Email</label>
                            <input 
                                type="email" 
                                className="form-control" 
                                name="email"
                                value={clientForm.email}
                                onChange={handleClientFormChange}
                                placeholder="Enter email" 
                                required
                            />
                        </div>
                    </div>
                    <div className="row">
                        <div className="col-md-6 mb-3">
                            <label className="form-label">Phone Number</label>
                            <input 
                                type="tel" 
                                className="form-control" 
                                name="phonenumber"
                                value={clientForm.phonenumber}
                                onChange={handleClientFormChange}
                                placeholder="Enter phone number" 
                                required
                            />
                        </div>
                        <div className="col-md-6 mb-3">
                            <label className="form-label">Date of Birth</label>
                            <input 
                                type="date" 
                                className="form-control" 
                                name="dateofbirth"
                                value={clientForm.dateofbirth}
                                onChange={handleClientFormChange}
                                required
                            />
                        </div>
                    </div>
                    <div className="row">
                        <div className="col-md-6 mb-3">
                            <label className="form-label">Gender</label>
                            <select 
                                className="form-select" 
                                name="gender"
                                value={clientForm.gender}
                                onChange={handleClientFormChange}
                                required
                            >
                                <option value="">Select gender</option>
                                <option value="Male">Male</option>
                                <option value="Female">Female</option>
                                <option value="Other">Other</option>
                            </select>
                        </div>
                        <div className="col-md-6 mb-3">
                            <label className="form-label">Blood Group</label>
                            <select 
                                className="form-select" 
                                name="bloodgroup"
                                value={clientForm.bloodgroup}
                                onChange={handleClientFormChange}
                                required
                            >
                                <option value="">Select blood group</option>
                                <option value="A+">A+</option>
                                <option value="A-">A-</option>
                                <option value="B+">B+</option>
                                <option value="B-">B-</option>
                                <option value="AB+">AB+</option>
                                <option value="AB-">AB-</option>
                                <option value="O+">O+</option>
                                <option value="O-">O-</option>
                            </select>
                        </div>
                    </div>
                    <div className="row">
                        <div className="col-md-6 mb-3">
                            <label className="form-label">Height (cm)</label>
                            <input 
                                type="number" 
                                className="form-control" 
                                name="height"
                                value={clientForm.height}
                                onChange={handleClientFormChange}
                                placeholder="Enter height" 
                                required
                            />
                        </div>
                        <div className="col-md-6 mb-3">
                            <label className="form-label">Weight (kg)</label>
                            <input 
                                type="number" 
                                className="form-control" 
                                name="weight"
                                value={clientForm.weight}
                                onChange={handleClientFormChange}
                                placeholder="Enter weight" 
                                required
                            />
                        </div>
                    </div>
                    <div className="row">
                        <div className="col-md-6 mb-3">
                            <label className="form-label">Address</label>
                            <textarea 
                                className="form-control" 
                                name="address"
                                value={clientForm.address}
                                onChange={handleClientFormChange}
                                placeholder="Enter address" 
                                required
                            />
                        </div>
                        <div className="col-md-6 mb-3">
                            <label className="form-label">Notes</label>
                            <textarea 
                                className="form-control" 
                                name="notes"
                                value={clientForm.notes}
                                onChange={handleClientFormChange}
                                placeholder="Enter any notes"
                            />
                        </div>
                    </div>
                    <div className="row">
                        <div className="col-md-6 mb-3">
                            <label className="form-label">Select Plan</label>
                            <select 
                                className="form-select" 
                                name="plan_id"
                                value={clientForm.plan_id}
                                onChange={handleClientFormChange}
                                required
                            >
                                <option value="">Select a plan</option>
                                {plans.map(plan => (
                                    <option key={plan.id} value={plan.id}>
                                        {plan.planname} ({plan.days} days - ${plan.amount})
                                    </option>
                                ))}
                            </select>
                        </div>
                        <div className="col-md-6 mb-3">
                            <label className="form-label">Start Date</label>
                            <input 
                                type="date" 
                                className="form-control" 
                                name="start_date"
                                value={clientForm.start_date}
                                onChange={handleClientFormChange}
                                required
                            />
                        </div>
                    </div>
                    <button type="submit" className="btn btn-primary">Add Client</button>
                </form>
            </div>
            
            <div className="table-container">
                <h4>All Clients</h4>
                <table className="table table-striped">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Name</th>
                            <th>Email</th>
                            <th>Phone</th>
                            <th>Plan</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {clients.map(client => (
                            <tr key={client.id}>
                                <td>{client.id}</td>
                                <td>{client.clientname}</td>
                                <td>{client.email}</td>
                                <td>{client.phonenumber}</td>
                                <td>{client.planname}</td>
                                <td>
                                    <button className="btn btn-sm btn-outline-primary me-1">Edit</button>
                                    <button 
                                        className="btn btn-sm btn-outline-danger"
                                        onClick={() => handleDeleteClient(client.id)}
                                    >
                                        Delete
                                    </button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
}

// Plans component
function Plans({ plans, onRefresh, loading, error }) {
    const [planForm, setPlanForm] = useState({
        planname: '',
        days: '',
        amount: ''
    });

    const handlePlanFormChange = (e) => {
        const { name, value } = e.target;
        setPlanForm(prev => ({
            ...prev,
            [name]: value
        }));
    };

    const handleAddPlan = async (e) => {
        e.preventDefault();
        try {
            // Convert form data to correct types
            const planData = {
                ...planForm,
                days: parseInt(planForm.days),
                amount: parseFloat(planForm.amount)
            };
            
            await apiCall('/plans/', {
                method: 'POST',
                body: JSON.stringify(planData)
            });
            
            // Reset form
            setPlanForm({
                planname: '',
                days: '',
                amount: ''
            });
            
            // Refresh data
            onRefresh();
            
            alert('Plan added successfully!');
        } catch (err) {
            alert('Failed to add plan: ' + err.message);
        }
    };

    const handleDeletePlan = async (planId) => {
        if (!window.confirm('Are you sure you want to delete this plan?')) return;
        
        try {
            await apiCall(`/plans/${planId}`, {
                method: 'DELETE'
            });
            
            // Refresh data
            onRefresh();
            
            alert('Plan deleted successfully!');
        } catch (err) {
            alert('Failed to delete plan: ' + err.message);
        }
    };

    if (loading) return <div>Loading plans...</div>;
    if (error) return <div className="alert alert-danger">Error: {error}</div>;

    return (
        <div>
            <h2>Membership Plans</h2>
            <div className="form-container">
                <h4>Create New Plan</h4>
                <form onSubmit={handleAddPlan}>
                    <div className="row">
                        <div className="col-md-4 mb-3">
                            <label className="form-label">Plan Name</label>
                            <input 
                                type="text" 
                                className="form-control" 
                                name="planname"
                                value={planForm.planname}
                                onChange={handlePlanFormChange}
                                placeholder="Enter plan name" 
                                required
                            />
                        </div>
                        <div className="col-md-4 mb-3">
                            <label className="form-label">Duration (Days)</label>
                            <input 
                                type="number" 
                                className="form-control" 
                                name="days"
                                value={planForm.days}
                                onChange={handlePlanFormChange}
                                placeholder="Enter duration" 
                                required
                            />
                        </div>
                        <div className="col-md-4 mb-3">
                            <label className="form-label">Amount ($)</label>
                            <input 
                                type="number" 
                                step="0.01" 
                                className="form-control" 
                                name="amount"
                                value={planForm.amount}
                                onChange={handlePlanFormChange}
                                placeholder="Enter amount" 
                                required
                            />
                        </div>
                    </div>
                    <button type="submit" className="btn btn-primary">Create Plan</button>
                </form>
            </div>
            
            <div className="table-container">
                <h4>All Plans</h4>
                <table className="table table-striped">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Plan Name</th>
                            <th>Duration</th>
                            <th>Amount</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {plans.map(plan => (
                            <tr key={plan.id}>
                                <td>{plan.id}</td>
                                <td>{plan.planname}</td>
                                <td>{plan.days} days</td>
                                <td>${plan.amount}</td>
                                <td>
                                    <button className="btn btn-sm btn-outline-primary me-1">Edit</button>
                                    <button 
                                        className="btn btn-sm btn-outline-danger"
                                        onClick={() => handleDeletePlan(plan.id)}
                                    >
                                        Delete
                                    </button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
}

// Staff component
function Staff({ staffs, onRefresh, loading, error }) {
    const [staffForm, setStaffForm] = useState({
        staffname: '',
        email: '',
        phonenumber: '',
        role: ''
    });

    const handleStaffFormChange = (e) => {
        const { name, value } = e.target;
        setStaffForm(prev => ({
            ...prev,
            [name]: value
        }));
    };

    const handleAddStaff = async (e) => {
        e.preventDefault();
        try {
            // Convert form data to correct types
            const staffData = {
                ...staffForm,
                phonenumber: parseInt(staffForm.phonenumber)
            };
            
            await apiCall('/staffs/', {
                method: 'POST',
                body: JSON.stringify(staffData)
            });
            
            // Reset form
            setStaffForm({
                staffname: '',
                email: '',
                phonenumber: '',
                role: ''
            });
            
            // Refresh data
            onRefresh();
            
            alert('Staff added successfully!');
        } catch (err) {
            alert('Failed to add staff: ' + err.message);
        }
    };

    const handleDeleteStaff = async (staffId) => {
        if (!window.confirm('Are you sure you want to delete this staff member?')) return;
        
        try {
            await apiCall(`/staffs/${staffId}`, {
                method: 'DELETE'
            });
            
            // Refresh data
            onRefresh();
            
            alert('Staff deleted successfully!');
        } catch (err) {
            alert('Failed to delete staff: ' + err.message);
        }
    };

    if (loading) return <div>Loading staff...</div>;
    if (error) return <div className="alert alert-danger">Error: {error}</div>;

    return (
        <div>
            <h2>Staff Management</h2>
            <div className="form-container">
                <h4>Add New Staff</h4>
                <form onSubmit={handleAddStaff}>
                    <div className="row">
                        <div className="col-md-6 mb-3">
                            <label className="form-label">Full Name</label>
                            <input 
                                type="text" 
                                className="form-control" 
                                name="staffname"
                                value={staffForm.staffname}
                                onChange={handleStaffFormChange}
                                placeholder="Enter full name" 
                                required
                            />
                        </div>
                        <div className="col-md-6 mb-3">
                            <label className="form-label">Email</label>
                            <input 
                                type="email" 
                                className="form-control" 
                                name="email"
                                value={staffForm.email}
                                onChange={handleStaffFormChange}
                                placeholder="Enter email" 
                                required
                            />
                        </div>
                    </div>
                    <div className="row">
                        <div className="col-md-6 mb-3">
                            <label className="form-label">Phone Number</label>
                            <input 
                                type="tel" 
                                className="form-control" 
                                name="phonenumber"
                                value={staffForm.phonenumber}
                                onChange={handleStaffFormChange}
                                placeholder="Enter phone number" 
                                required
                            />
                        </div>
                        <div className="col-md-6 mb-3">
                            <label className="form-label">Role</label>
                            <select 
                                className="form-select" 
                                name="role"
                                value={staffForm.role}
                                onChange={handleStaffFormChange}
                                required
                            >
                                <option value="">Select a role</option>
                                <option value="Trainer">Trainer</option>
                                <option value="Manager">Manager</option>
                                <option value="Receptionist">Receptionist</option>
                                <option value="Admin">Admin</option>
                            </select>
                        </div>
                    </div>
                    <button type="submit" className="btn btn-primary">Add Staff</button>
                </form>
            </div>
            
            <div className="table-container">
                <h4>All Staff</h4>
                <table className="table table-striped">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Name</th>
                            <th>Email</th>
                            <th>Phone</th>
                            <th>Role</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {staffs.map(staff => (
                            <tr key={staff.id}>
                                <td>{staff.id}</td>
                                <td>{staff.staffname}</td>
                                <td>{staff.email}</td>
                                <td>{staff.phonenumber || 'N/A'}</td>
                                <td>{staff.role}</td>
                                <td>
                                    <button className="btn btn-sm btn-outline-primary me-1">Edit</button>
                                    <button 
                                        className="btn btn-sm btn-outline-danger"
                                        onClick={() => handleDeleteStaff(staff.id)}
                                    >
                                        Delete
                                    </button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
}

// Payments component
function Payments({ onRefresh, loading, error }) {
    const [paymentForm, setPaymentForm] = useState({
        client_id: '',
        amount: '',
        paid_at: new Date().toISOString().split('T')[0],
        note: '',
        method: 'Cash'
    });

    const handlePaymentFormChange = (e) => {
        const { name, value } = e.target;
        setPaymentForm(prev => ({
            ...prev,
            [name]: value
        }));
    };

    const handleAddPayment = async (e) => {
        e.preventDefault();
        try {
            // Convert form data to correct types
            const paymentData = {
                ...paymentForm,
                client_id: parseInt(paymentForm.client_id),
                amount: parseFloat(paymentForm.amount)
            };
            
            await apiCall('/payments/', {
                method: 'POST',
                body: JSON.stringify(paymentData)
            });
            
            // Reset form
            setPaymentForm({
                client_id: '',
                amount: '',
                paid_at: new Date().toISOString().split('T')[0],
                note: '',
                method: 'Cash'
            });
            
            // Refresh data
            onRefresh();
            
            alert('Payment recorded successfully!');
        } catch (err) {
            alert('Failed to record payment: ' + err.message);
        }
    };

    const handleDeletePayment = async (paymentId) => {
        if (!window.confirm('Are you sure you want to delete this payment?')) return;
        
        try {
            // Note: The backend doesn't currently have a DELETE endpoint for payments
            // This is just a placeholder for future implementation
            alert('Payment deletion is not yet implemented in the backend API');
        } catch (err) {
            alert('Failed to delete payment: ' + err.message);
        }
    };

    if (loading) return <div>Loading payments...</div>;
    if (error) return <div className="alert alert-danger">Error: {error}</div>;

    return (
        <div>
            <h2>Payment Management</h2>
            <div className="form-container">
                <h4>Record New Payment</h4>
                <form onSubmit={handleAddPayment}>
                    <div className="row">
                        <div className="col-md-6 mb-3">
                            <label className="form-label">Client ID</label>
                            <input 
                                type="number" 
                                className="form-control" 
                                name="client_id"
                                value={paymentForm.client_id}
                                onChange={handlePaymentFormChange}
                                placeholder="Enter client ID" 
                                required
                            />
                        </div>
                        <div className="col-md-6 mb-3">
                            <label className="form-label">Amount ($)</label>
                            <input 
                                type="number" 
                                step="0.01" 
                                className="form-control" 
                                name="amount"
                                value={paymentForm.amount}
                                onChange={handlePaymentFormChange}
                                placeholder="Enter amount" 
                                required
                            />
                        </div>
                    </div>
                    <div className="row">
                        <div className="col-md-6 mb-3">
                            <label className="form-label">Payment Method</label>
                            <select 
                                className="form-select" 
                                name="method"
                                value={paymentForm.method}
                                onChange={handlePaymentFormChange}
                            >
                                <option value="Cash">Cash</option>
                                <option value="Credit Card">Credit Card</option>
                                <option value="Debit Card">Debit Card</option>
                                <option value="Bank Transfer">Bank Transfer</option>
                            </select>
                        </div>
                        <div className="col-md-6 mb-3">
                            <label className="form-label">Date</label>
                            <input 
                                type="date" 
                                className="form-control" 
                                name="paid_at"
                                value={paymentForm.paid_at}
                                onChange={handlePaymentFormChange}
                                required
                            />
                        </div>
                    </div>
                    <div className="mb-3">
                        <label className="form-label">Notes</label>
                        <textarea 
                            className="form-control" 
                            name="note"
                            value={paymentForm.note}
                            onChange={handlePaymentFormChange}
                            rows="3" 
                            placeholder="Enter any notes"
                        />
                    </div>
                    <button type="submit" className="btn btn-primary">Record Payment</button>
                </form>
            </div>
            
            <div className="table-container">
                <h4>Payment History</h4>
                <div className="alert alert-info">
                    Payment history display is not yet implemented. The backend API currently doesn't return payment details in a format that can be easily displayed.
                </div>
                {/* This section would be implemented when the backend API is updated to return payment details */}
            </div>
        </div>
    );
}

// Footer component
function Footer() {
    return (
        <footer className="footer mt-5">
            <div className="container text-center">
                <p>&copy; 2025 GymEdge. All rights reserved.</p>
            </div>
        </footer>
    );
}

// Render the app
const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<App />);