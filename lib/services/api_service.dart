import 'dart:convert';
import 'package:http/http.dart' as http;

class ApiService {
  static const String baseUrl = 'http://localhost:8001'; // For web and local development
  // static const String baseUrl = 'http://10.0.2.2:8001'; // For Android emulator
  // static const String baseUrl = 'http://your-ip:8001'; // For physical device

  // Headers
  static Map<String, String> get _headers => {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      };

  // Generic HTTP methods
  static Future<Map<String, dynamic>> _handleResponse(http.Response response) async {
    if (response.statusCode >= 200 && response.statusCode < 300) {
      return json.decode(response.body);
    } else {
      throw Exception('HTTP ${response.statusCode}: ${response.body}');
    }
  }

  // Dashboard Stats
  static Future<Map<String, dynamic>> getDashboardStats() async {
    final response = await http.get(
      Uri.parse('$baseUrl/dashboard/stats'),
      headers: _headers,
    );
    return _handleResponse(response);
  }

  // Clients
  static Future<Map<String, dynamic>> getClients() async {
    final response = await http.get(
      Uri.parse('$baseUrl/clients/'),
      headers: _headers,
    );
    return _handleResponse(response);
  }

  static Future<Map<String, dynamic>> getClient(int clientId) async {
    final response = await http.get(
      Uri.parse('$baseUrl/clients/$clientId'),
      headers: _headers,
    );
    return _handleResponse(response);
  }

  static Future<Map<String, dynamic>> createClient(Map<String, dynamic> clientData) async {
    final response = await http.post(
      Uri.parse('$baseUrl/clients/'),
      headers: _headers,
      body: json.encode(clientData),
    );
    return _handleResponse(response);
  }

  static Future<Map<String, dynamic>> updateClient(int clientId, Map<String, dynamic> clientData) async {
    final response = await http.put(
      Uri.parse('$baseUrl/clients/$clientId'),
      headers: _headers,
      body: json.encode(clientData),
    );
    return _handleResponse(response);
  }

  static Future<Map<String, dynamic>> deleteClient(int clientId) async {
    final response = await http.delete(
      Uri.parse('$baseUrl/clients/$clientId'),
      headers: _headers,
    );
    return _handleResponse(response);
  }

  static Future<Map<String, dynamic>> filterClients(String status) async {
    final response = await http.get(
      Uri.parse('$baseUrl/clients/filter/?status=$status'),
      headers: _headers,
    );
    return _handleResponse(response);
  }

  // Plans
  static Future<Map<String, dynamic>> getPlans() async {
    final response = await http.get(
      Uri.parse('$baseUrl/plans/'),
      headers: _headers,
    );
    return _handleResponse(response);
  }

  static Future<Map<String, dynamic>> createPlan(Map<String, dynamic> planData) async {
    final response = await http.post(
      Uri.parse('$baseUrl/plans/'),
      headers: _headers,
      body: json.encode(planData),
    );
    return _handleResponse(response);
  }

  static Future<Map<String, dynamic>> updatePlan(int planId, Map<String, dynamic> planData) async {
    final response = await http.put(
      Uri.parse('$baseUrl/plans/$planId'),
      headers: _headers,
      body: json.encode(planData),
    );
    return _handleResponse(response);
  }

  static Future<Map<String, dynamic>> deletePlan(int planId) async {
    final response = await http.delete(
      Uri.parse('$baseUrl/plans/$planId'),
      headers: _headers,
    );
    return _handleResponse(response);
  }

  // Staff
  static Future<Map<String, dynamic>> getStaff() async {
    final response = await http.get(
      Uri.parse('$baseUrl/staffs/'),
      headers: _headers,
    );
    return _handleResponse(response);
  }

  static Future<Map<String, dynamic>> createStaff(Map<String, dynamic> staffData) async {
    final response = await http.post(
      Uri.parse('$baseUrl/staffs/'),
      headers: _headers,
      body: json.encode(staffData),
    );
    return _handleResponse(response);
  }

  static Future<Map<String, dynamic>> updateStaff(int staffId, Map<String, dynamic> staffData) async {
    final response = await http.put(
      Uri.parse('$baseUrl/staffs/$staffId'),
      headers: _headers,
      body: json.encode(staffData),
    );
    return _handleResponse(response);
  }

  static Future<Map<String, dynamic>> deleteStaff(int staffId) async {
    final response = await http.delete(
      Uri.parse('$baseUrl/staffs/$staffId'),
      headers: _headers,
    );
    return _handleResponse(response);
  }

  // Leads
  static Future<Map<String, dynamic>> getLeads() async {
    final response = await http.get(
      Uri.parse('$baseUrl/leads/'),
      headers: _headers,
    );
    return _handleResponse(response);
  }

  static Future<Map<String, dynamic>> createLead(Map<String, dynamic> leadData) async {
    final response = await http.post(
      Uri.parse('$baseUrl/leads/'),
      headers: _headers,
      body: json.encode(leadData),
    );
    return _handleResponse(response);
  }

  static Future<Map<String, dynamic>> deleteLead(int leadId) async {
    final response = await http.delete(
      Uri.parse('$baseUrl/leads/$leadId'),
      headers: _headers,
    );
    return _handleResponse(response);
  }
}
