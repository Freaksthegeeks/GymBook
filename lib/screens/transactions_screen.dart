import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:gym_booking_app/providers/gym_provider.dart';
import 'package:gym_booking_app/providers/payment_provider.dart';
import 'package:gym_booking_app/models/client.dart';
import 'package:gym_booking_app/utils/theme.dart';

class TransactionsScreen extends StatefulWidget {
  const TransactionsScreen({super.key});

  @override
  State<TransactionsScreen> createState() => _TransactionsScreenState();
}

class _TransactionsScreenState extends State<TransactionsScreen> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final gym = context.read<GymProvider>();
      final payments = context.read<PaymentProvider>();
      gym.loadClients().then((_) {
        for (final c in gym.clients) {
          if (c.id != null) payments.loadPaymentsForClient(c.id!);
        }
      });
    });
  }

  @override
  Widget build(BuildContext context) {
    return Consumer2<GymProvider, PaymentProvider>(
      builder: (context, gym, payment, _) {
        final List<_ClientDue> dues = gym.clients.map((c) {
          final due = payment.computeDueForClient(c);
          return _ClientDue(client: c, due: due);
        }).where((x) => x.due > 0).toList()
          ..sort((a, b) => b.due.compareTo(a.due));

        return Scaffold(
          body: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text('Payment Dues', style: TextStyle(fontSize: 22, fontWeight: FontWeight.w700)),
                const SizedBox(height: 12),
                Expanded(
                  child: dues.isEmpty
                      ? const Center(child: Text('No dues'))
                      : ListView.builder(
                          itemCount: dues.length,
                          itemBuilder: (context, index) {
                            final d = dues[index];
                            return Card(
                              margin: const EdgeInsets.only(bottom: 12),
                              child: ListTile(
                                leading: CircleAvatar(
                                  backgroundColor: AppTheme.errorColor.withOpacity(0.1),
                                  child: const Icon(Icons.currency_rupee, color: AppTheme.errorColor),
                                ),
                                title: Text(d.client.clientname, style: const TextStyle(fontWeight: FontWeight.w600)),
                                subtitle: Text('Due: ₹${d.due.toStringAsFixed(2)}',
                                    style: const TextStyle(color: AppTheme.textSecondaryColor)),
                              ),
                            );
                          },
                        ),
                ),
              ],
            ),
          ),
        );
      },
    );
  }
}

class _ClientDue {
  final Client client;
  final double due;
  _ClientDue({required this.client, required this.due});
}



