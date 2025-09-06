import 'package:flutter/material.dart';
import 'package:gym_booking_app/utils/theme.dart';

class StatCard extends StatelessWidget {
  final String title;
  final String value;
  final IconData icon;
  final Color color;
  final VoidCallback? onTap;
  final List<String>? filters;
  final ValueChanged<String>? onFilterTap;

  const StatCard({
    super.key,
    required this.title,
    required this.value,
    required this.icon,
    required this.color,
  this.onTap,
  this.filters,
  this.onFilterTap,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Container(
                    padding: const EdgeInsets.all(8),
                    decoration: BoxDecoration(
                      color: color.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Icon(
                      icon,
                      size: 24,
                      color: color,
                    ),
                  ),
                  if (onTap != null)
                    Icon(
                      Icons.arrow_forward_ios,
                      size: 16,
                      color: AppTheme.textSecondaryColor,
                    ),
                ],
              ),
              const SizedBox(height: 12),
              Text(
                value,
                style: TextStyle(
                  fontSize: 28,
                  fontWeight: FontWeight.bold,
                  color: color,
                ),
              ),
              const SizedBox(height: 4),
              Text(
                title,
                style: const TextStyle(
                  fontSize: 14,
                  color: AppTheme.textSecondaryColor,
                ),
              ),
              const SizedBox(height: 8),
              if (filters != null && filters!.isNotEmpty)
                Wrap(
                  spacing: 8,
                  runSpacing: 4,
                  children: filters!.map((f) {
                    String key = (() {
                      final l = f.toLowerCase();
                      if (l.contains('all')) return 'all';
                      if (l.contains('active')) return 'active';
                      if (l.contains('expir')) return 'expiring';
                      if (l.contains('expired')) return 'expired';
                      return l.replaceAll(RegExp(r'[^a-z0-9]'), '_');
                    })();

                    return ActionChip(
                      label: Text(f),
                      onPressed: onFilterTap != null ? () => onFilterTap!(key) : null,
                    );
                  }).toList(),
                ),
            ],
          ),
        ),
      ),
    );
  }
}


