import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:gym_booking_app/providers/gym_provider.dart';
import 'package:gym_booking_app/utils/theme.dart';
import 'package:gym_booking_app/widgets/stat_card.dart';
import 'package:gym_booking_app/screens/members_screen.dart';
import 'package:gym_booking_app/screens/add_member_screen.dart';
import 'package:gym_booking_app/screens/plans_screen.dart';
import 'package:gym_booking_app/screens/staff_screen.dart';
import 'package:gym_booking_app/screens/leads_screen.dart';

class DashboardScreen extends StatefulWidget {
  const DashboardScreen({super.key});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<GymProvider>().loadDashboardStats();
    });
  }

  @override
  Widget build(BuildContext context) {
    return Consumer<GymProvider>(
      builder: (context, gymProvider, child) {
        return Scaffold(
          body: RefreshIndicator(
            onRefresh: () async {
              await gymProvider.loadDashboardStats();
            },
            child: SingleChildScrollView(
              physics: const AlwaysScrollableScrollPhysics(),
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Welcome Section
                  Container(
                    width: double.infinity,
                    padding: const EdgeInsets.all(20),
                    decoration: BoxDecoration(
                      gradient: LinearGradient(
                        colors: [
                          AppTheme.primaryColor,
                          AppTheme.secondaryColor,
                        ],
                        begin: Alignment.topLeft,
                        end: Alignment.bottomRight,
                      ),
                      borderRadius: BorderRadius.circular(16),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text(
                          'Welcome to GymBook!',
                          style: TextStyle(
                            fontSize: 24,
                            fontWeight: FontWeight.bold,
                            color: Colors.white,
                          ),
                        ),
                        const SizedBox(height: 8),
                        const Text(
                          'Manage your gym operations efficiently',
                          style: TextStyle(
                            fontSize: 16,
                            color: Colors.white70,
                          ),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 24),
                  // Stats Grid
                  if (gymProvider.isLoading)
                    const Center(
                      child: CircularProgressIndicator(),
                    )
                  else if (gymProvider.error != null)
                    Center(
                      child: Column(
                        children: [
                          const Icon(
                            Icons.error_outline,
                            size: 48,
                            color: AppTheme.errorColor,
                          ),
                          const SizedBox(height: 16),
                          Text(
                            'Error: ${gymProvider.error}',
                            style: const TextStyle(color: AppTheme.errorColor),
                            textAlign: TextAlign.center,
                          ),
                          const SizedBox(height: 16),
                          ElevatedButton(
                            onPressed: () {
                              gymProvider.clearError();
                              gymProvider.loadDashboardStats();
                            },
                            child: const Text('Retry'),
                          ),
                        ],
                      ),
                    )
                  else
                    Column(
                      children: [
                        // Stats Row 1
                        Row(
                          children: [
                            Expanded(
                              child: StatCard(
                                title: 'Total Members',
                                value: '${gymProvider.dashboardStats['total_members'] ?? 0}',
                                icon: Icons.people,
                                color: AppTheme.primaryColor,
                                onTap: () {
                                  Navigator.push(
                                    context,
                                    MaterialPageRoute(
                                      builder: (context) => const MembersScreen(initialFilter: 'all', showFilters: true),
                                    ),
                                  );
                                },
                              ),
                            ),
                            const SizedBox(width: 16),
                            Expanded(
                              child: StatCard(
                                title: 'Active Members',
                                value: '${gymProvider.dashboardStats['active_members'] ?? 0}',
                                icon: Icons.check_circle,
                                color: AppTheme.successColor,
                                onTap: () {
                                  Navigator.push(
                                    context,
                                    MaterialPageRoute(
                                      builder: (context) => const MembersScreen(initialFilter: 'active', showFilters: false),
                                    ),
                                  );
                                },
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 16),
                        // Stats Row 2
                        Row(
                          children: [
                            Expanded(
                              child: StatCard(
                                title: 'Expiring Soon',
                                value: '${gymProvider.dashboardStats['expiring_in_10_days'] ?? 0}',
                                icon: Icons.warning,
                                color: AppTheme.warningColor,
                                onTap: () {
                                  Navigator.push(
                                    context,
                                    MaterialPageRoute(
                                      builder: (context) => const MembersScreen(initialFilter: 'expiring', showFilters: false),
                                    ),
                                  );
                                },
                              ),
                            ),
                            const SizedBox(width: 16),
                            Expanded(
                              child: StatCard(
                                title: 'Recently Expired',
                                value: '${gymProvider.dashboardStats['expired_in_last_30_days'] ?? 0}',
                                icon: Icons.cancel,
                                color: AppTheme.errorColor,
                                onTap: () {
                                  Navigator.push(
                                    context,
                                    MaterialPageRoute(
                                      builder: (context) => const MembersScreen(initialFilter: 'expired', showFilters: false),
                                    ),
                                  );
                                },
                              ),
                            ),
                          ],
                        ),
                      ],
                    ),
                  const SizedBox(height: 32),
                  // Quick Actions
                  const Text(
                    'Quick Actions',
                    style: TextStyle(
                      fontSize: 20,
                      fontWeight: FontWeight.bold,
                      color: AppTheme.textPrimaryColor,
                    ),
                  ),
                  const SizedBox(height: 16),
                  GridView.count(
                    shrinkWrap: true,
                    physics: const NeverScrollableScrollPhysics(),
                    crossAxisCount: 2,
                    crossAxisSpacing: 16,
                    mainAxisSpacing: 16,
                    children: [
                      _buildQuickActionCard(
                        'Add Member',
                        Icons.person_add,
                        AppTheme.primaryColor,
                        () {
                          Navigator.push(
                            context,
                            MaterialPageRoute(
                              builder: (context) => const AddMemberScreen(),
                            ),
                          );
                        },
                      ),
                      _buildQuickActionCard(
                        'Add Plan',
                        Icons.add_card,
                        AppTheme.secondaryColor,
                        () {
                          Navigator.push(
                            context,
                            MaterialPageRoute(
                              builder: (context) => const PlansScreen(),
                            ),
                          );
                        },
                      ),
                      _buildQuickActionCard(
                        'Add Staff',
                        Icons.person_add_alt,
                        AppTheme.accentColor,
                        () {
                          Navigator.push(
                            context,
                            MaterialPageRoute(
                              builder: (context) => const StaffScreen(),
                            ),
                          );
                        },
                      ),
                      _buildQuickActionCard(
                        'Add Lead',
                        Icons.person_add,
                        AppTheme.successColor,
                        () {
                          Navigator.push(
                            context,
                            MaterialPageRoute(
                              builder: (context) => const LeadsScreen(),
                            ),
                          );
                        },
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ),
        );
      },
    );
  }

  Widget _buildQuickActionCard(
    String title,
    IconData icon,
    Color color,
    VoidCallback onTap,
  ) {
    return Card(
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: color.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Icon(
                  icon,
                  size: 32,
                  color: color,
                ),
              ),
              const SizedBox(height: 12),
              Text(
                title,
                style: const TextStyle(
                  fontSize: 14,
                  fontWeight: FontWeight.w600,
                  color: AppTheme.textPrimaryColor,
                ),
                textAlign: TextAlign.center,
              ),
            ],
          ),
        ),
      ),
    );
  }
}
