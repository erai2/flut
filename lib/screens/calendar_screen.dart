import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../services/entry_service.dart';
import '../models/entry.dart';
import 'package:go_router/go_router.dart';

class CalendarScreen extends StatefulWidget {
  const CalendarScreen({super.key});
  @override
  State<CalendarScreen> createState() => _CalendarScreenState();
}

class _CalendarScreenState extends State<CalendarScreen> {
  DateTime _month = DateTime(DateTime.now().year, DateTime.now().month);
  final _svc = EntryService();

  @override
  Widget build(BuildContext context) {
    final firstDay = DateTime(_month.year, _month.month, 1);
    final firstWeekday = firstDay.weekday % 7;
    final daysInMonth = DateTime(_month.year, _month.month + 1, 0).day;

    return Scaffold(
      appBar: AppBar(
        title: Text('캘린더 · ${DateFormat('yyyy.MM').format(_month)}'),
        actions: [
          IconButton(onPressed: () => setState(() => _month = DateTime(_month.year, _month.month - 1)), icon: const Icon(Icons.chevron_left)),
          IconButton(onPressed: () => setState(() => _month = DateTime(_month.year, _month.month + 1)), icon: const Icon(Icons.chevron_right)),
        ],
      ),
      body: StreamBuilder<List<Entry>>(
        stream: _svc.watchByMonth(_month),
        builder: (_, snap) {
          final byDay = <int, List<Entry>>{};
          if (snap.hasData) {
            for (final e in snap.data!) {
              byDay[e.date.day] = [...(byDay[e.date.day] ?? []), e];
            }
          }
          return GridView.builder(
            padding: const EdgeInsets.all(12),
            gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
              crossAxisCount: 7, crossAxisSpacing: 6, mainAxisSpacing: 6),
            itemCount: firstWeekday + daysInMonth,
            itemBuilder: (_, i) {
              if (i < firstWeekday) return const SizedBox.shrink();
              final day = i - firstWeekday + 1;
              final entries = byDay[day] ?? [];
              return InkWell(
                onTap: () => context.push('/edit', extra: DateTime(_month.year, _month.month, day)),
                child: Container(
                  padding: const EdgeInsets.all(6),
                  decoration: BoxDecoration(
                    border: Border.all(color: Theme.of(context).dividerColor),
                    borderRadius: BorderRadius.circular(6),
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text('$day', style: const TextStyle(fontWeight: FontWeight.bold)),
                      const SizedBox(height: 4),
                      ...entries.take(3).map((e) =>
                        Text('• ${e.title.isEmpty ? '(제목 없음)' : e.title}', maxLines: 1, overflow: TextOverflow.ellipsis, style: const TextStyle(fontSize: 11))),
                      if (entries.length > 3) const Text('…', style: TextStyle(fontSize: 11)),
                    ],
                  ),
                ),
              );
            },
          );
        },
      ),
    );
  }
}
