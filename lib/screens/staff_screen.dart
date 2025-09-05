import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:gym_booking_app/providers/gym_provider.dart';
import 'package:gym_booking_app/models/staff.dart';
import 'package:gym_booking_app/utils/theme.dart';

class StaffScreen extends StatefulWidget {
  const StaffScreen({super.key});

  @override
  State<StaffScreen> createState() => _StaffScreenState();
}

class _StaffScreenState extends State<StaffScreen> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<GymProvider>().loadStaff();
    });
  }

  @override
  Widget build(BuildContext context) {
    return Consumer<GymProvider>(
      builder: (context, gymProvider, child) {
        return Scaffold(
          body: gymProvider.isLoading
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
                            style: const TextStyle(color: AppTheme.errorColor),
                            textAlign: TextAlign.center,
                          ),
                          const SizedBox(height: 16),
                          ElevatedButton(
                            onPressed: () {
                              gymProvider.clearError();
                              gymProvider.loadStaff();
                            },
                            child: const Text('Retry'),
                          ),
                        ],
                      ),
                    )
                  : gymProvider.staff.isEmpty
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
                                'No staff found',
                                style: TextStyle(
                                  fontSize: 18,
                                  fontWeight: FontWeight.w600,
                                  color: AppTheme.textSecondaryColor,
                                ),
                              ),
                              const SizedBox(height: 8),
                              const Text(
                                'Add your first staff member to get started',
                                style: TextStyle(
                                  color: AppTheme.textSecondaryColor,
                                ),
                              ),
                            ],
                          ),
                        )
                      : RefreshIndicator(
                          onRefresh: () async {
                            await gymProvider.loadStaff();
                          },
                          child: ListView.builder(
                            padding: const EdgeInsets.all(16),
                            itemCount: gymProvider.staff.length,
                            itemBuilder: (context, index) {
                              final staff = gymProvider.staff[index];
                              return Card(
                                margin: const EdgeInsets.only(bottom: 12),
                                child: ListTile(
                                  leading: CircleAvatar(
                                    backgroundColor: AppTheme.accentColor.withOpacity(0.1),
                                    child: Icon(
                                      Icons.person,
                                      color: AppTheme.accentColor,
                                    ),
                                  ),
                                  title: Text(
                                    staff.staffname,
                                    style: const TextStyle(
                                      fontWeight: FontWeight.w600,
                                    ),
                                  ),
                                  subtitle: Column(
                                    crossAxisAlignment: CrossAxisAlignment.start,
                                    children: [
                                      Text(
                                        staff.email,
                                        style: const TextStyle(
                                          color: AppTheme.textSecondaryColor,
                                        ),
                                      ),
                                      Text(
                                        '${staff.role} • ${staff.phonenumber}',
                                        style: const TextStyle(
                                          color: AppTheme.textSecondaryColor,
                                        ),
                                      ),
                                    ],
                                  ),
                                  trailing: PopupMenuButton<String>(
                                    onSelected: (value) {
                                      switch (value) {
                                        case 'edit':
                                          _showEditStaffDialog(staff);
                                          break;
                                        case 'delete':
                                          _showDeleteDialog(staff);
                                          break;
                                      }
                                    },
                                    itemBuilder: (context) => [
                                      const PopupMenuItem(
                                        value: 'edit',
                                        child: Row(
                                          children: [
                                            Icon(Icons.edit, size: 20),
                                            SizedBox(width: 8),
                                            Text('Edit'),
                                          ],
                                        ),
                                      ),
                                      const PopupMenuItem(
                                        value: 'delete',
                                        child: Row(
                                          children: [
                                            Icon(Icons.delete, size: 20, color: AppTheme.errorColor),
                                            SizedBox(width: 8),
                                            Text('Delete', style: TextStyle(color: AppTheme.errorColor)),
                                          ],
                                        ),
                                      ),
                                    ],
                                  ),
                                ),
                              );
                            },
                          ),
                        ),
          floatingActionButton: FloatingActionButton(
            onPressed: () => _showAddStaffDialog(),
            child: const Icon(Icons.add),
          ),
        );
      },
    );
  }

  void _showAddStaffDialog() {
    _showStaffDialog();
  }

  void _showEditStaffDialog(Staff staff) {
    _showStaffDialog(staff: staff);
  }

  void _showStaffDialog({Staff? staff}) {
    final nameController = TextEditingController(text: staff?.staffname ?? '');
    final emailController = TextEditingController(text: staff?.email ?? '');
    final phoneController = TextEditingController(text: staff?.phonenumber.toString() ?? '');
    final roleController = TextEditingController(text: staff?.role ?? '');

    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(staff != null ? 'Edit Staff' : 'Add Staff'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            TextField(
              controller: nameController,
              decoration: const InputDecoration(
                labelText: 'Staff Name',
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 16),
            TextField(
              controller: emailController,
              decoration: const InputDecoration(
                labelText: 'Email',
                border: OutlineInputBorder(),
              ),
              keyboardType: TextInputType.emailAddress,
            ),
            const SizedBox(height: 16),
            TextField(
              controller: phoneController,
              decoration: const InputDecoration(
                labelText: 'Phone Number',
                border: OutlineInputBorder(),
              ),
              keyboardType: TextInputType.phone,
            ),
            const SizedBox(height: 16),
            TextField(
              controller: roleController,
              decoration: const InputDecoration(
                labelText: 'Role',
                border: OutlineInputBorder(),
              ),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () async {
              if (nameController.text.isEmpty ||
                  emailController.text.isEmpty ||
                  phoneController.text.isEmpty ||
                  roleController.text.isEmpty) {
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('Please fill all fields')),
                );
                return;
              }

              final newStaff = Staff(
                staffname: nameController.text,
                email: emailController.text,
                phonenumber: int.parse(phoneController.text),
                role: roleController.text,
              );

              try {
                if (staff != null) {
                  await context.read<GymProvider>().updateStaff(staff.id!, newStaff);
                } else {
                  await context.read<GymProvider>().createStaff(newStaff);
                }
                Navigator.of(context).pop();
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(
                    content: Text(staff != null ? 'Staff updated successfully' : 'Staff added successfully'),
                    backgroundColor: AppTheme.successColor,
                  ),
                );
              } catch (e) {
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(
                    content: Text('Error: ${e.toString()}'),
                    backgroundColor: AppTheme.errorColor,
                  ),
                );
              }
            },
            child: Text(staff != null ? 'Update' : 'Add'),
          ),
        ],
      ),
    );
  }

  void _showDeleteDialog(Staff staff) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Delete Staff'),
        content: Text(
          'Are you sure you want to delete "${staff.staffname}"? This action cannot be undone.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.of(context).pop();
              context.read<GymProvider>().deleteStaff(staff.id!);
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
}


