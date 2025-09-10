import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:gym_booking_app/models/client.dart';
import 'package:gym_booking_app/models/payment.dart';
import 'package:gym_booking_app/providers/payment_provider.dart';
import 'package:gym_booking_app/utils/theme.dart';

class PaymentScreen extends StatefulWidget {
  final Client client;
  const PaymentScreen({super.key, required this.client});

  @override
  State<PaymentScreen> createState() => _PaymentScreenState();
}

class _PaymentScreenState extends State<PaymentScreen> {
  final TextEditingController _amountController = TextEditingController();
  final TextEditingController _noteController = TextEditingController();
  String? _method;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<PaymentProvider>().loadPaymentsForClient(widget.client.id!);
    });
  }

  @override
  void dispose() {
    _amountController.dispose();
    _noteController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Consumer<PaymentProvider>(
      builder: (context, paymentProvider, child) {
        final payments = paymentProvider.paymentsForClient(widget.client.id!);
        final due = paymentProvider.computeDueForClient(widget.client);
        final totalPaid = payments.fold<double>(0.0, (s, p) => s + p.amount);

        return Scaffold(
          appBar: AppBar(
            title: Text('Payments • ${widget.client.clientname}'),
          ),
          body: RefreshIndicator(
            onRefresh: () => paymentProvider.loadPaymentsForClient(widget.client.id!),
            child: ListView(
              padding: const EdgeInsets.all(16),
              children: [
                _headerCard(due: due, totalPaid: totalPaid),
                const SizedBox(height: 16),
                _quickAdd(paymentProvider),
                const SizedBox(height: 16),
                const Text('Payment History', style: TextStyle(fontSize: 16, fontWeight: FontWeight.w700)),
                const SizedBox(height: 8),
                AnimatedSwitcher(
                  duration: const Duration(milliseconds: 300),
                  child: paymentProvider.isLoading && payments.isEmpty
                      ? const Center(
                          child: Padding(
                            padding: EdgeInsets.all(24.0),
                            child: CircularProgressIndicator(),
                          ),
                        )
                      : payments.isEmpty
                          ? const Text('No payments yet')
                          : Column(
                              key: ValueKey(payments.length),
                              children: payments.map((p) => _paymentTile(p)).toList(),
                            ),
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _headerCard({required double due, required double totalPaid}) {
    final planAmount = widget.client.planAmount ?? 0.0;
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppTheme.backgroundColor,
        border: Border.all(color: AppTheme.borderColor),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('Plan: ${widget.client.planName ?? 'N/A'} • ${widget.client.planDays ?? 0} days'),
          const SizedBox(height: 4),
          Text('Plan Amount: ${planAmount.toStringAsFixed(2)}'),
          const SizedBox(height: 4),
          TweenAnimationBuilder<double>(
            duration: const Duration(milliseconds: 400),
            tween: Tween<double>(begin: 0, end: totalPaid),
            builder: (context, value, child) => Text('Total Paid: ${value.toStringAsFixed(2)}'),
          ),
          const SizedBox(height: 4),
          TweenAnimationBuilder<double>(
            duration: const Duration(milliseconds: 400),
            tween: Tween<double>(begin: 0, end: due),
            builder: (context, value, child) => Text(
              'Due: ${value.toStringAsFixed(2)}',
              style: TextStyle(
                color: due > 0 ? AppTheme.errorColor : Colors.green,
                fontWeight: FontWeight.w700,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _quickAdd(PaymentProvider paymentProvider) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text('Add Payment', style: TextStyle(fontWeight: FontWeight.w600)),
        const SizedBox(height: 8),
        Row(
          children: [
            Expanded(
              child: TextField(
                controller: _amountController,
                keyboardType: const TextInputType.numberWithOptions(decimal: true),
                decoration: const InputDecoration(hintText: 'Amount'),
              ),
            ),
            const SizedBox(width: 8),
            DropdownButton<String>(
              value: _method,
              hint: const Text('Method'),
              items: const [
                DropdownMenuItem(value: 'cash', child: Text('Cash')),
                DropdownMenuItem(value: 'upi', child: Text('UPI')),
                DropdownMenuItem(value: 'card', child: Text('Card')),
              ],
              onChanged: (v) => setState(() => _method = v),
            ),
            const SizedBox(width: 8),
            ElevatedButton(
              onPressed: paymentProvider.isLoading
                  ? null
                  : () async {
                      final amount = double.tryParse(_amountController.text.trim()) ?? 0.0;
                      if (amount <= 0) return;
                      final ok = await paymentProvider.addPayment(
                        clientId: widget.client.id!,
                        planId: widget.client.planId,
                        amount: amount,
                        method: _method,
                        note: _noteController.text.trim().isEmpty ? null : _noteController.text.trim(),
                      );
                      if (ok) {
                        _amountController.clear();
                        _noteController.clear();
                        if (mounted) {
                          ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Payment recorded')));
                        }
                      } else if (paymentProvider.error != null && mounted) {
                        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Error: ${paymentProvider.error}')));
                      }
                    },
              child: Text(paymentProvider.isLoading ? 'Saving...' : 'Add'),
            )
          ],
        ),
        const SizedBox(height: 8),
        TextField(
          controller: _noteController,
          decoration: const InputDecoration(hintText: 'Note (optional)'),
        ),
      ],
    );
  }

  Widget _paymentTile(Payment p) {
    return Card(
      child: ListTile(
        leading: const Icon(Icons.receipt_long),
        title: Text('${p.amount.toStringAsFixed(2)} • ${p.method ?? 'N/A'}'),
        subtitle: Text(p.paidAt),
      ),
    );
  }
}


