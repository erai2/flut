import 'package:firebase_auth/firebase_auth.dart';
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:intl/intl.dart';
import '../models/entry.dart';
import '../services/auth_service.dart';
import '../services/entry_service.dart';
import '../widgets/entry_card.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});
  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final _auth = AuthService();
  late final EntryService _entryService;
  DateTime _month = DateTime.now();
  String _query = '';

  @override
  void initState() {
    super.initState();
    _entryService = EntryService();
    _auth.ensureSignedIn();
  }

  @override
  Widget build(BuildContext context) {
    final uid = FirebaseAuth.instance.currentUser?.uid;
    return Scaffold(
      appBar: AppBar(
        title: Text('내 일기장 · ${DateFormat('yyyy.MM').format(_month)}'),
        actions: [
          IconButton(
            onPressed: () => context.push('/fortune'),
            icon: const Icon(Icons.stars),
          ),
          IconButton(
            onPressed: () => context.push('/calendar'),
            icon: const Icon(Icons.calendar_month),
          ),
          IconButton(
            onPressed: () => context.push('/settings'),
            icon: const Icon(Icons.settings),
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () => context.push('/edit'),
        label: const Text('새 일기'),
        icon: const Icon(Icons.edit),
      ),
      body: uid == null
          ? const Center(child: CircularProgressIndicator())
          : Column(
              children: [
                Padding(
                  padding: const EdgeInsets.all(12),
                  child: TextField(
                    decoration: const InputDecoration(
                      hintText: '검색: 제목/내용/태그',
                      prefixIcon: Icon(Icons.search),
                      border: OutlineInputBorder(),
                    ),
                    onChanged: (v) => setState(() => _query = v),
                  ),
                ),
                Expanded(
                  child: _query.isEmpty
                      ? StreamBuilder<List<Entry>>(
                          stream: _entryService.watchByMonth(_month),
                          builder: (_, snap) {
                            if (!snap.hasData) {
                              return const Center(child: CircularProgressIndicator());
                            }
                            final items = snap.data!;
                            if (items.isEmpty) return const Center(child: Text('이번 달 일기가 없습니다.'));
                            return ListView.builder(
                              itemCount: items.length,
                              itemBuilder: (_, i) => EntryCard(entry: items[i]),
                            );
                          },
                        )
                      : StreamBuilder<List<Entry>>(
                          stream: _entryService.search(_query),
                          builder: (_, snap) {
                            if (!snap.hasData) {
                              return const Center(child: CircularProgressIndicator());
                            }
                            final items = snap.data!;
                            if (items.isEmpty) return const Center(child: Text('검색 결과 없음'));
                            return ListView.builder(
                              itemCount: items.length,
                              itemBuilder: (_, i) => EntryCard(entry: items[i]),
                            );
                          },
                        ),
                ),
              ],
            ),
    );
  }
}
