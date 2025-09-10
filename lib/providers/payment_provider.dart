import 'package:flutter/material.dart';
import 'package:gym_booking_app/models/payment.dart';
import 'package:gym_booking_app/models/client.dart';
import 'package:gym_booking_app/services/api_service.dart';

class PaymentProvider extends ChangeNotifier {
  final Map<int, List<Payment>> _clientIdToPayments = {};
  bool _isLoading = false;
  String? _error;

  bool get isLoading => _isLoading;
  String? get error => _error;

  List<Payment> paymentsForClient(int clientId) =>
      _clientIdToPayments[clientId] ?? const [];

  Future<void> loadPaymentsForClient(int clientId) async {
    try {
      _isLoading = true;
      _error = null;
      notifyListeners();

      final response = await PaymentsApi.getClientPayments(clientId);
      if (response['payments'] is List) {
        final list = (response['payments'] as List)
            .map((p) => Payment.fromJson(p as Map<String, dynamic>))
            .toList();
        _clientIdToPayments[clientId] = list;
      } else {
        _error = 'Invalid response format';
      }
    } catch (e) {
      _error = e.toString();
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<bool> addPayment({
    required int clientId,
    int? planId,
    required double amount,
    String? note,
    String? method,
    String? paidAtIso,
  }) async {
    try {
      _isLoading = true;
      _error = null;
      notifyListeners();

      final payload = {
        'client_id': clientId,
        if (planId != null) 'plan_id': planId,
        'amount': amount,
        'paid_at': paidAtIso ?? DateTime.now().toIso8601String(),
        if (note != null && note.isNotEmpty) 'note': note,
        if (method != null && method.isNotEmpty) 'method': method,
      };
      await PaymentsApi.createPayment(payload);
      await loadPaymentsForClient(clientId);
      return true;
    } catch (e) {
      _error = e.toString();
      return false;
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  double computeDueForClient(Client client) {
    final planAmount = client.planAmount ?? 0.0;
    final payments = paymentsForClient(client.id ?? -1);
    final totalPaid = payments.fold<double>(0.0, (sum, p) => sum + p.amount);
    final due = planAmount - totalPaid;
    if (due < 0) return 0.0;
    return due;
  }

  void clearError() {
    _error = null;
    notifyListeners();
  }
}

