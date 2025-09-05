import 'package:flutter/material.dart';
import 'package:gym_booking_app/models/client.dart';
import 'package:gym_booking_app/models/plan.dart';
import 'package:gym_booking_app/models/staff.dart';
import 'package:gym_booking_app/models/lead.dart';
import 'package:gym_booking_app/services/api_service.dart';

class GymProvider extends ChangeNotifier {
  List<Client> _clients = [];
  List<Plan> _plans = [];
  List<Staff> _staff = [];
  List<Lead> _leads = [];
  Map<String, dynamic> _dashboardStats = {};
  bool _isLoading = false;
  String? _error;

  // Getters
  List<Client> get clients => _clients;
  List<Plan> get plans => _plans;
  List<Staff> get staff => _staff;
  List<Lead> get leads => _leads;
  Map<String, dynamic> get dashboardStats => _dashboardStats;
  bool get isLoading => _isLoading;
  String? get error => _error;

  // Dashboard Stats
  Future<void> loadDashboardStats() async {
    try {
      _isLoading = true;
      _error = null;
      notifyListeners();

      final response = await ApiService.getDashboardStats();
      _dashboardStats = response;
    } catch (e) {
      _error = e.toString();
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  // Clients
  Future<void> loadClients() async {
    try {
      _isLoading = true;
      _error = null;
      notifyListeners();

      final response = await ApiService.getClients();
      if (response['clients'] is List) {
        _clients = (response['clients'] as List)
            .map((client) => Client.fromJson(client as Map<String, dynamic>))
            .toList();
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

  Future<void> createClient(Client client) async {
    try {
      _isLoading = true;
      _error = null;
      notifyListeners();

      await ApiService.createClient(client.toJson());
      await loadClients();
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> updateClient(int clientId, Client client) async {
    try {
      _isLoading = true;
      _error = null;
      notifyListeners();

      await ApiService.updateClient(clientId, client.toJson());
      await loadClients();
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> deleteClient(int clientId) async {
    try {
      _isLoading = true;
      _error = null;
      notifyListeners();

      await ApiService.deleteClient(clientId);
      await loadClients();
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<List<Client>> filterClients(String status) async {
    try {
      _isLoading = true;
      _error = null;
      notifyListeners();

      final response = await ApiService.filterClients(status);
      if (response['clients'] is List) {
        final list = (response['clients'] as List)
            .map((client) => Client.fromJson(client as Map<String, dynamic>))
            .toList();
        // Replace the provider's client list with the filtered list so UI can react
        _clients = list;
        return list;
      } else {
        _error = 'Invalid response format';
        notifyListeners();
        return [];
      }
    } catch (e) {
      _error = e.toString();
      notifyListeners();
      return [];
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  // Plans
  Future<void> loadPlans() async {
    try {
      _isLoading = true;
      _error = null;
      notifyListeners();

      final response = await ApiService.getPlans();
      if (response['plans'] is List) {
        _plans = (response['plans'] as List)
            .map((plan) => Plan.fromJson(plan as Map<String, dynamic>))
            .toList();
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

  Future<void> createPlan(Plan plan) async {
    try {
      _isLoading = true;
      _error = null;
      notifyListeners();

      await ApiService.createPlan(plan.toJson());
      await loadPlans();
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> updatePlan(int planId, Plan plan) async {
    try {
      _isLoading = true;
      _error = null;
      notifyListeners();

      await ApiService.updatePlan(planId, plan.toJson());
      await loadPlans();
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> deletePlan(int planId) async {
    try {
      _isLoading = true;
      _error = null;
      notifyListeners();

      await ApiService.deletePlan(planId);
      await loadPlans();
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  // Staff
  Future<void> loadStaff() async {
    try {
      _isLoading = true;
      _error = null;
      notifyListeners();

      final response = await ApiService.getStaff();
      if (response['staffs'] is List) {
        _staff = (response['staffs'] as List)
            .map((staff) => Staff.fromJson(staff as Map<String, dynamic>))
            .toList();
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

  Future<void> createStaff(Staff staff) async {
    try {
      _isLoading = true;
      _error = null;
      notifyListeners();

      await ApiService.createStaff(staff.toJson());
      await loadStaff();
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> updateStaff(int staffId, Staff staff) async {
    try {
      _isLoading = true;
      _error = null;
      notifyListeners();

      await ApiService.updateStaff(staffId, staff.toJson());
      await loadStaff();
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> deleteStaff(int staffId) async {
    try {
      _isLoading = true;
      _error = null;
      notifyListeners();

      await ApiService.deleteStaff(staffId);
      await loadStaff();
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  // Leads
  Future<void> loadLeads() async {
    try {
      _isLoading = true;
      _error = null;
      notifyListeners();

      final response = await ApiService.getLeads();
      if (response['leads'] is List) {
        _leads = (response['leads'] as List)
            .map((lead) => Lead.fromJson(lead as Map<String, dynamic>))
            .toList();
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

  Future<void> createLead(Lead lead) async {
    try {
      _isLoading = true;
      _error = null;
      notifyListeners();

      await ApiService.createLead(lead.toJson());
      await loadLeads();
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> deleteLead(int leadId) async {
    try {
      _isLoading = true;
      _error = null;
      notifyListeners();

      await ApiService.deleteLead(leadId);
      await loadLeads();
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  // Clear error
  void clearError() {
    _error = null;
    notifyListeners();
  }
}
