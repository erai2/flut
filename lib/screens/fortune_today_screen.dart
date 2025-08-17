import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:go_router/go_router.dart';
import '../services/fortune_service.dart';
import '../models/fortune.dart';
import '../utils/profile_prefs.dart';

class FortuneTodayScreen extends StatefulWidget {
  const FortuneTodayScreen({super.key});
  @override
  State<FortuneTodayScreen> createState() => _FortuneTodayScreenState();
}

class _FortuneTodayScreenState extends State<FortuneTodayScreen> {
  final _svc = FortuneService();
  Fortune? _fortune;
  bool _loading = true;
  String _birth = '';

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    final profile = await ProfilePrefs.load();
    _birth = profile['birth'] ?? '';
    final f = await _svc.getOrCreateToday(birth: _birth.isEmpty ? null : _birth);
    setState(() { _fortune = f; _loading = false; });
  }

  @override
  Widget build(BuildContext context) {
    final d = DateFormat('yyyy-MM-dd').format(DateTime.now());
    return Scaffold(
      appBar: AppBar(title: Text('오늘의 운세 · $d'), actions: [
        IconButton(icon: const Icon(Icons.history), onPressed: () => context.push('/calendar')),
      ]),
      body: _loading || _fortune == null
        ? const Center(child: CircularProgressIndicator())
        : Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              children: [
                Card(
                  child: ListTile(
                    title: Text(_fortune!.summary, style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                    subtitle: Text('행운 점수: ${_fortune!.score}/100'),
                    trailing: CircleAvatar(child: Text(_fortune!.score.toString())),
                  ),
                ),
                const SizedBox(height: 8),
                Row(
                  children: [
                    Expanded(child: _InfoChip(label: 'Lucky Color', value: _fortune!.luckyColor)),
                    const SizedBox(width: 8),
                    Expanded(child: _InfoChip(label: 'Lucky Item', value: _fortune!.luckyItem)),
                  ],
                ),
                const SizedBox(height: 8),
                Align(
                  alignment: Alignment.centerLeft,
                  child: Wrap(
                    spacing: 8,
                    children: _fortune!.tags.map((t) => Chip(label: Text('#$t'))).toList(),
                  ),
                ),
                const SizedBox(height: 12),
                Container(
                  width: double.infinity,
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    border: Border.all(color: Theme.of(context).dividerColor),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Text('오늘의 팁: ${_fortune!.advice}'),
                ),
                const Spacer(),
                FilledButton.icon(
                  icon: const Icon(Icons.edit_note),
                  label: const Text('이 운세로 일기 쓰기'),
                  onPressed: () => context.push('/edit', extra: {'fortuneId': _fortune!.id}),
                ),
              ],
            ),
          ),
    );
  }
}

class _InfoChip extends StatelessWidget {
  final String label;
  final String value;
  const _InfoChip({required this.label, required this.value});
  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        border: Border.all(color: Theme.of(context).dividerColor),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [Text(label, style: const TextStyle(fontWeight: FontWeight.bold)), Text(value)],
      ),
    );
  }
}
