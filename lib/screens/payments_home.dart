import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:gym_booking_app/providers/gym_provider.dart';
import 'package:gym_booking_app/providers/payment_provider.dart';
import 'package:gym_booking_app/models/client.dart';
import 'package:gym_booking_app/utils/theme.dart';
import 'dart:typed_data';
import 'package:image_picker/image_picker.dart';

class PaymentsHome extends StatefulWidget {
  const PaymentsHome({super.key});

  @override
  State<PaymentsHome> createState() => _PaymentsHomeState();
}

class _PaymentsHomeState extends State<PaymentsHome> {
  Client? _selectedClient;
  final TextEditingController _amountController = TextEditingController();
  final TextEditingController _noteController = TextEditingController();
  String? _method;
  Uint8List? _upiQrBytes; // in-memory bytes for web/mobile preview

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<GymProvider>().loadClients();
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
    return Consumer2<GymProvider, PaymentProvider>(
      builder: (context, gymProvider, paymentProvider, child) {
        final clients = gymProvider.clients;
        final due = _selectedClient == null
            ? 0.0
            : paymentProvider.computeDueForClient(_selectedClient!);

        return Scaffold(
          body: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'Payment Portal',
                  style: TextStyle(fontSize: 22, fontWeight: FontWeight.w700),
                ),
                const SizedBox(height: 12),
                DropdownButtonFormField<Client>(
                  value: _selectedClient,
                  items: clients
                      .map(
                        (c) => DropdownMenuItem<Client>(
                          value: c,
                          child: Text('${c.clientname} (${c.planName ?? 'No plan'})'),
                        ),
                      )
                      .toList(),
                  onChanged: (c) async {
                    setState(() {
                      _selectedClient = c;
                    });
                    if (c != null) {
                      await paymentProvider.loadPaymentsForClient(c.id!);
                    }
                  },
                  decoration: const InputDecoration(labelText: 'Select Client'),
                ),
                const SizedBox(height: 12),
                AnimatedSwitcher(
                  duration: const Duration(milliseconds: 300),
                  child: _selectedClient == null
                      ? const SizedBox.shrink()
                      : Container(
                          key: ValueKey(_selectedClient!.id),
                          width: double.infinity,
                          padding: const EdgeInsets.all(16),
                          decoration: BoxDecoration(
                            color: AppTheme.backgroundColor,
                            border: Border.all(color: AppTheme.borderColor),
                            borderRadius: BorderRadius.circular(12),
                          ),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text('Plan amount: ${_selectedClient!.planAmount?.toStringAsFixed(2) ?? '0.00'}'),
                              const SizedBox(height: 8),
                              TweenAnimationBuilder<double>(
                                duration: const Duration(milliseconds: 400),
                                tween: Tween<double>(begin: 0, end: due),
                                builder: (context, value, child) {
                                  final isDue = due > 0;
                                  return Text(
                                    'Current due: ${value.toStringAsFixed(2)}',
                                    style: TextStyle(
                                      color: isDue ? AppTheme.errorColor : Colors.green,
                                      fontWeight: FontWeight.w600,
                                    ),
                                  );
                                },
                              ),
                            ],
                          ),
                        ),
                ),
                const SizedBox(height: 16),
                TextFormField(
                  controller: _amountController,
                  keyboardType: const TextInputType.numberWithOptions(decimal: true),
                  decoration: const InputDecoration(labelText: 'Amount'),
                ),
                const SizedBox(height: 8),
                DropdownButtonFormField<String>(
                  value: _method,
                  items: const [
                    DropdownMenuItem(value: 'cash', child: Text('Cash')),
                    DropdownMenuItem(value: 'upi', child: Text('UPI')),
                    DropdownMenuItem(value: 'card', child: Text('Card')),
                  ],
                  onChanged: (m) => setState(() => _method = m),
                  decoration: const InputDecoration(labelText: 'Method'),
                ),
                const SizedBox(height: 8),
                TextFormField(
                  controller: _noteController,
                  decoration: const InputDecoration(labelText: 'Note (optional)'),
                ),
                const SizedBox(height: 16),
                SizedBox(
                  width: double.infinity,
                  height: 40,
                  child: ElevatedButton.icon(
                    onPressed: paymentProvider.isLoading
                        ? null
                        : () async {
                            if (_selectedClient == null) return;
                            final amount = double.tryParse(_amountController.text.trim()) ?? 0.0;
                            if (amount <= 0) return;
                            final ok = await paymentProvider.addPayment(
                              clientId: _selectedClient!.id!,
                              planId: _selectedClient!.planId,
                              amount: amount,
                              method: _method,
                              note: _noteController.text.trim(),
                            );
                            if (ok) {
                              _amountController.clear();
                              _noteController.clear();
                              ScaffoldMessenger.of(context).showSnackBar(
                                const SnackBar(content: Text('Payment recorded')),
                              );
                            } else if (paymentProvider.error != null) {
                              ScaffoldMessenger.of(context).showSnackBar(
                                SnackBar(content: Text('Error: ${paymentProvider.error}')),
                              );
                            }
                          },
                    icon: const Icon(Icons.payment, size: 18),
                    label: Text(paymentProvider.isLoading ? 'Saving...' : 'Add Payment'),
                    style: ElevatedButton.styleFrom(
                      padding: const EdgeInsets.symmetric(horizontal: 12),
                      textStyle: const TextStyle(fontSize: 14, fontWeight: FontWeight.w600),
                    ),
                  ),
                ),
                const SizedBox(height: 16),
                Row(
                  children: [
                    ElevatedButton.icon(
                      onPressed: () async {
                        // Use image_picker for mobile, for web it opens file picker
                        try {
                          final picker = ImagePicker();
                          final image = await picker.pickImage(source: ImageSource.gallery, maxWidth: 1024);
                          if (image != null) {
                            final bytes = await image.readAsBytes();
                            setState(() => _upiQrBytes = bytes);
                            ScaffoldMessenger.of(context).showSnackBar(
                              const SnackBar(content: Text('QR code added.')),
                            );
                          }
                        } catch (e) {
                          ScaffoldMessenger.of(context).showSnackBar(
                            SnackBar(content: Text('Failed to pick image: $e')),
                          );
                        }
                      },
                      icon: const Icon(Icons.qr_code_2),
                      label: const Text('Add QR Code'),
                    ),
                    const SizedBox(width: 12),
                    if (_upiQrBytes != null)
                      Expanded(
                        child: AspectRatio(
                          aspectRatio: 1,
                          child: Container(
                            decoration: BoxDecoration(
                              border: Border.all(color: AppTheme.borderColor),
                              borderRadius: BorderRadius.circular(12),
                            ),
                            clipBehavior: Clip.antiAlias,
                            child: Image.memory(_upiQrBytes!, fit: BoxFit.cover),
                          ),
                        ),
                      ),
                  ],
                ),
              ],
            ),
          ),
        );
      },
    );
  }
}

