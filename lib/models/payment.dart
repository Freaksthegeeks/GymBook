class Payment {
  final int? id;
  final int clientId;
  final int? planId;
  final double amount;
  final String paidAt;
  final String? note;
  final String? method;

  Payment({
    this.id,
    required this.clientId,
    this.planId,
    required this.amount,
    required this.paidAt,
    this.note,
    this.method,
  });

  factory Payment.fromJson(Map<String, dynamic> json) {
    return Payment(
      id: json['id'],
      clientId: json['client_id'] ?? json['clientId'] ?? 0,
      planId: json['plan_id'] ?? json['planId'],
      amount: (json['amount'] ?? 0.0).toDouble(),
      paidAt: json['paid_at'] ?? json['paidAt'] ?? '',
      note: json['note'],
      method: json['method'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'client_id': clientId,
      if (planId != null) 'plan_id': planId,
      'amount': amount,
      'paid_at': paidAt,
      if (note != null) 'note': note,
      if (method != null) 'method': method,
    };
  }
}

