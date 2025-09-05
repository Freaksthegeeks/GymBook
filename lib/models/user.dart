class User {
  final int id;
  final String username;
  final String email;
  final String? createdAt;

  User({
    required this.id,
    required this.username,
    required this.email,
    this.createdAt,
  });

  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      id: json['id'],
      username: json['username'],
      email: json['email'],
      createdAt: json['created_at'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'username': username,
      'email': email,
      'created_at': createdAt,
    };
  }
}

class AuthResponse {
  final String accessToken;
  final String tokenType;
  final int userId;
  final String username;

  AuthResponse({
    required this.accessToken,
    required this.tokenType,
    required this.userId,
    required this.username,
  });

  factory AuthResponse.fromJson(Map<String, dynamic> json) {
    return AuthResponse(
      accessToken: json['access_token'],
      tokenType: json['token_type'],
      userId: json['user_id'],
      username: json['username'],
    );
  }
}
