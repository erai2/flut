import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../services/auth_service.dart';
import '../utils/profile_prefs.dart';

class SettingsScreen extends StatelessWidget {
  const SettingsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final auth = AuthService();
    return Scaffold(
      appBar: AppBar(title: const Text('설정')),
      body: ListView(
        children: [
          ListTile(
            leading: const Icon(Icons.login),
            title: const Text('Google 로그인'),
            onTap: () async {
              await auth.signInWithGoogle();
              if (context.mounted) {
                ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('로그인 완료')));
              }
            },
          ),
          ListTile(
            leading: const Icon(Icons.logout),
            title: const Text('로그아웃'),
            onTap: () async {
              await auth.signOut();
              if (context.mounted) {
                ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('로그아웃 완료')));
              }
            },
          ),
          const Padding(
            padding: EdgeInsets.fromLTRB(16, 8, 16, 0),
            child: Text('내 프로필(운세 가중치용, 로컬 저장)', style: TextStyle(fontWeight: FontWeight.bold)),
          ),
          const _ProfileEditor(),
        ],
      ),
    );
  }
}

class _ProfileEditor extends StatefulWidget {
  const _ProfileEditor();
  @override
  State<_ProfileEditor> createState() => _ProfileEditorState();
}

class _ProfileEditorState extends State<_ProfileEditor> {
  final _name = TextEditingController();
  DateTime? _birth;

  @override
  void initState() {
    super.initState();
    ProfilePrefs.load().then((p) {
      _name.text = p['name'] ?? '';
      if ((p['birth'] ?? '').isNotEmpty) {
        final s = p['birth']!;
        _birth = DateTime.tryParse(s);
        setState(() {});
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    final birthStr = _birth == null ? '생년월일 선택' : DateFormat('yyyy-MM-dd').format(_birth!);
    return Card(
      margin: const EdgeInsets.all(12),
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          children: [
            TextField(
              controller: _name,
              decoration: const InputDecoration(labelText: '이름', border: OutlineInputBorder()),
            ),
            const SizedBox(height: 8),
            Row(
              children: [
                Expanded(child: Text(birthStr)),
                TextButton.icon(
                  icon: const Icon(Icons.event),
                  label: const Text('생년월일'),
                  onPressed: () async {
                    final now = DateTime.now();
                    final picked = await showDatePicker(
                      context: context,
                      initialDate: _birth ?? DateTime(now.year-20, now.month, now.day),
                      firstDate: DateTime(1900),
                      lastDate: DateTime(2100),
                    );
                    if (picked != null) setState(() => _birth = picked);
                  },
                )
              ],
            ),
            const SizedBox(height: 8),
            FilledButton.icon(
              icon: const Icon(Icons.save),
              label: const Text('프로필 저장(로컬)'),
              onPressed: () async {
                await ProfilePrefs.save(
                  name: _name.text.trim(),
                  birth: _birth == null ? null : DateFormat('yyyy-MM-dd').format(_birth!),
                );
                if (context.mounted) {
                  ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('저장됨')));
                }
              },
            ),
          ],
        ),
      ),
    );
  }
}
