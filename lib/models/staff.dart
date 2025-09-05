class Staff {
  final int? id;
  final String staffname;
  final String email;
  final int phonenumber;
  final String role;

  Staff({
    this.id,
    required this.staffname,
    required this.email,
    required this.phonenumber,
    required this.role,
  });

  factory Staff.fromJson(Map<String, dynamic> json) {
    return Staff(
      id: json['id'],
      staffname: json['staffname'] ?? '',
      email: json['email'] ?? '',
      phonenumber: json['phonenumber'] ?? 0,
      role: json['role'] ?? '',
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'staffname': staffname,
      'email': email,
      'phonenumber': phonenumber,
      'role': role,
    };
  }

  Staff copyWith({
    int? id,
    String? staffname,
    String? email,
    int? phonenumber,
    String? role,
  }) {
    return Staff(
      id: id ?? this.id,
      staffname: staffname ?? this.staffname,
      email: email ?? this.email,
      phonenumber: phonenumber ?? this.phonenumber,
      role: role ?? this.role,
    );
  }
}


