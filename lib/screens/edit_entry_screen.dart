import 'dart:io';
import 'package:flutter/material.dart';
import 'package:flutter_markdown/flutter_markdown.dart';
import 'package:image_picker/image_picker.dart';
import 'package:go_router/go_router.dart';
import 'package:intl/intl.dart';
import '../models/entry.dart';
import '../services/entry_service.dart';
import '../services/storage_service.dart';
import 'package:firebase_auth/firebase_auth.dart';

class EditEntryScreen extends StatefulWidget {
  final String? id;
  const EditEntryScreen({super.key, this.id});

  @override
  State<EditEntryScreen> createState() => _EditEntryScreenState();
}

class _EditEntryScreenState extends State<EditEntryScreen> {
  final _title = TextEditingController();
  final _content = TextEditingController();
  final _tags = TextEditingController();
  int _mood = 3;
  DateTime _date = DateTime.now();
  List<String> _images = [];
  final _entryService = EntryService();
  final _storage = StorageService();

  bool _loading = false;

  @override
  void initState() {
    super.initState();
    _loadIfEdit();
    _loadFromExtra();
  }

  Future<void> _loadIfEdit() async {
    if (widget.id == null) return;
    setState(() => _loading = true);
    final e = await _entryService.getById(widget.id!);
    if (e != null) {
      _title.text = e.title;
      _content.text = e.contentMarkdown;
      _tags.text = e.tags.join(', ');
      _mood = e.mood;
      _date = e.date;
      _images = List.of(e.imageUrls);
    }
    setState(() => _loading = false);
  }

  void _loadFromExtra() {
    final extra = GoRouterState.of(context).extra;
    if (widget.id == null && extra is Map && extra['fortuneId'] != null) {
      final today = DateTime.now();
      _title.text = '오늘의 운세 일기 (${DateFormat('yyyy-MM-dd').format(today)})';
      _content.text = '''
**오늘의 요약**  
- 점수: (자동 저장된 운세에서 확인)
- 한 줄: 오늘의 흐름 메모

**느낀 점**  
- 

**실행 TODO (행운 아이템/컬러 활용)**  
- 
''';
      setState(() {});
    }
  }

  Future<void> _pickImage() async {
    final picker = ImagePicker();
    final x = await picker.pickImage(source: ImageSource.gallery, maxWidth: 2000);
    if (x == null) return;
    setState(() => _loading = true);
    final url = await _storage.uploadImage(File(x.path));
    setState(() {
      _images.add(url);
      _loading = false;
    });
  }

  Future<void> _save() async {
    setState(() => _loading = true);
    final uid = FirebaseAuth.instance.currentUser!.uid;
    final now = DateTime.now();
    final entry = Entry(
      id: widget.id ?? '',
      userId: uid,
      date: _date,
      title: _title.text.trim(),
      contentMarkdown: _content.text,
      tags: _tags.text.split(',').map((e) => e.trim()).where((e) => e.isNotEmpty).toList(),
      mood: _mood,
      imageUrls: _images,
      createdAt: now,
      updatedAt: now,
    );
    final id = await _entryService.createOrUpdate(entry);
    if (mounted) {
      setState(() => _loading = false);
      context.go('/edit/$id');
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('저장 완료')));
    }
  }

  @override
  Widget build(BuildContext context) {
    final dateStr = DateFormat('yyyy-MM-dd').format(_date);
    return Scaffold(
      appBar: AppBar(
        title: Text(widget.id == null ? '새 일기' : '일기 편집'),
        actions: [
          IconButton(onPressed: _loading ? null : _save, icon: const Icon(Icons.save)),
        ],
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : ListView(
              padding: const EdgeInsets.all(12),
              children: [
                Row(
                  children: [
                    TextButton.icon(
                      onPressed: () async {
                        final picked = await showDatePicker(
                          context: context, initialDate: _date,
                          firstDate: DateTime(2000), lastDate: DateTime(2100));
                        if (picked != null) setState(() => _date = picked);
                      },
                      icon: const Icon(Icons.event),
                      label: Text(dateStr),
                    ),
                    const Spacer(),
                    DropdownButton<int>(
                      value: _mood,
                      onChanged: (v) => setState(() => _mood = v ?? 3),
                      items: const [
                        DropdownMenuItem(value: 1, child: Text('😞 1')),
                        DropdownMenuItem(value: 2, child: Text('🙁 2')),
                        DropdownMenuItem(value: 3, child: Text('😐 3')),
                        DropdownMenuItem(value: 4, child: Text('🙂 4')),
                        DropdownMenuItem(value: 5, child: Text('😄 5')),
                      ],
                    ),
                  ],
                ),
                TextField(
                  controller: _title,
                  decoration: const InputDecoration(
                    labelText: '제목', border: OutlineInputBorder()),
                ),
                const SizedBox(height: 12),
                TextField(
                  controller: _tags,
                  decoration: const InputDecoration(
                    labelText: '태그 (쉼표 구분)', border: OutlineInputBorder()),
                ),
                const SizedBox(height: 12),
                Row(
                  children: [
                    const Text('이미지'),
                    const SizedBox(width: 8),
                    OutlinedButton.icon(
                      onPressed: _pickImage,
                      icon: const Icon(Icons.image),
                      label: const Text('추가'),
                    ),
                  ],
                ),
                Wrap(
                  spacing: 8, runSpacing: 8,
                  children: _images.map((u) => Stack(
                    alignment: Alignment.topRight,
                    children: [
                      ClipRRect(
                        borderRadius: BorderRadius.circular(8),
                        child: Image.network(u, width: 120, height: 120, fit: BoxFit.cover),
                      ),
                      IconButton(
                        icon: const Icon(Icons.close, size: 18),
                        onPressed: () => setState(() => _images.remove(u)),
                      )
                    ],
                  )).toList(),
                ),
                const SizedBox(height: 12),
                const Text('Markdown 본문 (우측 실시간 미리보기)'),
                const SizedBox(height: 8),
                SizedBox(
                  height: 300,
                  child: Row(
                    children: [
                      Expanded(
                        child: TextField(
                          controller: _content,
                          maxLines: null,
                          expands: true,
                          decoration: const InputDecoration(
                            border: OutlineInputBorder(), hintText: '# 오늘의 기록...'),
                          onChanged: (_) => setState(() {}),
                        ),
                      ),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Container(
                          decoration: BoxDecoration(
                            border: Border.all(color: Theme.of(context).dividerColor),
                            borderRadius: BorderRadius.circular(4),
                          ),
                          child: Markdown(data: _content.text),
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
    );
  }
}
