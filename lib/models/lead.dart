class Lead {
  final int? id;
  final String name;
  final String phonenumber;
  final String? notes;
  final String? createdAt;

  Lead({
    this.id,
    required this.name,
    required this.phonenumber,
    this.notes,
    this.createdAt,
  });

  factory Lead.fromJson(Map<String, dynamic> json) {
    return Lead(
      id: json['id'],
      name: json['name'] ?? '',
      phonenumber: json['phonenumber']?.toString() ?? '',
      notes: json['notes'],
      createdAt: json['created_at'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'name': name,
      'phonenumber': phonenumber,
      'notes': notes,
    };
  }

  Lead copyWith({
    int? id,
    String? name,
    String? phonenumber,
    String? notes,
    String? createdAt,
  }) {
    return Lead(
      id: id ?? this.id,
      name: name ?? this.name,
      phonenumber: phonenumber ?? this.phonenumber,
      notes: notes ?? this.notes,
      createdAt: createdAt ?? this.createdAt,
    );
  }
}


