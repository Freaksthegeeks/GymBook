// Main entry point for the React application

const { useState, useEffect } = React;

// API base URL - assuming backend runs on port 8001
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
        
        // Add timestamp to bust cache
        const cacheBuster = endpoint.includes('?') ? `&_t=${Date.now()}` : `?_t=${Date.now()}`;
        const response = await fetch(`${API_BASE_URL}${endpoint}${cacheBuster}`, {
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
        const [filteredClients, setFilteredClients] = useState([]);
        const [filterStatus, setFilterStatus] = useState('all');
    const [staffs, setStaffs] = useState([]);
    const [leads, setLeads] = useState([]);
    const [dashboardStats, setDashboardStats] = useState({
        total_members: 0,
        active_members: 0,
        expiring_in_10_days: 0,
        expired_in_last_30_days: 0,
        birthdays_today: 0,
        total_leads: 0
    });
    const [birthdayClients, setBirthdayClients] = useState([]);
    const [dueMembers, setDueMembers] = useState([]);
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
            const leadsData = await apiCall('/leads/');
            const dashboardData = await apiCall('/dashboard/stats');
            const birthdayData = await apiCall('/clients/birthdays/today');
            const dueMembersData = await apiCall('/dashboard/due_members');
            
            setClients(clientsData.clients || []);
            setPlans(plansData.plans || []);
            setStaffs(staffsData.staffs || []);
            setLeads(leadsData.leads || []);
            setDashboardStats(dashboardData);
            setBirthdayClients(birthdayData.clients || []);
            setDueMembers(dueMembersData.due_members || []);
        } catch (err) {
            setError('Failed to fetch data: ' + err.message);
            console.error('Fetch error:', err);
        } finally {
            setLoading(false);
        }
    };

    // Fetch filtered clients
    const fetchFilteredClients = async (status) => {
        setLoading(true);
        setError(null);
        try {
            let clientsData;
            if (status === 'all') {
                clientsData = await apiCall('/clients/');
            } else {
                clientsData = await apiCall(`/clients/filter/?status=${status}`);
            }
            
            if (status === 'all') {
                setFilteredClients(clientsData.clients || []);
            } else {
                setFilteredClients(clientsData.clients || []);
            }
            setFilterStatus(status);
        } catch (err) {
            setError('Failed to fetch filtered data: ' + err.message);
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

    // Navigation handler for filtered client views
    const handleFilteredNavigation = (page, status) => {
        setCurrentPage(page);
        if (isLoggedIn) {
            fetchFilteredClients(status);
        }
    };

    // Update global reference to handleFilteredNavigation
    useEffect(() => {
        window.handleFilteredNavigation = handleFilteredNavigation;
    }, [isLoggedIn]);

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
                    leads={leads}
                    birthdayClients={birthdayClients}
                    dueMembers={dueMembers}
                    loading={loading} 
                    error={error} 
                    onNavigate={handleNavigation}
                />;
            case 'clients':
                return <Clients clients={filterStatus === 'all' ? clients : filteredClients} plans={plans} onRefresh={fetchData} loading={loading} error={error} filterStatus={filterStatus} onFilterChange={fetchFilteredClients} />;
            case 'plans':
                return <Plans plans={plans} onRefresh={fetchData} loading={loading} error={error} />;
            case 'staff':
                return <Staff staffs={staffs} onRefresh={fetchData} loading={loading} error={error} />;
            case 'payments':
                return <Payments clients={clients} onRefresh={fetchData} loading={loading} error={error} />;
            case 'leads':
                return <Leads leads={leads} onRefresh={fetchData} loading={loading} error={error} />;
            case 'reports':
                return <Reports onRefresh={fetchData} loading={loading} error={error} />;
            default:
                return <Dashboard 
                    stats={dashboardStats} 
                    clients={clients} 
                    plans={plans} 
                    staffs={staffs} 
                    leads={leads}
                    birthdayClients={birthdayClients}
                    dueMembers={dueMembers}
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
                        <li className="nav-item">
                            <button className="nav-link btn" onClick={() => onNavigate('leads')}>Leads</button>
                        </li>
                        <li className="nav-item">
                            <button className="nav-link btn" onClick={() => onNavigate('reports')}>Reports</button>
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
function Dashboard({ stats, clients, plans, staffs, birthdayClients, dueMembers, loading, error, onNavigate }) {
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
                <div className="col-md-2 mb-4">
                    <div 
                        className="stat-card blue clickable" 
                        onClick={() => window.handleFilteredNavigation('clients', 'all')}
                        style={{ cursor: 'pointer' }}
                    >
                        <h3>{stats.total_members}</h3>
                        <p>Total Members</p>
                    </div>
                </div>
                <div className="col-md-2 mb-4">
                    <div 
                        className="stat-card green clickable" 
                        onClick={() => window.handleFilteredNavigation('clients', 'active')}
                        style={{ cursor: 'pointer' }}
                    >
                        <h3>{stats.active_members}</h3>
                        <p>Active Members</p>
                    </div>
                </div>
                <div className="col-md-2 mb-4">
                    <div 
                        className="stat-card orange clickable" 
                        onClick={() => window.handleFilteredNavigation('clients', 'expiring')}
                        style={{ cursor: 'pointer' }}
                    >
                        <h3>{stats.expiring_in_10_days}</h3>
                        <p>Expiring in 10 Days</p>
                    </div>
                </div>
                <div className="col-md-2 mb-4">
                    <div 
                        className="stat-card red clickable" 
                        onClick={() => window.handleFilteredNavigation('clients', 'expired')}
                        style={{ cursor: 'pointer' }}
                    >
                        <h3>{stats.expired_in_last_30_days}</h3>
                        <p>Expired in 30 Days</p>
                    </div>
                </div>
                <div className="col-md-2 mb-4">
                    <div 
                        className="stat-card purple clickable" 
                        onClick={() => onNavigate('leads')}
                        style={{ cursor: 'pointer' }}
                    >
                        <h3>{stats.total_leads}</h3>
                        <p>Total Leads</p>
                    </div>
                </div>
                <div className="col-md-2 mb-4">
                    <div 
                        className="stat-card yellow clickable" 
                        onClick={() => window.handleFilteredNavigation('clients', 'all')}
                        style={{ cursor: 'pointer' }}
                    >
                        <h3>{stats.birthdays_today}</h3>
                        <p>Birthdays Today</p>
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
                            <h5>Today's Birthdays</h5>
                        </div>
                        <div className="card-body">
                            {birthdayClients.length > 0 ? (
                                <table className="table table-striped">
                                    <thead>
                                        <tr>
                                            <th>Name</th>
                                            <th>Email</th>
                                            <th>Phone</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {birthdayClients.map(client => (
                                            <tr key={client.id}>
                                                <td>{client.clientname}</td>
                                                <td>{client.email}</td>
                                                <td>{client.phonenumber}</td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            ) : (
                                <p>No birthdays today.</p>
                            )}
                        </div>
                    </div>
                </div>
            </div>
            
            {/* Due Members Section */}
            <div className="row mt-4">
                <div className="col-12">
                    <div className="card">
                        <div className="card-header">
                            <h5>Members with Pending Payments</h5>
                        </div>
                        <div className="card-body">
                            {dueMembers.length > 0 ? (
                                <table className="table table-striped">
                                    <thead>
                                        <tr>
                                            <th>Client ID</th>
                                            <th>Name</th>
                                            <th>Phone Number</th>
                                            <th>Balance Amount ($)</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {dueMembers.map(member => (
                                            <tr key={member.id}>
                                                <td>{member.id}</td>
                                                <td>{member.clientname}</td>
                                                <td>{member.phonenumber}</td>
                                                <td>${member.balance_due.toFixed(2)}</td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            ) : (
                                <p>All members are up to date with their payments.</p>
                            )}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}

// Clients component
function Clients({ clients, plans, onRefresh, loading, error, filterStatus, onFilterChange }) {
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
    
    // State for renewal modal
    const [showRenewalModal, setShowRenewalModal] = useState(false);
    const [renewalClientId, setRenewalClientId] = useState(null);
    const [renewalClientName, setRenewalClientName] = '';

    // State for edit modal
    const [showEditModal, setShowEditModal] = useState(false);
    const [editingClient, setEditingClient] = useState(null);
    
    // Helper function to check if a client is expired
    const isClientExpired = (client) => {
        if (!client.end_date) return false;
        const endDate = new Date(client.end_date);
        const today = new Date();
        return endDate < today;
    };

    // Helper function to check if a client is active
    const isClientActive = (client) => {
        if (!client.end_date) return false;
        const endDate = new Date(client.end_date);
        const today = new Date();
        return endDate >= today;
    };
    
    // Handle edit client
    const handleEditClient = (client) => {
        setEditingClient(client);
        setShowEditModal(true);
    };
    
    // Handle edit submit
    const handleEditSubmit = async (e) => {
        e.preventDefault();
        const formData = new FormData(e.target);
        const clientData = {
            clientname: formData.get('clientname'),
            email: formData.get('email'),
            phonenumber: formData.get('phonenumber'),
            dateofbirth: formData.get('dateofbirth'),
            gender: formData.get('gender'),
            bloodgroup: formData.get('bloodgroup'),
            address: formData.get('address'),
            notes: formData.get('notes'),
            height: parseFloat(formData.get('height')),
            weight: parseFloat(formData.get('weight'))
            // Removed plan_id and start_date as they should not be editable
        };
        
        try {
            await apiCall(`/clients/${editingClient.id}`, {
                method: 'PUT',
                body: JSON.stringify(clientData)
            });
            
            // Close modal
            setShowEditModal(false);
            setEditingClient(null);
            
            // Refresh data
            onRefresh();
            
            alert('Client updated successfully!');
        } catch (err) {
            alert('Failed to update client: ' + err.message);
        }
    };
    
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
            const phoneNumber = parseInt(clientForm.phonenumber);
            if (isNaN(phoneNumber)) {
                alert('Please enter a valid phone number');
                return;
            }
            
            const height = parseFloat(clientForm.height);
            if (isNaN(height)) {
                alert('Please enter a valid height');
                return;
            }
            
            const weight = parseFloat(clientForm.weight);
            if (isNaN(weight)) {
                alert('Please enter a valid weight');
                return;
            }
            
            const planId = parseInt(clientForm.plan_id);
            if (isNaN(planId)) {
                alert('Please select a valid plan');
                return;
            }
            
            const clientData = {
                ...clientForm,
                phonenumber: phoneNumber,
                height: height,
                weight: weight,
                plan_id: planId
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

    const handleRenewal = (clientId, clientName) => {
        setShowRenewalModal(true);
        setRenewalClientId(clientId);
        setRenewalClientName(clientName);
    };

    const handleRenewalSubmit = async (e) => {
        e.preventDefault();
        const renewalDate = e.target.renewalDate.value;
        const renewalPlanId = parseInt(e.target.renewalPlanId.value);
        if (isNaN(renewalPlanId)) {
            alert('Please select a valid plan');
            return;
        }
        
        try {
            await apiCall(`/clients/${renewalClientId}/renew`, {
                method: 'POST',
                body: JSON.stringify({
                    start_date: renewalDate,
                    plan_id: renewalPlanId
                })
            });
            
            // Close modal
            setShowRenewalModal(false);
            
            // Refresh data
            onRefresh();
            
            alert('Client renewed successfully!');
        } catch (err) {
            alert('Failed to renew client: ' + err.message);
        }
    };

    if (loading) return <div>Loading clients...</div>;
    if (error) return <div className="alert alert-danger">Error: {error}</div>;

    return (
        <div>
            <h2>Clients</h2>
            
            {/* Edit Modal */}
            {showEditModal && editingClient && (
                <div className="modal show d-block" tabIndex="-1" style={{ backgroundColor: 'rgba(0,0,0,0.5)' }}>
                    <div className="modal-dialog modal-lg">
                        <div className="modal-content">
                            <div className="modal-header">
                                <h5 className="modal-title">Edit Client: {editingClient.clientname}</h5>
                                <button type="button" className="btn-close" onClick={() => setShowEditModal(false)}></button>
                            </div>
                            <form onSubmit={handleEditSubmit}>
                                <div className="modal-body">
                                    <div className="row">
                                        <div className="col-md-6 mb-3">
                                            <label className="form-label">Name</label>
                                            <input
                                                type="text"
                                                className="form-control"
                                                name="clientname"
                                                defaultValue={editingClient.clientname}
                                                required
                                            />
                                        </div>
                                        <div className="col-md-6 mb-3">
                                            <label className="form-label">Email</label>
                                            <input
                                                type="email"
                                                className="form-control"
                                                name="email"
                                                defaultValue={editingClient.email}
                                                required
                                            />
                                        </div>
                                    </div>
                                    <div className="row">
                                        <div className="col-md-6 mb-3">
                                            <label className="form-label">Phone Number</label>
                                            <input
                                                type="text"
                                                className="form-control"
                                                name="phonenumber"
                                                defaultValue={editingClient.phonenumber}
                                                required
                                            />
                                        </div>
                                        <div className="col-md-6 mb-3">
                                            <label className="form-label">Date of Birth</label>
                                            <input
                                                type="date"
                                                className="form-control"
                                                name="dateofbirth"
                                                defaultValue={editingClient.dateofbirth}
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
                                                defaultValue={editingClient.gender}
                                                required
                                            >
                                                <option value="">Select</option>
                                                <option value="male">Male</option>
                                                <option value="female">Female</option>
                                                <option value="other">Other</option>
                                            </select>
                                        </div>
                                        <div className="col-md-6 mb-3">
                                            <label className="form-label">Blood Group</label>
                                            <input
                                                type="text"
                                                className="form-control"
                                                name="bloodgroup"
                                                defaultValue={editingClient.bloodgroup}
                                            />
                                        </div>
                                    </div>
                                    <div className="row">
                                        <div className="col-md-6 mb-3">
                                            <label className="form-label">Height (cm)</label>
                                            <input
                                                type="number"
                                                className="form-control"
                                                name="height"
                                                defaultValue={editingClient.height}
                                                required
                                            />
                                        </div>
                                        <div className="col-md-6 mb-3">
                                            <label className="form-label">Weight (kg)</label>
                                            <input
                                                type="number"
                                                className="form-control"
                                                name="weight"
                                                defaultValue={editingClient.weight}
                                                required
                                            />
                                        </div>
                                    </div>
                                    <div className="mb-3">
                                        <label className="form-label">Address</label>
                                        <textarea
                                            className="form-control"
                                            name="address"
                                            defaultValue={editingClient.address}
                                            rows="3"
                                        ></textarea>
                                    </div>
                                    <div className="mb-3">
                                        <label className="form-label">Notes</label>
                                        <textarea
                                            className="form-control"
                                            name="notes"
                                            defaultValue={editingClient.notes}
                                            rows="3"
                                        ></textarea>
                                    </div>
                                    <div className="alert alert-info">
                                        <strong>Plan Information:</strong> Plan and start date cannot be edited. To change the plan, use the Renew button.
                                        <br />
                                        Current Plan: {editingClient.planname}
                                        <br />
                                        Start Date: {editingClient.start_date}
                                        <br />
                                        End Date: {editingClient.end_date}
                                    </div>
                                </div>
                                <div className="modal-footer">
                                    <button type="button" className="btn btn-secondary" onClick={() => setShowEditModal(false)}>Cancel</button>
                                    <button type="submit" className="btn btn-primary">Save Changes</button>
                                </div>
                            </form>
                        </div>
                    </div>
                </div>
            )}
            
            {/* Renewal Modal */}
            {showRenewalModal && (
                <div className="modal show d-block" tabIndex="-1" style={{ backgroundColor: 'rgba(0,0,0,0.5)' }}>
                    <div className="modal-dialog">
                        <div className="modal-content">
                            <div className="modal-header">
                                <h5 className="modal-title">Renew Subscription for {renewalClientName}</h5>
                                <button type="button" className="btn-close" onClick={() => setShowRenewalModal(false)}></button>
                            </div>
                            <form onSubmit={handleRenewalSubmit}>
                                <div className="modal-body">
                                    <div className="mb-3">
                                        <label className="form-label">New Plan</label>
                                        <select className="form-select" name="renewalPlanId" required>
                                            <option value="">Select a plan</option>
                                            {plans.map(plan => (
                                                <option key={plan.id} value={plan.id}>{plan.planname}</option>
                                            ))}
                                        </select>
                                    </div>
                                    <div className="mb-3">
                                        <label className="form-label">Start Date</label>
                                        <input 
                                            type="date" 
                                            className="form-control" 
                                            name="renewalDate" 
                                            defaultValue={new Date().toISOString().split('T')[0]}
                                            required 
                                        />
                                    </div>
                                </div>
                                <div className="modal-footer">
                                    <button type="button" className="btn btn-secondary" onClick={() => setShowRenewalModal(false)}>Cancel</button>
                                    <button type="submit" className="btn btn-primary">Renew Subscription</button>
                                </div>
                            </form>
                        </div>
                    </div>
                </div>
            )}

            <div className="row mb-4">
                <div className="col-12">
                    <div className="card">
                        <div className="card-header">
                            <h5>Client List</h5>
                        </div>
                        <div className="card-body">
                            <table className="table table-striped">
                                <thead>
                                    <tr>
                                        <th>Name</th>
                                        <th>Email</th>
                                        <th>Phone</th>
                                        <th>Plan</th>
                                        <th>Status</th>
                                        <th>Actions</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {clients.map(client => (
                                        <tr key={client.id}>
                                            <td>{client.clientname}</td>
                                            <td>{client.email}</td>
                                            <td>{client.phonenumber}</td>
                                            <td>{client.planname}</td>
                                            <td>
                                                {isClientActive(client) ? 'Active' : 'Expired'}
                                            </td>
                                            <td>
                                                {isClientExpired(client) && (
                                                    <button className="btn btn-sm btn-primary me-1" onClick={() => handleRenewal(client.id, client.clientname)}>Renew</button>
                                                )}
                                                <button className="btn btn-sm btn-warning me-1" onClick={() => handleEditClient(client)}>Edit</button>
                                                <button className="btn btn-sm btn-danger" onClick={() => handleDeleteClient(client.id)}>Delete</button>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
            
            <div className="row">
                <div className="col-12">
                    <div className="card">
                        <div className="card-header">
                            <h5>Add New Client</h5>
                        </div>
                        <div className="card-body">
                            <form onSubmit={handleAddClient}>
                                <div className="mb-3">
                                    <label className="form-label">Name</label>
                                    <input
                                        type="text"
                                        className="form-control"
                                        name="clientname"
                                        value={clientForm.clientname}
                                        onChange={handleClientFormChange}
                                        required
                                    />
                                </div>
                                <div className="mb-3">
                                    <label className="form-label">Email</label>
                                    <input
                                        type="email"
                                        className="form-control"
                                        name="email"
                                        value={clientForm.email}
                                        onChange={handleClientFormChange}
                                        required
                                    />
                                </div>
                                <div className="mb-3">
                                    <label className="form-label">Phone Number</label>
                                    <input
                                        type="text"
                                        className="form-control"
                                        name="phonenumber"
                                        value={clientForm.phonenumber}
                                        onChange={handleClientFormChange}
                                        required
                                    />
                                </div>
                                <div className="mb-3">
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
                                <div className="mb-3">
                                    <label className="form-label">Gender</label>
                                    <select
                                        className="form-select"
                                        name="gender"
                                        value={clientForm.gender}
                                        onChange={handleClientFormChange}
                                        required
                                    >
                                        <option value="">Select</option>
                                        <option value="male">Male</option>
                                        <option value="female">Female</option>
                                        <option value="other">Other</option>
                                    </select>
                                </div>
                                <div className="mb-3">
                                    <label className="form-label">Blood Group</label>
                                    <input
                                        type="text"
                                        className="form-control"
                                        name="bloodgroup"
                                        value={clientForm.bloodgroup}
                                        onChange={handleClientFormChange}
                                    />
                                </div>
                                <div className="mb-3">
                                    <label className="form-label">Address</label>
                                    <textarea
                                        className="form-control"
                                        name="address"
                                        value={clientForm.address}
                                        onChange={handleClientFormChange}
                                    ></textarea>
                                </div>
                                <div className="mb-3">
                                    <label className="form-label">Notes</label>
                                    <textarea
                                        className="form-control"
                                        name="notes"
                                        value={clientForm.notes}
                                        onChange={handleClientFormChange}
                                    ></textarea>
                                </div>
                                <div className="mb-3">
                                    <label className="form-label">Height (cm)</label>
                                    <input
                                        type="number"
                                        className="form-control"
                                        name="height"
                                        value={clientForm.height}
                                        onChange={handleClientFormChange}
                                        required
                                    />
                                </div>
                                <div className="mb-3">
                                    <label className="form-label">Weight (kg)</label>
                                    <input
                                        type="number"
                                        className="form-control"
                                        name="weight"
                                        value={clientForm.weight}
                                        onChange={handleClientFormChange}
                                        required
                                    />
                                </div>
                                <div className="mb-3">
                                    <label className="form-label">Plan</label>
                                    <select
                                        className="form-select"
                                        name="plan_id"
                                        value={clientForm.plan_id}
                                        onChange={handleClientFormChange}
                                        required
                                    >
                                        <option value="">Select</option>
                                        {plans.map(plan => (
                                            <option key={plan.id} value={plan.id}>{plan.planname}</option>
                                        ))}
                                    </select>
                                </div>
                                <div className="mb-3">
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
                                <button type="submit" className="btn btn-primary">Add Client</button>
                            </form>
                        </div>
                    </div>
                </div>
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
            const days = parseInt(planForm.days);
            if (isNaN(days)) {
                alert('Please enter a valid number of days');
                return;
            }
            
            const amount = parseFloat(planForm.amount);
            if (isNaN(amount)) {
                alert('Please enter a valid amount');
                return;
            }
            
            const planData = {
                ...planForm,
                days: days,
                amount: amount
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
    
    // State for edit modal
    const [showEditModal, setShowEditModal] = useState(false);
    const [editingStaff, setEditingStaff] = useState(null);
    
    const handleStaffFormChange = (e) => {
        const { name, value } = e.target;
        setStaffForm(prev => ({
            ...prev,
            [name]: value
        }));
    };
    
    // Handle edit staff
    const handleEditStaff = (staff) => {
        setEditingStaff(staff);
        setShowEditModal(true);
    };
    
    // Handle edit submit
    const handleEditSubmit = async (e) => {
        e.preventDefault();
        const formData = new FormData(e.target);
        const staffData = {
            staffname: formData.get('staffname'),
            email: formData.get('email'),
            phonenumber: parseInt(formData.get('phonenumber')),
            role: formData.get('role')
        };
        
        try {
            await apiCall(`/staffs/${editingStaff.id}`, {
                method: 'PUT',
                body: JSON.stringify(staffData)
            });
            
            // Close modal
            setShowEditModal(false);
            setEditingStaff(null);
            
            // Refresh data
            onRefresh();
            
            alert('Staff member updated successfully!');
        } catch (err) {
            alert('Failed to update staff member: ' + err.message);
        }
    };
    
    const handleAddStaff = async (e) => {
        e.preventDefault();
        try {
            // Convert form data to correct types
            const phoneNumber = parseInt(staffForm.phonenumber);
            if (isNaN(phoneNumber)) {
                alert('Please enter a valid phone number');
                return;
            }
            
            const staffData = {
                ...staffForm,
                phonenumber: phoneNumber
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
            
            alert('Staff member added successfully!');
        } catch (err) {
            alert('Failed to add staff member: ' + err.message);
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
            
            alert('Staff member deleted successfully!');
        } catch (err) {
            alert('Failed to delete staff member: ' + err.message);
        }
    };

    if (loading) return <div>Loading staff...</div>;
    if (error) return <div className="alert alert-danger">Error: {error}</div>;

    return (
        <div>
            <h2>Staff Management</h2>
            
            {/* Edit Modal */}
            {showEditModal && editingStaff && (
                <div className="modal show d-block" tabIndex="-1" style={{ backgroundColor: 'rgba(0,0,0,0.5)' }}>
                    <div className="modal-dialog">
                        <div className="modal-content">
                            <div className="modal-header">
                                <h5 className="modal-title">Edit Staff Member: {editingStaff.staffname}</h5>
                                <button type="button" className="btn-close" onClick={() => setShowEditModal(false)}></button>
                            </div>
                            <form onSubmit={handleEditSubmit}>
                                <div className="modal-body">
                                    <div className="mb-3">
                                        <label className="form-label">Full Name</label>
                                        <input 
                                            type="text" 
                                            className="form-control" 
                                            name="staffname"
                                            defaultValue={editingStaff.staffname}
                                            placeholder="Enter full name" 
                                            required
                                        />
                                    </div>
                                    <div className="mb-3">
                                        <label className="form-label">Email</label>
                                        <input 
                                            type="email" 
                                            className="form-control" 
                                            name="email"
                                            defaultValue={editingStaff.email}
                                            placeholder="Enter email" 
                                            required
                                        />
                                    </div>
                                    <div className="mb-3">
                                        <label className="form-label">Phone Number</label>
                                        <input 
                                            type="tel" 
                                            className="form-control" 
                                            name="phonenumber"
                                            defaultValue={editingStaff.phonenumber}
                                            placeholder="Enter phone number" 
                                            required
                                        />
                                    </div>
                                    <div className="mb-3">
                                        <label className="form-label">Role</label>
                                        <input 
                                            type="text" 
                                            className="form-control" 
                                            name="role"
                                            defaultValue={editingStaff.role}
                                            placeholder="Enter role" 
                                            required
                                        />
                                    </div>
                                </div>
                                <div className="modal-footer">
                                    <button type="button" className="btn btn-secondary" onClick={() => setShowEditModal(false)}>Cancel</button>
                                    <button type="submit" className="btn btn-primary">Save Changes</button>
                                </div>
                            </form>
                        </div>
                    </div>
                </div>
            )}
            
            <div className="form-container">
                <h4>Add New Staff Member</h4>
                <form onSubmit={handleAddStaff}>
                    <div className="row">
                        <div className="col-md-3 mb-3">
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
                        <div className="col-md-3 mb-3">
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
                        <div className="col-md-3 mb-3">
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
                        <div className="col-md-3 mb-3">
                            <label className="form-label">Role</label>
                            <input 
                                type="text" 
                                className="form-control" 
                                name="role"
                                value={staffForm.role}
                                onChange={handleStaffFormChange}
                                placeholder="Enter role" 
                                required
                            />
                        </div>
                    </div>
                    <button type="submit" className="btn btn-primary">Add Staff Member</button>
                </form>
            </div>
            
            <div className="table-container">
                <h4>All Staff Members</h4>
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
                                <td>{staff.phonenumber}</td>
                                <td>{staff.role}</td>
                                <td>
                                    <button className="btn btn-sm btn-outline-primary me-1" onClick={() => handleEditStaff(staff)}>Edit</button>
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
function Payments({ clients, onRefresh, loading, error }) {
    const [paymentForm, setPaymentForm] = useState({
        client_id: '',
        amount: '',
        paid_at: new Date().toISOString().split('T')[0],
        note: '',
        method: 'Cash'
    });
    
    const [paymentHistory, setPaymentHistory] = useState([]);
    const [selectedClientId, setSelectedClientId] = useState('');
    const [recentPayments, setRecentPayments] = useState([]);

    const handlePaymentFormChange = (e) => {
        const { name, value } = e.target;
        setPaymentForm(prev => ({
            ...prev,
            [name]: value
        }));
    };
    
    const handleClientSelect = (clientId) => {
        // Convert clientId to string for comparison since it might come as a number
        const clientIdStr = clientId.toString();
        console.log('Client selected:', clientIdStr);
        setSelectedClientId(clientIdStr);
        setPaymentForm(prev => ({
            ...prev,
            client_id: clientIdStr
        }));
        
        // Load payment history for selected client
        if (clientIdStr) {
            loadPaymentHistory(clientIdStr);
        }
    };

    const loadPaymentHistory = async (clientId) => {
        console.log('Loading payment history for client:', clientId);
        try {
            const response = await apiCall(`/payments/?client_id=${clientId}`);
            console.log('Payment history response:', response);
            setPaymentHistory(response.payments || []);
        } catch (err) {
            console.error('Failed to load payment history:', err);
            setPaymentHistory([]);
        }
    };
    
    const loadRecentPayments = async () => {
        try {
            const response = await apiCall('/payments/');
            setRecentPayments(response.payments.slice(0, 10) || []); // Get last 10 payments
        } catch (err) {
            console.error('Failed to load recent payments:', err);
            setRecentPayments([]);
        }
    };

    const handleAddPayment = async (e) => {
        e.preventDefault();
        try {
            // Convert form data to correct types
            const clientId = parseInt(paymentForm.client_id);
            if (isNaN(clientId)) {
                alert('Please select a valid client');
                return;
            }
            
            const amount = parseFloat(paymentForm.amount);
            if (isNaN(amount)) {
                alert('Please enter a valid amount');
                return;
            }
            
            const paymentData = {
                ...paymentForm,
                client_id: clientId,
                amount: amount
            };
            
            const response = await apiCall('/payments/', {
                method: 'POST',
                body: JSON.stringify(paymentData)
            });
            
            // Show warning if overpayment
            let message = 'Payment recorded successfully!';
            if (response.overpayment) {
                message += `\nWarning: Client has overpaid by $${Math.abs(response.balance_due).toFixed(2)}`;
            } else if (response.balance_due <= 0) {
                message += '\nClient payment is now complete!';
            } else {
                message += `\nBalance due: $${response.balance_due.toFixed(2)}`;
            }
            
            // Reset form
            setPaymentForm({
                client_id: '',
                amount: '',
                paid_at: new Date().toISOString().split('T')[0],
                note: '',
                method: 'Cash'
            });
            
            // Clear selected client
            setSelectedClientId('');
            setPaymentHistory([]);
            
            // Refresh data
            onRefresh();
            loadRecentPayments(); // Refresh recent payments
            
            alert(message);
        } catch (err) {
            alert('Failed to record payment: ' + err.message);
        }
    };

    const handleDeletePayment = async (paymentId) => {
        if (!window.confirm('Are you sure you want to delete this payment?')) return;
        
        try {
            await apiCall(`/payments/${paymentId}`, {
                method: 'DELETE'
            });
            
            // Refresh data
            onRefresh();
            loadRecentPayments(); // Refresh recent payments
            
            // Reload payment history if a client is selected
            if (selectedClientId) {
                loadPaymentHistory(selectedClientId);
            }
            
            alert('Payment deleted successfully!');
        } catch (err) {
            alert('Failed to delete payment: ' + err.message);
        }
    };
    
    // Load recent payments when component mounts
    useEffect(() => {
        loadRecentPayments();
    }, []);

    if (loading) return <div>Loading payments...</div>;
    if (error) return <div className="alert alert-danger">Error: {error}</div>;

    // Get client details for selected client
    const selectedClient = clients && clients.find(client => client.id.toString() === selectedClientId) || null;
    
    // Get client name by ID for recent payments
    const getClientName = (clientId) => {
        if (!clients) return `Client ${clientId}`;
        const client = clients.find(c => c.id.toString() === clientId.toString());
        return client ? client.clientname : `Client ${clientId}`;
    };

    return (
        <div>
            <h2>Payment Management</h2>
            <div className="form-container">
                <h4>Record New Payment</h4>
                <form onSubmit={handleAddPayment}>
                    <div className="row">
                        <div className="col-md-6 mb-3">
                            <label className="form-label">Select Client</label>
                            <select 
                                className="form-select" 
                                name="client_id"
                                value={paymentForm.client_id}
                                onChange={(e) => handleClientSelect(e.target.value)}
                                required
                            >
                                <option value="">Select a client</option>
                                {clients && clients.map(client => (
                                    <option key={client.id} value={client.id}>
                                        {client.clientname} (ID: {client.id}) - ${client.amount} plan
                                    </option>
                                ))}
                            </select>
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
                    {selectedClient && (
                        <div className="row mb-3">
                            <div className="col-md-12">
                                <div className="alert alert-info">
                                    <div className="row">
                                        <div className="col-md-6">
                                            <strong>Client:</strong> {selectedClient.clientname} (ID: {selectedClient.id})<br/>
                                            <strong>Plan:</strong> {selectedClient.planname} (${selectedClient.amount})<br/>
                                        </div>
                                        <div className="col-md-6">
                                            <strong>Total Paid:</strong> ${selectedClient.total_paid.toFixed(2)}<br/>
                                            <strong>Balance Due:</strong> ${selectedClient.balance_due.toFixed(2)}
                                            {selectedClient.balance_due < 0 && (
                                                <span className="text-danger"> (Overpaid by ${Math.abs(selectedClient.balance_due).toFixed(2)})</span>
                                            )}
                                            {selectedClient.balance_due <= 0 && selectedClient.balance_due >= 0 && (
                                                <span className="text-success"> (Payment Complete)</span>
                                            )}
                                            {selectedClient.balance_due > 0 && (
                                                <span className="text-warning"> (Payment Pending)</span>
                                            )}
                                        </div>
                                    </div>
                                    <div className="row mt-2">
                                        <div className="col-md-12">
                                            <strong>Payment Status:</strong> 
                                            {selectedClient.balance_due <= 0 ? (
                                                selectedClient.balance_due < 0 ? (
                                                    <span className="badge bg-danger ms-2">Overpaid</span>
                                                ) : (
                                                    <span className="badge bg-success ms-2">Paid</span>
                                                )
                                            ) : (
                                                <span className="badge bg-warning ms-2">Pending (${selectedClient.balance_due.toFixed(2)} due)</span>
                                            )}
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    )}
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
            
            {selectedClientId && (
                <div className="table-container mt-4">
                    <h4>Payment History for {selectedClient?.clientname || 'Selected Client'}</h4>
                    {paymentHistory.length > 0 ? (
                        <table className="table table-striped">
                            <thead>
                                <tr>
                                    <th>ID</th>
                                    <th>Date</th>
                                    <th>Amount</th>
                                    <th>Method</th>
                                    <th>Note</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                {paymentHistory.map(payment => (
                                    <tr key={payment.id}>
                                        <td>{payment.id}</td>
                                        <td>{new Date(payment.paid_at).toLocaleDateString()}</td>
                                        <td>${payment.amount.toFixed(2)}</td>
                                        <td>{payment.method}</td>
                                        <td>{payment.note || '-'}</td>
                                        <td>
                                            <button 
                                                className="btn btn-sm btn-outline-danger"
                                                onClick={() => handleDeletePayment(payment.id)}
                                            >
                                                Delete
                                            </button>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    ) : (
                        <p>No payment history found for this client.</p>
                    )}
                </div>
            )}
            
            <div className="table-container mt-4">
                <h4>Recent Payments</h4>
                {recentPayments.length > 0 ? (
                    <table className="table table-striped">
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Client</th>
                                <th>Date</th>
                                <th>Amount</th>
                                <th>Method</th>
                            </tr>
                        </thead>
                        <tbody>
                            {recentPayments.map(payment => (
                                <tr key={payment.id}>
                                    <td>{payment.id}</td>
                                    <td>{getClientName(payment.client_id)} (ID: {payment.client_id})</td>
                                    <td>{new Date(payment.paid_at).toLocaleDateString()}</td>
                                    <td>${payment.amount.toFixed(2)}</td>
                                    <td>{payment.method}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                ) : (
                    <p>No recent payments found.</p>
                )}
            </div>
        </div>
    );
}

// Leads component
function Leads({ leads, onRefresh, loading, error }) {
    const [leadForm, setLeadForm] = useState({
        name: '',
        phonenumber: '',
        notes: ''
    });

    const handleLeadFormChange = (e) => {
        const { name, value } = e.target;
        setLeadForm(prev => ({
            ...prev,
            [name]: value
        }));
    };

    const handleAddLead = async (e) => {
        e.preventDefault();
        try {
            // Convert form data to correct types
            const phoneNumber = parseInt(leadForm.phonenumber);
            if (isNaN(phoneNumber)) {
                alert('Please enter a valid phone number');
                return;
            }
            
            const leadData = {
                ...leadForm,
                phonenumber: phoneNumber
            };
            
            await apiCall('/leads/', {
                method: 'POST',
                body: JSON.stringify(leadData)
            });
            
            // Reset form
            setLeadForm({
                name: '',
                phonenumber: '',
                notes: ''
            });
            
            // Refresh data
            onRefresh();
            
            alert('Lead added successfully!');
        } catch (err) {
            alert('Failed to add lead: ' + err.message);
        }
    };

    const handleDeleteLead = async (leadId) => {
        if (!window.confirm('Are you sure you want to delete this lead?')) return;
        
        try {
            await apiCall(`/leads/${leadId}`, {
                method: 'DELETE'
            });
            
            // Refresh data
            onRefresh();
            
            alert('Lead deleted successfully!');
        } catch (err) {
            alert('Failed to delete lead: ' + err.message);
        }
    };

    if (loading) return <div>Loading leads...</div>;
    if (error) return <div className="alert alert-danger">Error: {error}</div>;

    return (
        <div>
            <h2>Lead Management</h2>
            <div className="form-container">
                <h4>Add New Lead</h4>
                <form onSubmit={handleAddLead}>
                    <div className="row">
                        <div className="col-md-4 mb-3">
                            <label className="form-label">Full Name</label>
                            <input 
                                type="text" 
                                className="form-control" 
                                name="name"
                                value={leadForm.name}
                                onChange={handleLeadFormChange}
                                placeholder="Enter full name" 
                                required
                            />
                        </div>
                        <div className="col-md-4 mb-3">
                            <label className="form-label">Phone Number</label>
                            <input 
                                type="tel" 
                                className="form-control" 
                                name="phonenumber"
                                value={leadForm.phonenumber}
                                onChange={handleLeadFormChange}
                                placeholder="Enter phone number" 
                                required
                            />
                        </div>
                        <div className="col-md-4 mb-3">
                            <label className="form-label">Notes</label>
                            <textarea 
                                className="form-control" 
                                name="notes"
                                value={leadForm.notes}
                                onChange={handleLeadFormChange}
                                rows="3" 
                                placeholder="Enter any notes"
                            />
                        </div>
                    </div>
                    <button type="submit" className="btn btn-primary">Add Lead</button>
                </form>
            </div>
            
            <div className="table-container">
                <h4>All Leads</h4>
                <table className="table table-striped">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Name</th>
                            <th>Phone</th>
                            <th>Notes</th>
                            <th>Created At</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {leads.map(lead => (
                            <tr key={lead.id}>
                                <td>{lead.id}</td>
                                <td>{lead.name}</td>
                                <td>{lead.phonenumber}</td>
                                <td>{lead.notes || '-'}</td>
                                <td>{new Date(lead.created_at).toLocaleDateString()}</td>
                                <td>
                                    <button className="btn btn-sm btn-outline-primary me-1">Convert</button>
                                    <button 
                                        className="btn btn-sm btn-outline-danger"
                                        onClick={() => handleDeleteLead(lead.id)}
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

// Reports component
function Reports({ onRefresh, loading, error }) {
    const [revenueData, setRevenueData] = useState([]);
    const [planRevenueData, setPlanRevenueData] = useState([]);
    const [growthData, setGrowthData] = useState([]);
    const [planDistributionData, setPlanDistributionData] = useState([]);
    const [paymentMethodsData, setPaymentMethodsData] = useState([]);
    const [membershipStatusData, setMembershipStatusData] = useState([]);
    const [ageDistributionData, setAgeDistributionData] = useState([]);
    const [genderDistributionData, setGenderDistributionData] = useState([]);
    const [revenuePeriod, setRevenuePeriod] = useState('monthly');
    const [growthPeriod, setGrowthPeriod] = useState('monthly');
    
    // View modes for each chart (visual or text)
    const [viewModes, setViewModes] = useState({
        revenue: 'visual',
        planRevenue: 'visual',
        planDistribution: 'visual',
        growth: 'visual',
        paymentMethods: 'visual',
        membershipStatus: 'visual',
        ageDistribution: 'visual',
        genderDistribution: 'visual'
    });

    // Fetch all report data
    const fetchReportData = async () => {
        try {
            // Fetch revenue data
            const revenueResponse = await apiCall(`/reports/revenue?period=${revenuePeriod}`);
            setRevenueData(revenueResponse.revenue_data || []);
            
            // Fetch revenue by plan
            const planRevenueResponse = await apiCall('/reports/revenue-by-plan');
            setPlanRevenueData(planRevenueResponse.plan_revenue || []);
            
            // Fetch client growth data
            const growthResponse = await apiCall(`/reports/client-growth?period=${growthPeriod}`);
            setGrowthData(growthResponse.growth_data || []);
            
            // Fetch plan distribution
            const planDistributionResponse = await apiCall('/reports/plan-distribution');
            setPlanDistributionData(planDistributionResponse.plan_distribution || []);
            
            // Fetch payment methods
            const paymentMethodsResponse = await apiCall('/reports/payment-methods');
            setPaymentMethodsData(paymentMethodsResponse.payment_methods || []);
            
            // Fetch membership status
            const membershipStatusResponse = await apiCall('/reports/membership-status');
            setMembershipStatusData(membershipStatusResponse.membership_status || []);
            
            // Fetch age distribution
            const ageDistributionResponse = await apiCall('/reports/age-distribution');
            setAgeDistributionData(ageDistributionResponse.age_distribution || []);
            
            // Fetch gender distribution
            const genderDistributionResponse = await apiCall('/reports/gender-distribution');
            setGenderDistributionData(genderDistributionResponse.gender_distribution || []);
        } catch (err) {
            console.error('Failed to fetch report data:', err);
            // Set all data states to empty arrays to prevent undefined errors
            setRevenueData([]);
            setPlanRevenueData([]);
            setGrowthData([]);
            setPlanDistributionData([]);
            setPaymentMethodsData([]);
            setMembershipStatusData([]);
            setAgeDistributionData([]);
            setGenderDistributionData([]);
            // Show error message to user
            alert('Failed to load report data. Please try again.');
        }
    };

    // Load data when component mounts
    useEffect(() => {
        fetchReportData();
    }, [revenuePeriod, growthPeriod]);
    
    // Render charts when data changes
    useEffect(() => {
        // Only render if Plotly is available
        if (typeof window.Plotly === 'undefined') {
            console.error('Plotly is not loaded');
            return;
        }
        
        // Small delay to ensure DOM is ready
        const timer = setTimeout(() => {
            // Function to render a single chart with retries
            const renderChartWithRetry = (elementId, chartData, layout, maxRetries = 3) => {
                let attempts = 0;
                
                const tryRender = () => {
                    const chartElement = document.getElementById(elementId);
                    if (chartElement) {
                        try {
                            // Clear any existing content
                            chartElement.innerHTML = '';
                            window.Plotly.newPlot(chartElement, chartData, layout);
                        } catch (error) {
                            console.error(`Error rendering chart ${elementId}:`, error);
                            chartElement.innerHTML = '<div class="alert alert-warning">Unable to render chart. Please try again.</div>';
                        }
                    } else if (attempts < maxRetries) {
                        attempts++;
                        setTimeout(tryRender, 100);
                    } else {
                        console.error(`Could not find element with id ${elementId} after ${maxRetries} attempts`);
                    }
                };
                
                tryRender();
            };
            
            // Render revenue chart
            if (safeRevenueData.length > 0 && window.Plotly) {
                renderChartWithRetry('revenue-chart', revenueChartData, { 
                    title: 'Revenue Overview',
                    xaxis: { title: 'Period' },
                    yaxis: { title: 'Revenue ($)' }
                });
            }
            
            // Render plan revenue chart
            if (safePlanRevenueData.length > 0 && window.Plotly) {
                renderChartWithRetry('plan-revenue-chart', planRevenueChartData, { 
                    title: 'Revenue by Membership Plan',
                    xaxis: { title: 'Plan' },
                    yaxis: { title: 'Revenue ($)' }
                });
            }
            
            // Render plan distribution chart
            if (safePlanDistributionData.length > 0 && window.Plotly) {
                renderChartWithRetry('plan-distribution-chart', planDistributionChartData, { 
                    title: 'Client Distribution by Plan'
                });
            }
            
            // Render growth chart
            if (safeGrowthData.length > 0 && window.Plotly) {
                renderChartWithRetry('growth-chart', growthChartData, { 
                    title: 'New Clients Over Time',
                    xaxis: { title: 'Period' },
                    yaxis: { title: 'New Clients' }
                });
            }
            
            // Render payment methods chart
            if (safePaymentMethodsData.length > 0 && window.Plotly) {
                renderChartWithRetry('payment-methods-chart', paymentMethodsChartData, { 
                    title: 'Payment Methods',
                    xaxis: { title: 'Method' },
                    yaxis: { title: 'Count' }
                });
            }
            
            // Render membership status chart
            if (safeMembershipStatusData.length > 0 && window.Plotly) {
                renderChartWithRetry('membership-status-chart', membershipStatusChartData, { 
                    title: 'Membership Status'
                });
            }
            
            // Render age distribution chart
            if (safeAgeDistributionData.length > 0 && window.Plotly) {
                renderChartWithRetry('age-distribution-chart', ageDistributionChartData, { 
                    title: 'Age Distribution',
                    xaxis: { title: 'Age Group' },
                    yaxis: { title: 'Count' }
                });
            }
            
            // Render gender distribution chart
            if (safeGenderDistributionData.length > 0 && window.Plotly) {
                renderChartWithRetry('gender-distribution-chart', genderDistributionChartData, { 
                    title: 'Gender Distribution'
                });
            }
        }, 100); // 100ms delay
        
        // Cleanup timeout
        return () => clearTimeout(timer);
    }, [revenueData, planRevenueData, planDistributionData, growthData, paymentMethodsData, membershipStatusData, ageDistributionData, genderDistributionData]);

    // Handle period changes
    const handleRevenuePeriodChange = (period) => {
        setRevenuePeriod(period);
    };

    const handleGrowthPeriodChange = (period) => {
        setGrowthPeriod(period);
    };
    
    // Toggle view mode for a chart
    const toggleViewMode = (chartName) => {
        setViewModes(prev => ({
            ...prev,
            [chartName]: prev[chartName] === 'visual' ? 'text' : 'visual'
        }));
    };
    
    // Render Plotly chart
    const renderChart = (chartId, data, layout = {}) => {
        // We'll render the chart container and handle the plotting in useEffect of the Reports component
        return <div id={chartId} style={{ width: '100%', height: '400px' }}></div>;
    };
    
    if (loading) return <div>Loading reports...</div>;
    if (error) return <div className="alert alert-danger">Error: {error}</div>;
    
    // Ensure all data arrays are defined
    const safeRevenueData = Array.isArray(revenueData) ? revenueData : [];
    const safePlanRevenueData = Array.isArray(planRevenueData) ? planRevenueData : [];
    const safeGrowthData = Array.isArray(growthData) ? growthData : [];
    const safePlanDistributionData = Array.isArray(planDistributionData) ? planDistributionData : [];
    const safePaymentMethodsData = Array.isArray(paymentMethodsData) ? paymentMethodsData : [];
    const safeMembershipStatusData = Array.isArray(membershipStatusData) ? membershipStatusData : [];
    const safeAgeDistributionData = Array.isArray(ageDistributionData) ? ageDistributionData : [];
    const safeGenderDistributionData = Array.isArray(genderDistributionData) ? genderDistributionData : [];

    // Chart data preparations
    const revenueChartData = safeRevenueData && safeRevenueData.length > 0 ? [{
        x: safeRevenueData.map(item => item && item.period ? item.period : ''),
        y: safeRevenueData.map(item => item && item.total_revenue !== undefined ? item.total_revenue : 0),
        type: 'bar',
        marker: { color: '#4e73df' }
    }] : [];
    
    const planRevenueChartData = safePlanRevenueData && safePlanRevenueData.length > 0 ? [{
        x: safePlanRevenueData.map(item => item && item.plan_name ? item.plan_name : ''),
        y: safePlanRevenueData.map(item => item && item.total_revenue !== undefined ? item.total_revenue : 0),
        type: 'bar',
        marker: { color: '#1cc88a' }
    }] : [];
    
    const planDistributionChartData = safePlanDistributionData && safePlanDistributionData.length > 0 ? [{
        labels: safePlanDistributionData.map(item => item && item.plan_name ? item.plan_name : ''),
        values: safePlanDistributionData.map(item => item && item.client_count !== undefined ? item.client_count : 0),
        type: 'pie',
        marker: { colors: ['#4e73df', '#1cc88a', '#36b9cc', '#f6c23e', '#e74a3b'] }
    }] : [];
    
    const growthChartData = safeGrowthData && safeGrowthData.length > 0 ? [{
        x: safeGrowthData.map(item => item && item.period ? item.period : ''),
        y: safeGrowthData.map(item => item && item.new_clients !== undefined ? item.new_clients : 0),
        type: 'scatter',
        mode: 'lines+markers',
        line: { color: '#4e73df' },
        marker: { color: '#4e73df' }
    }] : [];
    
    const paymentMethodsChartData = safePaymentMethodsData && safePaymentMethodsData.length > 0 ? [{
        x: safePaymentMethodsData.map(item => item && item.method ? item.method : ''),
        y: safePaymentMethodsData.map(item => item && item.count !== undefined ? item.count : 0),
        type: 'bar',
        marker: { color: '#6f42c1' }
    }] : [];
    
    const membershipStatusChartData = safeMembershipStatusData && safeMembershipStatusData.length > 0 ? [{
        labels: safeMembershipStatusData.map(item => item && item.status ? item.status : ''),
        values: safeMembershipStatusData.map(item => item && item.count !== undefined ? item.count : 0),
        type: 'pie',
        marker: { colors: ['#1cc88a', '#f6c23e', '#e74a3b'] }
    }] : [];
    
    const ageDistributionChartData = safeAgeDistributionData && safeAgeDistributionData.length > 0 ? [{
        x: safeAgeDistributionData.map(item => item && item.age_group ? item.age_group : ''),
        y: safeAgeDistributionData.map(item => item && item.count !== undefined ? item.count : 0),
        type: 'bar',
        marker: { color: '#36b9cc' }
    }] : [];
    
    const genderDistributionChartData = safeGenderDistributionData && safeGenderDistributionData.length > 0 ? [{
        labels: safeGenderDistributionData.map(item => item && item.gender ? item.gender : ''),
        values: safeGenderDistributionData.map(item => item && item.count !== undefined ? item.count : 0),
        type: 'pie',
        marker: { colors: ['#4e73df', '#e74a3b', '#1cc88a'] }
    }] : [];

    return (
        <div>
            <h2>Reports & Analytics</h2>
            
            {/* Revenue Overview */}
            <div className="row mb-4">
                <div className="col-12">
                    <div className="card">
                        <div className="card-header d-flex justify-content-between align-items-center">
                            <h5>Revenue Overview</h5>
                            <div className="d-flex align-items-center">
                                <div className="me-3">
                                    <button 
                                        className={`btn btn-sm ${revenuePeriod === 'daily' ? 'btn-primary' : 'btn-outline-secondary'}`}
                                        onClick={() => handleRevenuePeriodChange('daily')}
                                    >
                                        Daily
                                    </button>
                                    <button 
                                        className={`btn btn-sm mx-2 ${revenuePeriod === 'weekly' ? 'btn-primary' : 'btn-outline-secondary'}`}
                                        onClick={() => handleRevenuePeriodChange('weekly')}
                                    >
                                        Weekly
                                    </button>
                                    <button 
                                        className={`btn btn-sm mx-2 ${revenuePeriod === 'monthly' ? 'btn-primary' : 'btn-outline-secondary'}`}
                                        onClick={() => handleRevenuePeriodChange('monthly')}
                                    >
                                        Monthly
                                    </button>
                                    <button 
                                        className={`btn btn-sm ${revenuePeriod === 'yearly' ? 'btn-primary' : 'btn-outline-secondary'}`}
                                        onClick={() => handleRevenuePeriodChange('yearly')}
                                    >
                                        Yearly
                                    </button>
                                </div>
                                <button 
                                    className="btn btn-sm btn-outline-primary"
                                    onClick={() => toggleViewMode('revenue')}
                                >
                                    {viewModes.revenue === 'visual' ? 'Text View' : 'Visual View'}
                                </button>
                            </div>
                        </div>
                        <div className="card-body">
                            {safeRevenueData.length > 0 ? (
                                viewModes.revenue === 'visual' ? (
                                    <div key="revenue-visual">
                                        {renderChart('revenue-chart', revenueChartData, { 
                                            title: 'Revenue Overview',
                                            xaxis: { title: 'Period' },
                                            yaxis: { title: 'Revenue ($)' }
                                        })}
                                    </div>
                                ) : (
                                    <div key="revenue-text" className="chart-container">
                                        <table className="table table-striped">
                                            <thead>
                                                <tr>
                                                    <th>Period</th>
                                                    <th>Revenue ($)</th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                {safeRevenueData.map((item, index) => (
                                                    <tr key={index}>
                                                        <td>{item && item.period ? item.period : ''}</td>
                                                        <td>${item && item.total_revenue !== undefined ? item.total_revenue.toFixed(2) : '0.00'}</td>
                                                    </tr>
                                                ))}
                                            </tbody>
                                        </table>
                                    </div>
                                )
                            ) : (
                                <p>No revenue data available.</p>
                            )}
                        </div>
                    </div>
                </div>
            </div>
            
            {/* Revenue by Plan */}
            <div className="row mb-4">
                <div className="col-md-6">
                    <div className="card">
                        <div className="card-header d-flex justify-content-between align-items-center">
                            <h5>Revenue by Membership Plan</h5>
                            <button 
                                className="btn btn-sm btn-outline-primary"
                                onClick={() => toggleViewMode('planRevenue')}
                            >
                                {viewModes.planRevenue === 'visual' ? 'Text View' : 'Visual View'}
                            </button>
                        </div>
                        <div className="card-body">
                            {safePlanRevenueData.length > 0 ? (
                                viewModes.planRevenue === 'visual' ? (
                                    <div key="plan-revenue-visual">
                                        {renderChart('plan-revenue-chart', planRevenueChartData, { 
                                            title: 'Revenue by Membership Plan',
                                            xaxis: { title: 'Plan' },
                                            yaxis: { title: 'Revenue ($)' }
                                        })}
                                    </div>
                                ) : (
                                    <div key="plan-revenue-text" className="chart-container">
                                        <table className="table table-striped">
                                            <thead>
                                                <tr>
                                                    <th>Plan</th>
                                                    <th>Revenue ($)</th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                {safePlanRevenueData.map((item, index) => (
                                                    <tr key={index}>
                                                        <td>{item && item.plan_name ? item.plan_name : ''}</td>
                                                        <td>${item && item.total_revenue !== undefined ? item.total_revenue.toFixed(2) : '0.00'}</td>
                                                    </tr>
                                                ))}
                                            </tbody>
                                        </table>
                                    </div>
                                )
                            ) : (
                                <p>No plan revenue data available.</p>
                            )}
                        </div>
                    </div>
                </div>
                
                {/* Plan Distribution */}
                <div className="col-md-6">
                    <div className="card">
                        <div className="card-header d-flex justify-content-between align-items-center">
                            <h5>Client Distribution by Plan</h5>
                            <button 
                                className="btn btn-sm btn-outline-primary"
                                onClick={() => toggleViewMode('planDistribution')}
                            >
                                {viewModes.planDistribution === 'visual' ? 'Text View' : 'Visual View'}
                            </button>
                        </div>
                        <div className="card-body">
                            {safePlanDistributionData.length > 0 ? (
                                viewModes.planDistribution === 'visual' ? (
                                    <div key="plan-distribution-visual">
                                        {renderChart('plan-distribution-chart', planDistributionChartData, { 
                                            title: 'Client Distribution by Plan'
                                        })}
                                    </div>
                                ) : (
                                    <div key="plan-distribution-text" className="chart-container">
                                        <table className="table table-striped">
                                            <thead>
                                                <tr>
                                                    <th>Plan</th>
                                                    <th>Clients</th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                {safePlanDistributionData.map((item, index) => (
                                                    <tr key={index}>
                                                        <td>{item && item.plan_name ? item.plan_name : ''}</td>
                                                        <td>{item && item.client_count !== undefined ? item.client_count : 0}</td>
                                                    </tr>
                                                ))}
                                            </tbody>
                                        </table>
                                    </div>
                                )
                            ) : (
                                <p>No plan distribution data available.</p>
                            )}
                        </div>
                    </div>
                </div>
            </div>
            
            {/* Client Growth */}
            <div className="row mb-4">
                <div className="col-12">
                    <div className="card">
                        <div className="card-header d-flex justify-content-between align-items-center">
                            <h5>New Clients Over Time</h5>
                            <div className="d-flex align-items-center">
                                <div className="me-3">
                                    <button 
                                        className={`btn btn-sm ${growthPeriod === 'daily' ? 'btn-primary' : 'btn-outline-secondary'}`}
                                        onClick={() => handleGrowthPeriodChange('daily')}
                                    >
                                        Daily
                                    </button>
                                    <button 
                                        className={`btn btn-sm mx-2 ${growthPeriod === 'weekly' ? 'btn-primary' : 'btn-outline-secondary'}`}
                                        onClick={() => handleGrowthPeriodChange('weekly')}
                                    >
                                        Weekly
                                    </button>
                                    <button 
                                        className={`btn btn-sm mx-2 ${growthPeriod === 'monthly' ? 'btn-primary' : 'btn-outline-secondary'}`}
                                        onClick={() => handleGrowthPeriodChange('monthly')}
                                    >
                                        Monthly
                                    </button>
                                    <button 
                                        className={`btn btn-sm ${growthPeriod === 'yearly' ? 'btn-primary' : 'btn-outline-secondary'}`}
                                        onClick={() => handleGrowthPeriodChange('yearly')}
                                    >
                                        Yearly
                                    </button>
                                </div>
                                <button 
                                    className="btn btn-sm btn-outline-primary"
                                    onClick={() => toggleViewMode('growth')}
                                >
                                    {viewModes.growth === 'visual' ? 'Text View' : 'Visual View'}
                                </button>
                            </div>
                        </div>
                        <div className="card-body">
                            {safeGrowthData.length > 0 ? (
                                viewModes.growth === 'visual' ? (
                                    <div key="growth-visual">
                                        {renderChart('growth-chart', growthChartData, { 
                                            title: 'New Clients Over Time',
                                            xaxis: { title: 'Period' },
                                            yaxis: { title: 'New Clients' }
                                        })}
                                    </div>
                                ) : (
                                    <div key="growth-text" className="chart-container">
                                        <table className="table table-striped">
                                            <thead>
                                                <tr>
                                                    <th>Period</th>
                                                    <th>New Clients</th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                {safeGrowthData.map((item, index) => (
                                                    <tr key={index}>
                                                        <td>{item && item.period ? item.period : ''}</td>
                                                        <td>{item && item.new_clients !== undefined ? item.new_clients : 0}</td>
                                                    </tr>
                                                ))}
                                            </tbody>
                                        </table>
                                    </div>
                                )
                            ) : (
                                <p>No client growth data available.</p>
                            )}
                        </div>
                    </div>
                </div>
            </div>
            
            {/* Additional Metrics */}
            <div className="row mb-4">
                {/* Payment Methods */}
                <div className="col-md-4">
                    <div className="card">
                        <div className="card-header d-flex justify-content-between align-items-center">
                            <h5>Payment Methods</h5>
                            <button 
                                className="btn btn-sm btn-outline-primary"
                                onClick={() => toggleViewMode('paymentMethods')}
                            >
                                {viewModes.paymentMethods === 'visual' ? 'Text View' : 'Visual View'}
                            </button>
                        </div>
                        <div className="card-body">
                            {safePaymentMethodsData.length > 0 ? (
                                viewModes.paymentMethods === 'visual' ? (
                                    <div key="payment-methods-visual">
                                        {renderChart('payment-methods-chart', paymentMethodsChartData, { 
                                            title: 'Payment Methods',
                                            xaxis: { title: 'Method' },
                                            yaxis: { title: 'Count' }
                                        })}
                                    </div>
                                ) : (
                                    <div key="payment-methods-text" className="chart-container">
                                        <table className="table table-striped">
                                            <thead>
                                                <tr>
                                                    <th>Method</th>
                                                    <th>Count</th>
                                                    <th>Amount ($)</th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                {safePaymentMethodsData.map((item, index) => (
                                                    <tr key={index}>
                                                        <td>{item && item.method ? item.method : ''}</td>
                                                        <td>{item && item.count !== undefined ? item.count : 0}</td>
                                                        <td>${item && item.total_amount !== undefined ? item.total_amount.toFixed(2) : '0.00'}</td>
                                                    </tr>
                                                ))}
                                            </tbody>
                                        </table>
                                    </div>
                                )
                            ) : (
                                <p>No payment method data available.</p>
                            )}
                        </div>
                    </div>
                </div>
                
                {/* Membership Status */}
                <div className="col-md-4">
                    <div className="card">
                        <div className="card-header d-flex justify-content-between align-items-center">
                            <h5>Membership Status</h5>
                            <button 
                                className="btn btn-sm btn-outline-primary"
                                onClick={() => toggleViewMode('membershipStatus')}
                            >
                                {viewModes.membershipStatus === 'visual' ? 'Text View' : 'Visual View'}
                            </button>
                        </div>
                        <div className="card-body">
                            {safeMembershipStatusData.length > 0 ? (
                                viewModes.membershipStatus === 'visual' ? (
                                    <div key="membership-status-visual">
                                        {renderChart('membership-status-chart', membershipStatusChartData, { 
                                            title: 'Membership Status'
                                        })}
                                    </div>
                                ) : (
                                    <div key="membership-status-text" className="chart-container">
                                        <table className="table table-striped">
                                            <thead>
                                                <tr>
                                                    <th>Status</th>
                                                    <th>Count</th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                {safeMembershipStatusData.map((item, index) => (
                                                    <tr key={index}>
                                                        <td>{item && item.status ? item.status : ''}</td>
                                                        <td>{item && item.count !== undefined ? item.count : 0}</td>
                                                    </tr>
                                                ))}
                                            </tbody>
                                        </table>
                                    </div>
                                )
                            ) : (
                                <p>No membership status data available.</p>
                            )}
                        </div>
                    </div>
                </div>
                
                {/* Age Distribution */}
                <div className="col-md-4">
                    <div className="card">
                        <div className="card-header d-flex justify-content-between align-items-center">
                            <h5>Age Distribution</h5>
                            <button 
                                className="btn btn-sm btn-outline-primary"
                                onClick={() => toggleViewMode('ageDistribution')}
                            >
                                {viewModes.ageDistribution === 'visual' ? 'Text View' : 'Visual View'}
                            </button>
                        </div>
                        <div className="card-body">
                            {safeAgeDistributionData.length > 0 ? (
                                viewModes.ageDistribution === 'visual' ? (
                                    <div key="age-distribution-visual">
                                        {renderChart('age-distribution-chart', ageDistributionChartData, { 
                                            title: 'Age Distribution',
                                            xaxis: { title: 'Age Group' },
                                            yaxis: { title: 'Count' }
                                        })}
                                    </div>
                                ) : (
                                    <div key="age-distribution-text" className="chart-container">
                                        <table className="table table-striped">
                                            <thead>
                                                <tr>
                                                    <th>Age Group</th>
                                                    <th>Count</th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                {safeAgeDistributionData.map((item, index) => (
                                                    <tr key={index}>
                                                        <td>{item && item.age_group ? item.age_group : ''}</td>
                                                        <td>{item && item.count !== undefined ? item.count : 0}</td>
                                                    </tr>
                                                ))}
                                            </tbody>
                                        </table>
                                    </div>
                                )
                            ) : (
                                <p>No age distribution data available.</p>
                            )}
                        </div>
                    </div>
                </div>
            </div>
            
            {/* Gender Distribution */}
            <div className="row mb-4">
                <div className="col-12">
                    <div className="card">
                        <div className="card-header d-flex justify-content-between align-items-center">
                            <h5>Gender Distribution</h5>
                            <button 
                                className="btn btn-sm btn-outline-primary"
                                onClick={() => toggleViewMode('genderDistribution')}
                            >
                                {viewModes.genderDistribution === 'visual' ? 'Text View' : 'Visual View'}
                            </button>
                        </div>
                        <div className="card-body">
                            {safeGenderDistributionData.length > 0 ? (
                                viewModes.genderDistribution === 'visual' ? (
                                    <div key="gender-distribution-visual">
                                        {renderChart('gender-distribution-chart', genderDistributionChartData, { 
                                            title: 'Gender Distribution'
                                        })}
                                    </div>
                                ) : (
                                    <div key="gender-distribution-text" className="chart-container">
                                        <table className="table table-striped">
                                            <thead>
                                                <tr>
                                                    <th>Gender</th>
                                                    <th>Count</th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                {safeGenderDistributionData.map((item, index) => (
                                                    <tr key={index}>
                                                        <td>{item && item.gender ? item.gender : ''}</td>
                                                        <td>{item && item.count !== undefined ? item.count : 0}</td>
                                                    </tr>
                                                ))}
                                            </tbody>
                                        </table>
                                    </div>
                                )
                            ) : (
                                <p>No gender distribution data available.</p>
                            )}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}

// Footer component
function Footer() {
    return (
        <footer className="footer mt-4">
            <div className="container text-center">
                <p>&copy; 2023 GymEdge. All rights reserved.</p>
            </div>
        </footer>
    );
}

// Expose functions to global scope for onclick handlers
window.handleFilteredNavigation = null;

// Render the app
const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<App />);