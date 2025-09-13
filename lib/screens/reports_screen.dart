import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:gym_booking_app/providers/gym_provider.dart';
import 'package:gym_booking_app/providers/payment_provider.dart';
import 'package:gym_booking_app/utils/theme.dart';

class ReportsScreen extends StatefulWidget {
  const ReportsScreen({super.key});

  @override
  State<ReportsScreen> createState() => _ReportsScreenState();
}

class _ReportsScreenState extends State<ReportsScreen> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<GymProvider>().loadDashboardStats();
      context.read<GymProvider>().loadClients();
    });
  }

  @override
  Widget build(BuildContext context) {
    return Consumer2<GymProvider, PaymentProvider>(
      builder: (context, gym, payments, _) {
        final stats = gym.dashboardStats;
        final totalMembers = gym.clients.length;
        final totalRevenue = (stats['total_revenue'] ?? 0).toString();
        final balance = (stats['all_time_balance'] ?? 0).toString();

        return Scaffold(
          body: SingleChildScrollView(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text('Reports', style: TextStyle(fontSize: 22, fontWeight: FontWeight.w700)),
                const SizedBox(height: 12),
                Wrap(
                  spacing: 12,
                  runSpacing: 12,
                  children: [
                    _statCard('Total Revenue', '₹$totalRevenue', Icons.payments),
                    _statCard('All time balance', '₹$balance', Icons.account_balance_wallet),
                    _statCard('Total Members', '$totalMembers', Icons.people_alt),
                  ],
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _statCard(String title, String value, IconData icon) {
    return Container(
      width: 180,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: AppTheme.borderColor),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(icon, color: AppTheme.primaryColor),
              const SizedBox(width: 8),
              Text(title, style: const TextStyle(fontWeight: FontWeight.w600)),
            ],
          ),
          const SizedBox(height: 8),
          Text(value, style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w700)),
        ],
      ),
    );
  }
}



