import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:flutter/services.dart';
import 'package:gym_booking_app/providers/gym_provider.dart';
import 'package:gym_booking_app/models/plan.dart';
import 'package:gym_booking_app/utils/theme.dart';

class PlansScreen extends StatefulWidget {
  const PlansScreen({super.key});

  @override
  State<PlansScreen> createState() => _PlansScreenState();
}

class _PlansScreenState extends State<PlansScreen> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<GymProvider>().loadPlans();
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
                              gymProvider.loadPlans();
                            },
                            child: const Text('Retry'),
                          ),
                        ],
                      ),
                    )
                  : gymProvider.plans.isEmpty
                      ? Center(
                          child: Column(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              Icon(
                                Icons.card_membership_outlined,
                                size: 64,
                                color: AppTheme.textSecondaryColor,
                              ),
                              const SizedBox(height: 16),
                              const Text(
                                'No plans found',
                                style: TextStyle(
                                  fontSize: 18,
                                  fontWeight: FontWeight.w600,
                                  color: AppTheme.textSecondaryColor,
                                ),
                              ),
                              const SizedBox(height: 8),
                              const Text(
                                'Add your first plan to get started',
                                style: TextStyle(
                                  color: AppTheme.textSecondaryColor,
                                ),
                              ),
                            ],
                          ),
                        )
                      : RefreshIndicator(
                          onRefresh: () async {
                            await gymProvider.loadPlans();
                          },
                          child: ListView.builder(
                            padding: const EdgeInsets.all(16),
                            itemCount: gymProvider.plans.length,
                            itemBuilder: (context, index) {
                              final plan = gymProvider.plans[index];
                              return Card(
                                margin: const EdgeInsets.only(bottom: 12),
                                child: ListTile(
                                  leading: CircleAvatar(
                                    backgroundColor: AppTheme.primaryColor.withOpacity(0.1),
                                    child: Icon(
                                      Icons.card_membership,
                                      color: AppTheme.primaryColor,
                                    ),
                                  ),
                                  title: Text(
                                    plan.planname,
                                    style: const TextStyle(
                                      fontWeight: FontWeight.w600,
                                    ),
                                  ),
                                  subtitle: Text(
                                    '${plan.days} days • \$${plan.amount}',
                                    style: const TextStyle(
                                      color: AppTheme.textSecondaryColor,
                                    ),
                                  ),
                                  trailing: PopupMenuButton<String>(
                                    onSelected: (value) {
                                      switch (value) {
                                        case 'edit':
                                          _showEditPlanDialog(plan);
                                          break;
                                        case 'delete':
                                          _showDeleteDialog(plan);
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
            onPressed: () => _showAddPlanDialog(),
            child: const Icon(Icons.add),
          ),
        );
      },
    );
  }

  void _showAddPlanDialog() {
    _showPlanDialog();
  }

  void _showEditPlanDialog(Plan plan) {
    _showPlanDialog(plan: plan);
  }

  void _showPlanDialog({Plan? plan}) {
    final nameController = TextEditingController(text: plan?.planname ?? '');
    final durationValueController = TextEditingController(text: plan?.days.toString() ?? '');
    final amountController = TextEditingController(text: plan?.amount.toString() ?? '');

    // Determine initial unit and displayed value using requested ranges:
    // days range: 1-14; months range: 0.5-12. If plan.days <= 14, default to Days, else Months.
    String initialUnit = 'Days';
    if (plan != null) {
      if (plan.days <= 14) {
        initialUnit = 'Days';
        durationValueController.text = plan.days.toString();
      } else {
        initialUnit = 'Months';
        final monthsVal = plan.days / 30.0;
        // show one decimal if needed
        durationValueController.text = (monthsVal == monthsVal.truncateToDouble())
            ? monthsVal.toStringAsFixed(0)
            : monthsVal.toStringAsFixed(1);
      }
    }

    String selectedUnit = initialUnit;

    showDialog(
      context: context,
      builder: (context) => StatefulBuilder(
        builder: (context, setState) {
          return AlertDialog(
            title: Text(plan != null ? 'Edit Plan' : 'Add Plan'),
            content: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                TextField(
                  controller: nameController,
                  decoration: const InputDecoration(
                    labelText: 'Plan Name',
                    border: OutlineInputBorder(),
                  ),
                ),
                const SizedBox(height: 12),
                Row(
                  children: [
                    Expanded(
                      flex: 2,
                      child: TextField(
                        controller: durationValueController,
                        decoration: InputDecoration(
                          labelText: selectedUnit == 'Months'
                              ? 'Duration (months) (0.5 - 12)'
                              : 'Duration (days) (1 - 14)',
                          border: const OutlineInputBorder(),
                        ),
                        keyboardType: selectedUnit == 'Months'
                            ? const TextInputType.numberWithOptions(decimal: true)
                            : TextInputType.number,
                        inputFormatters: selectedUnit == 'Months'
                            ? <TextInputFormatter>[
                                // Allow up to 2 digits before decimal and one decimal place
                                FilteringTextInputFormatter.allow(RegExp(r'^\d{0,2}(?:\.\d{0,1})?')),
                              ]
                            : <TextInputFormatter>[
                                FilteringTextInputFormatter.digitsOnly,
                              ],
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      flex: 1,
                      child: DropdownButtonFormField<String>(
                        value: selectedUnit,
                        decoration: const InputDecoration(
                          labelText: 'Unit',
                          border: OutlineInputBorder(),
                        ),
                        items: const [
                          DropdownMenuItem(value: 'Days', child: Text('Days')),
                          DropdownMenuItem(value: 'Months', child: Text('Months')),
                        ],
                        onChanged: (val) {
                          if (val == null) return;
                          final currentStr = durationValueController.text;
                          if (selectedUnit == val) return;
                          if (val == 'Months' && selectedUnit == 'Days') {
                            final current = int.tryParse(currentStr) ?? 0;
                            final months = (current / 30.0);
                            durationValueController.text = months.toStringAsFixed(months == months.truncateToDouble() ? 0 : 1);
                          } else if (val == 'Days' && selectedUnit == 'Months') {
                            final current = double.tryParse(currentStr) ?? 0.0;
                            final days = (current * 30).round();
                            durationValueController.text = days.toString();
                          }
                          setState(() {
                            selectedUnit = val;
                          });
                        },
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 12),
                TextField(
                  controller: amountController,
                  decoration: const InputDecoration(
                    labelText: 'Amount',
                    border: OutlineInputBorder(),
                  ),
                  keyboardType: const TextInputType.numberWithOptions(decimal: true),
                  inputFormatters: <TextInputFormatter>[
                    FilteringTextInputFormatter.allow(RegExp(r'^\d+(?:\.\d{0,2})?')),
                  ],
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
                  if (nameController.text.isEmpty || durationValueController.text.isEmpty || amountController.text.isEmpty) {
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(content: Text('Please fill all fields')),
                    );
                    return;
                  }

                  int daysToSend;

                  if (selectedUnit == 'Days') {
                    final value = int.tryParse(durationValueController.text) ?? 0;
                    if (value < 1 || value > 14) {
                      ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(content: Text('Days must be between 1 and 14')),
                      );
                      return;
                    }
                    daysToSend = value;
                  } else {
                    final value = double.tryParse(durationValueController.text) ?? 0.0;
                    if (value < 0.5 || value > 12.0) {
                      ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(content: Text('Months must be between 0.5 and 12')),
                      );
                      return;
                    }
                    daysToSend = (value * 30).round();
                  }

                  try {
                    final newPlan = Plan(
                      planname: nameController.text,
                      days: daysToSend,
                      amount: double.parse(amountController.text),
                    );

                    if (plan != null) {
                      await context.read<GymProvider>().updatePlan(plan.id!, newPlan);
                    } else {
                      await context.read<GymProvider>().createPlan(newPlan);
                    }
                    Navigator.of(context).pop();
                    ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(
                        content: Text(plan != null ? 'Plan updated successfully' : 'Plan added successfully'),
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
                child: Text(plan != null ? 'Update' : 'Add'),
              ),
            ],
          );
        },
      ),
    );
  }

  void _showDeleteDialog(Plan plan) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Delete Plan'),
        content: Text(
          'Are you sure you want to delete "${plan.planname}"? This action cannot be undone.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.of(context).pop();
              context.read<GymProvider>().deletePlan(plan.id!);
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


