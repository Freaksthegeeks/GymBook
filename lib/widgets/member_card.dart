import 'package:flutter/material.dart';
import 'package:gym_booking_app/models/client.dart';
import 'package:gym_booking_app/utils/theme.dart';

class MemberCard extends StatelessWidget {
  final Client client;
  final VoidCallback? onTap;
  final VoidCallback? onEdit;
  final VoidCallback? onDelete;

  const MemberCard({
    super.key,
    required this.client,
    this.onTap,
    this.onEdit,
    this.onDelete,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  // Avatar
                  CircleAvatar(
                    radius: 25,
                    backgroundColor: AppTheme.primaryColor.withOpacity(0.1),
                    child: Text(
                      client.clientname.isNotEmpty
                          ? client.clientname[0].toUpperCase()
                          : '?',
                      style: TextStyle(
                        fontSize: 20,
                        fontWeight: FontWeight.bold,
                        color: AppTheme.primaryColor,
                      ),
                    ),
                  ),
                  const SizedBox(width: 12),
                  // Member Info
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          client.clientname,
                          style: const TextStyle(
                            fontSize: 18,
                            fontWeight: FontWeight.w600,
                            color: AppTheme.textPrimaryColor,
                          ),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          client.email,
                          style: const TextStyle(
                            fontSize: 14,
                            color: AppTheme.textSecondaryColor,
                          ),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          client.phonenumber,
                          style: const TextStyle(
                            fontSize: 14,
                            color: AppTheme.textSecondaryColor,
                          ),
                        ),
                      ],
                    ),
                  ),
                  // Status pill
                  _buildStatusPill(),
                  const SizedBox(width: 8),
                  // Action Buttons
                  if (onEdit != null || onDelete != null)
                    PopupMenuButton<String>(
                      onSelected: (value) {
                        switch (value) {
                          case 'edit':
                            onEdit?.call();
                            break;
                          case 'delete':
                            onDelete?.call();
                            break;
                        }
                      },
                      itemBuilder: (context) => [
                        if (onEdit != null)
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
                        if (onDelete != null)
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
                      child: const Icon(
                        Icons.more_vert,
                        color: AppTheme.textSecondaryColor,
                      ),
                    ),
                ],
              ),
              const SizedBox(height: 12),
              // Additional Info
              Row(
                children: [
                  _buildInfoChip('Plan', client.planName ?? 'N/A'),
                  const SizedBox(width: 8),
                  _buildInfoChip('Gender', client.gender),
                  const SizedBox(width: 8),
                  _buildInfoChip('Age', _calculateAge(client.dateofbirth)),
                ],
              ),
              if (client.endDate != null) ...[
                const SizedBox(height: 8),
                Row(
                  children: [
                    Icon(
                      Icons.calendar_today,
                      size: 16,
                      color: AppTheme.textSecondaryColor,
                    ),
                    const SizedBox(width: 4),
                    Text(
                      'Expires: ${client.endDate}',
                      style: const TextStyle(
                        fontSize: 12,
                        color: AppTheme.textSecondaryColor,
                      ),
                    ),
                  ],
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildInfoChip(String label, String value) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: AppTheme.backgroundColor,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: AppTheme.borderColor),
      ),
      child: Text(
        '$label: $value',
        style: const TextStyle(
          fontSize: 12,
          color: AppTheme.textSecondaryColor,
        ),
      ),
    );
  }

  String _calculateAge(String dateOfBirth) {
    try {
      final dob = DateTime.parse(dateOfBirth);
      final now = DateTime.now();
      final age = now.year - dob.year;
      if (now.month < dob.month || (now.month == dob.month && now.day < dob.day)) {
        return '${age - 1}';
      }
      return age.toString();
    } catch (e) {
      return 'N/A';
    }
  }

  // Builds the status chip with a colored dot and dynamic text based on end date
  Widget _buildStatusPill() {
    final status = _computeStatus();
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
      decoration: BoxDecoration(
        color: status.backgroundColor,
        borderRadius: BorderRadius.circular(999),
        border: Border.all(color: status.borderColor),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Container(
            width: 8,
            height: 8,
            decoration: BoxDecoration(
              color: status.dotColor,
              shape: BoxShape.circle,
            ),
          ),
          const SizedBox(width: 6),
          Text(
            status.label,
            style: const TextStyle(fontSize: 12, color: AppTheme.textPrimaryColor),
          ),
        ],
      ),
    );
  }

  _MembershipStatus _computeStatus() {
    if (client.endDate == null || client.endDate!.isEmpty) {
      return _MembershipStatus.active();
    }

    final DateTime? endDate = DateTime.tryParse(client.endDate!);
    if (endDate == null) {
      return _MembershipStatus.active();
    }

    final DateTime today = DateTime.now();
    final DateTime end = DateTime(endDate.year, endDate.month, endDate.day);
    final DateTime now = DateTime(today.year, today.month, today.day);
    final int daysRemaining = end.difference(now).inDays;

    if (daysRemaining < 0) {
      final int daysAgo = -daysRemaining;
      return _MembershipStatus.expired(daysAgo);
    }

    if (daysRemaining <= 15) {
      return _MembershipStatus.expiring(daysRemaining);
    }

    return _MembershipStatus.active();
  }
}

class _MembershipStatus {
  final String label;
  final Color dotColor;
  final Color backgroundColor;
  final Color borderColor;

  _MembershipStatus({
    required this.label,
    required this.dotColor,
    required this.backgroundColor,
    required this.borderColor,
  });

  factory _MembershipStatus.active() {
    return _MembershipStatus(
      label: 'Active',
      dotColor: Colors.green,
      backgroundColor: const Color(0xFFE9F7EF),
      borderColor: const Color(0xFFBFE5CD),
    );
  }

  factory _MembershipStatus.expiring(int days) {
    final plural = days == 1 ? 'day' : 'days';
    return _MembershipStatus(
      label: 'Expiring in $days $plural',
      dotColor: Colors.orange,
      backgroundColor: const Color(0xFFFFF5E6),
      borderColor: const Color(0xFFFFE0B2),
    );
  }

  factory _MembershipStatus.expired(int daysAgo) {
    final plural = daysAgo == 1 ? 'day' : 'days';
    return _MembershipStatus(
      label: 'Expired $daysAgo $plural ago',
      dotColor: Colors.red,
      backgroundColor: const Color(0xFFFFEBEE),
      borderColor: const Color(0xFFF5C6CB),
    );
  }
}


