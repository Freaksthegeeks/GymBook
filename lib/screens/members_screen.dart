import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:gym_booking_app/providers/gym_provider.dart';
import 'package:gym_booking_app/models/client.dart';
import 'package:gym_booking_app/utils/theme.dart';
import 'package:gym_booking_app/widgets/member_card.dart';
import 'package:gym_booking_app/screens/add_member_screen.dart';
import 'package:gym_booking_app/screens/payment_screen.dart';

class MembersScreen extends StatefulWidget {
  final String? initialFilter;
  final bool showFilters;

  const MembersScreen({super.key, this.initialFilter, this.showFilters = true});

  @override
  State<MembersScreen> createState() => _MembersScreenState();
}

class _MembersScreenState extends State<MembersScreen> {
  String _selectedFilter = 'all';
  final TextEditingController _searchController = TextEditingController();
  List<Client> _filteredClients = [];
  String _sortBy = 'name_asc';

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      // Load clients or apply initial filter if provided
      final provider = context.read<GymProvider>();
      if (widget.initialFilter != null && widget.initialFilter != 'all') {
        _selectedFilter = widget.initialFilter!;
        provider.filterClients(_selectedFilter).then((_) => _filterClients());
      } else {
        provider.loadClients().then((_) => _filterClients());
      }
    });
  }

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  void _filterClients() {
    final gymProvider = context.read<GymProvider>();
  List<Client> clients = List<Client>.from(gymProvider.clients);
    // Apply search filter: only name or phone number
    if (_searchController.text.isNotEmpty) {
      final q = _searchController.text.toLowerCase();
      clients = clients.where((client) {
        return client.clientname.toLowerCase().contains(q) ||
            client.phonenumber.toLowerCase().contains(q);
      }).toList();
    }

    // Apply status filter: if a filter is selected, call provider.filterClients
    if (_selectedFilter != 'all') {
      // Use the provider's clients which should already be filtered if filterClients was called.
      clients = List<Client>.from(gymProvider.clients);
      // Apply search on top of filtered provider clients
      if (_searchController.text.isNotEmpty) {
        final q = _searchController.text.toLowerCase();
        clients = clients.where((client) {
          return client.clientname.toLowerCase().contains(q) ||
              client.phonenumber.toLowerCase().contains(q);
        }).toList();
      }
    }

    setState(() {
      _filteredClients = clients;
    });
  }

  void _sortClients() {
    setState(() {
      if (_sortBy == 'name_asc') {
        _filteredClients.sort((a, b) => a.clientname.toLowerCase().compareTo(b.clientname.toLowerCase()));
      } else if (_sortBy == 'name_desc') {
        _filteredClients.sort((a, b) => b.clientname.toLowerCase().compareTo(a.clientname.toLowerCase()));
      } else if (_sortBy == 'expires_soon') {
        _filteredClients.sort((a, b) {
          final aDate = a.endDate != null ? DateTime.tryParse(a.endDate!) : null;
          final bDate = b.endDate != null ? DateTime.tryParse(b.endDate!) : null;
          if (aDate == null && bDate == null) return 0;
          if (aDate == null) return 1;
          if (bDate == null) return -1;
          return aDate.compareTo(bDate);
        });
      } else if (_sortBy == 'expires_late') {
        _filteredClients.sort((a, b) {
          final aDate = a.endDate != null ? DateTime.tryParse(a.endDate!) : null;
          final bDate = b.endDate != null ? DateTime.tryParse(b.endDate!) : null;
          if (aDate == null && bDate == null) return 0;
          if (aDate == null) return 1;
          if (bDate == null) return -1;
          return bDate.compareTo(aDate);
        });
      }
    });
  }

  @override
  Widget build(BuildContext context) {
        return Consumer<GymProvider>(
      builder: (context, gymProvider, child) {

        return Scaffold(
          body: Column(
            children: [
              // Search and Filter Bar
              Container(
                padding: const EdgeInsets.all(16),
                child: Column(
                  children: [
                    // Search Bar
                    TextField(
                      controller: _searchController,
                      decoration: InputDecoration(
                        hintText: 'Search members...',
                        prefixIcon: const Icon(Icons.search),
                        suffixIcon: _searchController.text.isNotEmpty
                            ? IconButton(
                                icon: const Icon(Icons.clear),
                                onPressed: () {
                                  _searchController.clear();
                                  _filterClients();
                                },
                              )
                            : null,
                      ),
                      onChanged: (value) => _filterClients(),
                    ),
                    const SizedBox(height: 12),
                    // Sort dropdown + member count
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        DropdownButton<String>(
                          value: _sortBy,
                          items: const [
                            DropdownMenuItem(value: 'name_asc', child: Text('Name A→Z')),
                            DropdownMenuItem(value: 'name_desc', child: Text('Name Z→A')),
                            DropdownMenuItem(value: 'expires_soon', child: Text('Expires soon')),
                            DropdownMenuItem(value: 'expires_late', child: Text('Expires late')),
                          ],
                          onChanged: (val) {
                            if (val == null) return;
                            setState(() {
                              _sortBy = val;
                            });
                            _sortClients();
                          },
                        ),
                        // member count in italics
                        Text(
                          '${_filteredClients.length} members',
                          style: const TextStyle(fontStyle: FontStyle.italic, color: AppTheme.textSecondaryColor),
                        ),
                      ],
                    ),
                    // Filter Chips (only show when enabled)
                    if (widget.showFilters)
                      SingleChildScrollView(
                        scrollDirection: Axis.horizontal,
                        child: Row(
                          children: [
                            _buildFilterChip('All', 'all'),
                            const SizedBox(width: 8),
                            _buildFilterChip('Active', 'active'),
                            const SizedBox(width: 8),
                            _buildFilterChip('Expiring', 'expiring'),
                            const SizedBox(width: 8),
                            _buildFilterChip('Expired', 'expired'),
                          ],
                        ),
                      ),
                  ],
                ),
              ),
              // Members List
              Expanded(
                child: gymProvider.isLoading
                    ? const Center(child: CircularProgressIndicator())
                    : gymProvider.error != null
                        ? Center(
                            child: Column(
                              mainAxisAlignment: MainAxisAlignment.center,
                              children: [
                                const Icon(
                                  Icons.error_outline,
                                  size: 48,
                                  color: AppTheme.errorColor,
                                ),
                                const SizedBox(height: 16),
                                Text(
                                  'Error: ${gymProvider.error}',
                                  style: const TextStyle(
                                    color: AppTheme.errorColor,
                                  ),
                                  textAlign: TextAlign.center,
                                ),
                                const SizedBox(height: 16),
                                ElevatedButton(
                                  onPressed: () {
                                    gymProvider.clearError();
                                    gymProvider.loadClients();
                                  },
                                  child: const Text('Retry'),
                                ),
                              ],
                            ),
                          )
                        : _filteredClients.isEmpty
                            ? Center(
                                child: Column(
                                  mainAxisAlignment: MainAxisAlignment.center,
                                  children: [
                                    Icon(
                                      Icons.people_outline,
                                      size: 64,
                                      color: AppTheme.textSecondaryColor,
                                    ),
                                    const SizedBox(height: 16),
                                    const Text(
                                      'No members found',
                                      style: TextStyle(
                                        fontSize: 18,
                                        fontWeight: FontWeight.w600,
                                        color: AppTheme.textSecondaryColor,
                                      ),
                                    ),
                                    const SizedBox(height: 8),
                                    const Text(
                                      'Add your first member to get started',
                                      style: TextStyle(
                                        color: AppTheme.textSecondaryColor,
                                      ),
                                    ),
                                  ],
                                ),
                              )
                            : RefreshIndicator(
                                onRefresh: () async {
                                  await gymProvider.loadClients();
                                },
                                child: ListView.builder(
                                  padding: const EdgeInsets.all(16),
                                  itemCount: _filteredClients.length,
                                  itemBuilder: (context, index) {
                                    final client = _filteredClients[index];
                                    return MemberCard(
                                      client: client,
                                      onTap: () => _showMemberDetails(client),
                                      onEdit: () async {
                                        // Navigate to edit member and refresh list when returned
                                        await Navigator.push(
                                          context,
                                          MaterialPageRoute(
                                            builder: (context) => AddMemberScreen(client: client),
                                          ),
                                        );
                                        // Refresh after edit
                                        await context.read<GymProvider>().loadClients();
                                        _filterClients();
                                      },
                                      onDelete: () {
                                        _showDeleteDialog(client);
                                      },
                                    );
                                  },
                                ),
                              ),
              ),
            ],
          ),
          floatingActionButton: FloatingActionButton(
            onPressed: () {
              Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (context) => const AddMemberScreen(),
                ),
              );
            },
            child: const Icon(Icons.add),
          ),
        );
      },
    );
  }

  Widget _buildFilterChip(String label, String value) {
    final isSelected = _selectedFilter == value;
    return FilterChip(
      label: Text(label),
      selected: isSelected,
      onSelected: (selected) {
        setState(() {
          _selectedFilter = value;
        });
        // Trigger provider filtering
        final provider = context.read<GymProvider>();
        if (value == 'all') {
          provider.loadClients().then((_) => _filterClients());
        } else {
          provider.filterClients(value).then((_) => _filterClients());
        }
      },
      selectedColor: AppTheme.primaryColor.withOpacity(0.2),
      checkmarkColor: AppTheme.primaryColor,
    );
  }

  void _showDeleteDialog(Client client) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Delete Member'),
        content: Text(
          'Are you sure you want to delete ${client.clientname}? This action cannot be undone.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.of(context).pop();
              context.read<GymProvider>().deleteClient(client.id!);
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: AppTheme.errorColor,
            ),
            child: const Text('Delete'),
          ),
        ],
      ),
    );
  }

  void _showMemberDetails(Client client) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(client.clientname),
        content: SingleChildScrollView(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text('Phone: ${client.phonenumber}'),
              const SizedBox(height: 8),
              Text('Email: ${client.email}'),
              const SizedBox(height: 8),
              Text('DOB: ${client.dateofbirth}'),
              const SizedBox(height: 8),
              Text('Gender: ${client.gender}'),
              const SizedBox(height: 8),
              Text('Blood Group: ${client.bloodgroup}'),
              const SizedBox(height: 8),
              Text('Address: ${client.address}'),
              const SizedBox(height: 8),
              if (client.notes != null && client.notes!.isNotEmpty) Text('Notes: ${client.notes}'),
              const SizedBox(height: 8),
              Text('Plan: ${client.planName ?? 'N/A'}'),
              const SizedBox(height: 8),
              Text('Start Date: ${client.startDate}'),
              const SizedBox(height: 8),
              Text('End Date: ${client.endDate ?? 'N/A'}'),
            ],
          ),
        ),
        actions: [
          TextButton(onPressed: () => Navigator.of(context).pop(), child: const Text('Close')),
          TextButton(
            onPressed: () async {
              Navigator.of(context).pop();
              await Navigator.push(
                context,
                MaterialPageRoute(builder: (context) => PaymentScreen(client: client)),
              );
            },
            child: const Text('Payments'),
          ),
          TextButton(
            onPressed: () async {
              Navigator.of(context).pop();
              await Navigator.push(
                context,
                MaterialPageRoute(builder: (context) => AddMemberScreen(client: client)),
              );
              // Refresh after edit
              await context.read<GymProvider>().loadClients();
              _filterClients();
            },
            child: const Text('Edit'),
          ),
        ],
      ),
    );
  }
}


