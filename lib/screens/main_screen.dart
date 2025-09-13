import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/auth_provider.dart';
import '../providers/gym_provider.dart';
import '../providers/theme_provider.dart';
import 'dashboard_screen.dart';
import 'members_screen.dart';
import 'plans_screen.dart';
import 'staff_screen.dart';
import 'leads_screen.dart';
import 'transactions_screen.dart';
import 'reports_screen.dart';
import 'add_member_screen.dart';
import 'login_screen.dart';
import 'payments_home.dart';
import '../utils/theme.dart';

class MainScreen extends StatefulWidget {
  const MainScreen({super.key});

  @override
  State<MainScreen> createState() => _MainScreenState();
}

class _MainScreenState extends State<MainScreen> {
  int _currentIndex = 0; // 0: Dashboard, 1: Members, 2: Transactions, 3: Reports

  final List<Widget> _screens = const [
    DashboardScreen(),
    MembersScreen(),
    TransactionsScreen(),
    ReportsScreen(),
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      drawer: _buildDrawer(context),
      body: _screens[_currentIndex],
      bottomNavigationBar: _buildBottomBar(),
      floatingActionButton: FloatingActionButton(
        onPressed: _showQuickAddSheet,
        child: const Icon(Icons.add),
      ),
      floatingActionButtonLocation: FloatingActionButtonLocation.centerDocked,
      appBar: AppBar(
        title: Text(_getTitle()),
        actions: [
          IconButton(
            icon: const Icon(Icons.brightness_6),
            onPressed: () {
              // toggle theme
              final themeProvider = Provider.of<ThemeProvider>(context, listen: false);
              themeProvider.toggle();
            },
          ),
          IconButton(
            icon: const Icon(Icons.logout),
            onPressed: _showLogoutDialog,
          ),
        ],
      ),
    );
  }

  String _getTitle() {
    switch (_currentIndex) {
      case 0:
        return 'Home';
      case 1:
        return 'Members';
      case 2:
        return 'Transactions';
      case 3:
        return 'Reports';
      default:
        return 'GymEdge';
    }
  }

  Widget _buildBottomBar() {
    return BottomAppBar(
      shape: const CircularNotchedRectangle(),
      notchMargin: 6,
      child: SizedBox(
        height: 60,
        child: Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Row(
              children: [
                _buildTabButton(icon: Icons.home_filled, label: 'Home', index: 0),
                _buildTabButton(icon: Icons.people, label: 'Members', index: 1),
              ],
            ),
            Row(
              children: [
                _buildTabButton(icon: Icons.receipt_long, label: 'Transactions', index: 2),
                _buildTabButton(icon: Icons.insert_chart_outlined, label: 'Reports', index: 3),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildTabButton({required IconData icon, required String label, required int index}) {
    final bool selected = _currentIndex == index;
    final Color color = selected ? AppTheme.primaryColor : AppTheme.textSecondaryColor;
    return InkWell(
      onTap: () => setState(() => _currentIndex = index),
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(icon, color: color),
            const SizedBox(height: 2),
            Text(label, style: TextStyle(color: color, fontSize: 12, fontWeight: FontWeight.w600)),
          ],
        ),
      ),
    );
  }

  void _showQuickAddSheet() {
    showModalBottomSheet(
      context: context,
      shape: const RoundedRectangleBorder(borderRadius: BorderRadius.vertical(top: Radius.circular(16))),
      builder: (context) {
        return SafeArea(
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text('+ Add New', style: TextStyle(fontSize: 18, fontWeight: FontWeight.w700)),
                const SizedBox(height: 12),
                Wrap(
                  spacing: 16,
                  runSpacing: 16,
                  children: [
                    _quickAction(icon: Icons.person_add, label: 'Member', onTap: () {
                      Navigator.pop(context);
                      Navigator.of(context).push(
                        MaterialPageRoute(builder: (_) => const MembersScreen()),
                      );
                      Navigator.of(context).push(
                        MaterialPageRoute(builder: (_) => AddMemberScreen()),
                      );
                    }),
                    _quickAction(icon: Icons.people_alt, label: 'Staff', onTap: () {
                      Navigator.pop(context);
                      Navigator.of(context).push(
                        MaterialPageRoute(builder: (_) => const StaffScreen()),
                      );
                    }),
                    _quickAction(icon: Icons.card_membership, label: 'Plan', onTap: () {
                      Navigator.pop(context);
                      Navigator.of(context).push(
                        MaterialPageRoute(builder: (_) => const PlansScreen()),
                      );
                    }),
                    _quickAction(icon: Icons.call, label: 'Leads', onTap: () {
                      Navigator.pop(context);
                      Navigator.of(context).push(
                        MaterialPageRoute(builder: (_) => const LeadsScreen()),
                      );
                    }),
                  ],
                ),
                const SizedBox(height: 8),
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _quickAction({required IconData icon, required String label, required VoidCallback onTap}) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        width: 120,
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: AppTheme.borderColor),
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(icon, color: AppTheme.textPrimaryColor),
            const SizedBox(height: 8),
            Text(label, style: const TextStyle(fontWeight: FontWeight.w600)),
          ],
        ),
      ),
    );
  }

  void _showLogoutDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Logout'),
        content: const Text('Are you sure you want to logout?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.of(context).pop();
              _logout();
            },
            child: const Text('Logout'),
          ),
        ],
      ),
    );
  }

  void _logout() {
    final authProvider = Provider.of<AuthProvider>(context, listen: false);
    authProvider.logout();
    Navigator.of(context).pushAndRemoveUntil(
      MaterialPageRoute(builder: (context) => const LoginScreen()),
      (route) => false,
    );
  }

  Drawer _buildDrawer(BuildContext context) {
    final auth = Provider.of<AuthProvider>(context);
    return Drawer(
      child: SafeArea(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            UserAccountsDrawerHeader(
              accountName: Text(auth.user?.username ?? 'Guest'),
              accountEmail: Text(auth.user?.email ?? ''),
              currentAccountPicture: const CircleAvatar(child: Icon(Icons.person)),
            ),
            ListTile(
              leading: const Icon(Icons.dashboard),
              title: const Text('Dashboard'),
              onTap: () {
                Navigator.pop(context);
                setState(() => _currentIndex = 0);
              },
            ),
            ListTile(
              leading: const Icon(Icons.people),
              title: const Text('Members'),
              onTap: () {
                Navigator.pop(context);
                setState(() => _currentIndex = 1);
              },
            ),
            ListTile(
              leading: const Icon(Icons.card_membership),
              title: const Text('Plans'),
              onTap: () {
                Navigator.pop(context);
                Navigator.of(context).push(MaterialPageRoute(builder: (_) => const PlansScreen()));
              },
            ),
            ListTile(
              leading: const Icon(Icons.person),
              title: const Text('Staff'),
              onTap: () {
                Navigator.pop(context);
                Navigator.of(context).push(MaterialPageRoute(builder: (_) => const StaffScreen()));
              },
            ),
            ListTile(
              leading: const Icon(Icons.phone),
              title: const Text('Leads'),
              onTap: () {
                Navigator.pop(context);
                Navigator.of(context).push(MaterialPageRoute(builder: (_) => const LeadsScreen()));
              },
            ),
            const Divider(),
            ListTile(
              leading: const Icon(Icons.payments),
              title: const Text('Payment Portal'),
              onTap: () {
                Navigator.pop(context);
                Navigator.of(context).push(
                  MaterialPageRoute(builder: (_) => const PaymentsHome()),
                );
              },
            ),
            Consumer<GymProvider>(
              builder: (context, gym, _) {
                final now = DateTime.now();
                final todays = gym.clients.where((c) {
                  try {
                    final dob = DateTime.parse(c.dateofbirth);
                    return dob.month == now.month && dob.day == now.day;
                  } catch (_) {
                    return false;
                  }
                }).toList();
                if (todays.isEmpty) return const SizedBox.shrink();
                return ExpansionTile(
                  leading: const Icon(Icons.cake),
                  title: const Text("Today's Birthdays"),
                  children: todays
                      .map((c) => ListTile(
                            title: Text(c.clientname),
                            subtitle: Text('Phone: ${c.phonenumber}'),
                          ))
                      .toList(),
                );
              },
            ),
            const Spacer(),
            ListTile(
              leading: const Icon(Icons.logout),
              title: const Text('Logout'),
              onTap: _showLogoutDialog,
            ),
          ],
        ),
      ),
    );
  }
}


