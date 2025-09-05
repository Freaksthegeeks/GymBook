class Plan {
  final int? id;
  final String planname;
  final int days;
  final double amount;

  Plan({
    this.id,
    required this.planname,
    required this.days,
    required this.amount,
  });

  factory Plan.fromJson(Map<String, dynamic> json) {
    return Plan(
      id: json['id'],
      planname: json['planname'] ?? '',
      days: json['days'] ?? 0,
      amount: (json['amount'] ?? 0.0).toDouble(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'planname': planname,
      'days': days,
      'amount': amount,
    };
  }

  Plan copyWith({
    int? id,
    String? planname,
    int? days,
    double? amount,
  }) {
    return Plan(
      id: id ?? this.id,
      planname: planname ?? this.planname,
      days: days ?? this.days,
      amount: amount ?? this.amount,
    );
  }
}


