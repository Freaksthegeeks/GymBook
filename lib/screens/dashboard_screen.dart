import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:gym_booking_app/providers/gym_provider.dart';
import 'package:gym_booking_app/utils/theme.dart';
import 'package:gym_booking_app/widgets/stat_card.dart';
import 'package:gym_booking_app/screens/members_screen.dart';
import 'package:gym_booking_app/widgets/member_card.dart';
import 'package:gym_booking_app/providers/payment_provider.dart';

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
      context.read<GymProvider>().loadClients().then((_) {
        // Load payments for all clients to keep dues up-to-date
        final payments = context.read<PaymentProvider>();
        for (final c in context.read<GymProvider>().clients) {
          if (c.id != null) payments.loadPaymentsForClient(c.id!);
        }
      });
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
                          'Welcome to GymEdge!',
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
                  // (Birthdays moved below Quick Actions)
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
                        // Stats Row 1 (reordered): Active, Expiring Soon
                        Row(
                          children: [
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
                                        builder: (context) => const MembersScreen(initialFilter: 'active', showFilters: true),
                                      ),
                                    );
                                  },
                                ),
                            ),
                            const SizedBox(width: 16),
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
                                        builder: (context) => const MembersScreen(initialFilter: 'expiring', showFilters: true),
                                      ),
                                    );
                                  },
                                ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 16),
                        // Stats Row 2 (reordered): Recently Expired, Total Members (last)
                        Row(
                          children: [
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
                                        builder: (context) => const MembersScreen(initialFilter: 'expired', showFilters: true),
                                      ),
                                    );
                                  },
                                ),
                            ),
                            const SizedBox(width: 16),
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
                          ],
                        ),
                      ],
                    ),
                  const SizedBox(height: 32),
                  // Category top members
                  const _TopMembersSection(),
                  const SizedBox(height: 16),
                  // Dues section (shows members who have outstanding dues)
                  const _DuesSection(),
                  const SizedBox(height: 24),
                  // Today's Birthdays
                  _TodaysBirthdaysSection(),
                ],
              ),
            ),
          ),
        );
      },
    );
  }
}

class _DuesSection extends StatelessWidget {
  const _DuesSection();

  @override
  Widget build(BuildContext context) {
    return Consumer2<GymProvider, PaymentProvider>(
      builder: (context, gym, payment, _) {
        final List<_ClientDue> dues = gym.clients.map((c) {
          final due = payment.computeDueForClient(c);
          return _ClientDue(client: c, due: due);
        }).where((x) => x.due > 0).toList()
          ..sort((a, b) => b.due.compareTo(a.due));

        return Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('Payment Dues', style: TextStyle(fontSize: 18, fontWeight: FontWeight.w700, color: AppTheme.textPrimaryColor)),
            const SizedBox(height: 8),
            if (dues.isEmpty)
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(12.0),
                  child: Row(
                    children: const [
                      Icon(Icons.check_circle, color: AppTheme.successColor),
                      SizedBox(width: 8),
                      Expanded(child: Text('No payment dues', style: TextStyle(fontSize: 14))),
                    ],
                  ),
                ),
              )
            else
              Column(
                children: dues.take(3).map((d) {
                  return Card(
                    margin: const EdgeInsets.only(bottom: 8),
                    child: ListTile(
                      leading: CircleAvatar(
                        backgroundColor: AppTheme.errorColor.withOpacity(0.1),
                        child: const Icon(Icons.currency_rupee, color: AppTheme.errorColor),
                      ),
                      title: Text(d.client.clientname, style: const TextStyle(fontWeight: FontWeight.w600)),
                      subtitle: Text('Due: \u20b9${d.due.toStringAsFixed(2)}', style: const TextStyle(color: AppTheme.textSecondaryColor)),
                      onTap: () {
                        // Navigate to members/payments if needed
                        Navigator.push(
                          context,
                          MaterialPageRoute(builder: (context) => MembersScreen(initialFilter: 'all', showFilters: true)),
                        );
                      },
                    ),
                  );
                }).toList(),
              ),
          ],
        );
      },
    );
  }
}

class _ClientDue {
  final dynamic client;
  final double due;
  _ClientDue({required this.client, required this.due});
}

class _TodaysBirthdaysSection extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Consumer<GymProvider>(
      builder: (context, gym, child) {
        final now = DateTime.now();
        final birthdays = gym.clients.where((c) {
          try {
            final dob = DateTime.parse(c.dateofbirth);
            return dob.month == now.month && dob.day == now.day;
          } catch (_) {
            return false;
          }
        }).toList();
        if (birthdays.isEmpty) return const SizedBox.shrink();
        return Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              "Today's Birthdays",
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.w700, color: AppTheme.textPrimaryColor),
            ),
            const SizedBox(height: 8),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: birthdays
                  .map((c) => Chip(
                        avatar: const Icon(Icons.cake, size: 16),
                        label: Text(c.clientname),
                      ))
                  .toList(),
            ),
          ],
        );
      },
    );
  }
}

class _TopMembersSection extends StatelessWidget {
  const _TopMembersSection();

  List<Widget> _buildCategory(BuildContext context, {required String title, required List clients}) {
    final items = clients.take(2).toList();
    // Header always shown
    final header = [
      const SizedBox(height: 8),
      Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(title, style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w700, color: AppTheme.textPrimaryColor)),
          TextButton(
            onPressed: () {
              // navigate to MembersScreen filtered by this category
              String filter = 'all';
              if (title.toLowerCase().contains('expiring')) filter = 'expiring';
              if (title.toLowerCase().contains('expired')) filter = 'expired';
              if (title.toLowerCase().contains('active')) filter = 'active';
              Navigator.push(
                context,
                MaterialPageRoute(builder: (context) => MembersScreen(initialFilter: filter, showFilters: true)),
              );
            },
            child: const Text('See All'),
          ),
        ],
      ),
      const SizedBox(height: 8),
    ];

    if (items.isEmpty) {
      return [
        ...header,
        Card(
          child: Padding(
            padding: const EdgeInsets.all(12.0),
            child: Text('No members found in this status', style: const TextStyle(color: AppTheme.textSecondaryColor)),
          ),
        ),
        const SizedBox(height: 12),
      ];
    }

    return [
      ...header,
      ...items.map((c) => MemberCard(client: c as dynamic)),
      const SizedBox(height: 12),
    ];
  }

  @override
  Widget build(BuildContext context) {
    return Consumer<GymProvider>(
      builder: (context, gym, _) {
        final now = DateTime.now();
        List active = <dynamic>[];
        List expiring = <dynamic>[];
        List expired = <dynamic>[];
        for (final c in gym.clients) {
          if (c.endDate == null || c.endDate!.isEmpty) {
            active.add(c);
            continue;
          }
          final end = DateTime.tryParse(c.endDate!);
          if (end == null) {
            active.add(c);
            continue;
          }
          final daysRemaining = DateTime(end.year, end.month, end.day)
              .difference(DateTime(now.year, now.month, now.day))
              .inDays;
          if (daysRemaining < 0) {
            expired.add(c);
          } else if (daysRemaining <= 15) {
            expiring.add(c);
          } else {
            active.add(c);
          }
        }

        return Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('Members', style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold, color: AppTheme.textPrimaryColor)),
            ..._buildCategory(context, title: 'Active', clients: active),
            ..._buildCategory(context, title: 'Expiring Soon', clients: expiring),
            ..._buildCategory(context, title: 'Expired', clients: expired),
          ],
        );
      },
    );
  }
}
