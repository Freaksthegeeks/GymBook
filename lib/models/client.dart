class Client {
  final int? id;
  final String clientname;
  final String phonenumber;
  final String dateofbirth;
  final String gender;
  final String bloodgroup;
  final String address;
  final String? notes;
  final String email;
  final double height;
  final double weight;
  final int planId;
  final String startDate;
  final String? endDate;
  final String? planName;
  final int? planDays;
  final double? planAmount;

  Client({
    this.id,
    required this.clientname,
    required this.phonenumber,
    required this.dateofbirth,
    required this.gender,
    required this.bloodgroup,
    required this.address,
    this.notes,
    required this.email,
    required this.height,
    required this.weight,
    required this.planId,
    required this.startDate,
    this.endDate,
    this.planName,
    this.planDays,
    this.planAmount,
  });

  factory Client.fromJson(Map<String, dynamic> json) {
    return Client(
      id: json['id'],
      clientname: json['clientname'] ?? '',
      phonenumber: json['phonenumber']?.toString() ?? '',
      dateofbirth: json['dateofbirth'] ?? '',
      gender: json['gender'] ?? '',
      bloodgroup: json['bloodgroup'] ?? '',
      address: json['address'] ?? '',
      notes: json['notes'],
      email: json['email'] ?? '',
      height: (json['height'] ?? 0.0).toDouble(),
      weight: (json['weight'] ?? 0.0).toDouble(),
      planId: json['plan_id'] ?? 0,
      startDate: json['start_date'] ?? '',
      endDate: json['end_date'],
      planName: json['planname'],
      planDays: json['days'],
      planAmount: json['amount']?.toDouble(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'clientname': clientname,
      'phonenumber': phonenumber,
      'dateofbirth': dateofbirth,
      'gender': gender,
      'bloodgroup': bloodgroup,
      'address': address,
      'notes': notes,
      'email': email,
      'height': height,
      'weight': weight,
      'plan_id': planId,
      'start_date': startDate,
    };
  }

  Client copyWith({
    int? id,
    String? clientname,
    String? phonenumber,
    String? dateofbirth,
    String? gender,
    String? bloodgroup,
    String? address,
    String? notes,
    String? email,
    double? height,
    double? weight,
    int? planId,
    String? startDate,
    String? endDate,
    String? planName,
    int? planDays,
    double? planAmount,
  }) {
    return Client(
      id: id ?? this.id,
      clientname: clientname ?? this.clientname,
      phonenumber: phonenumber ?? this.phonenumber,
      dateofbirth: dateofbirth ?? this.dateofbirth,
      gender: gender ?? this.gender,
      bloodgroup: bloodgroup ?? this.bloodgroup,
      address: address ?? this.address,
      notes: notes ?? this.notes,
      email: email ?? this.email,
      height: height ?? this.height,
      weight: weight ?? this.weight,
      planId: planId ?? this.planId,
      startDate: startDate ?? this.startDate,
      endDate: endDate ?? this.endDate,
      planName: planName ?? this.planName,
      planDays: planDays ?? this.planDays,
      planAmount: planAmount ?? this.planAmount,
    );
  }
}


