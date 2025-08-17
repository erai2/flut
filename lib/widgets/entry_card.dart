import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../models/entry.dart';
import 'package:intl/intl.dart';

class EntryCard extends StatelessWidget {
  final Entry entry;
  const EntryCard({super.key, required this.entry});

  @override
  Widget build(BuildContext context) {
    final dateStr = DateFormat('yyyy-MM-dd').format(entry.date);
    return Card(
      child: ListTile(
        onTap: () => context.push('/edit/${entry.id}'),
        title: Text(entry.title.isEmpty ? '(제목 없음)' : entry.title),
        subtitle: Text('$dateStr · 태그: ${entry.tags.join(', ')} · 기분: ${entry.mood}'),
        trailing: const Icon(Icons.chevron_right),
      ),
    );
  }
}
