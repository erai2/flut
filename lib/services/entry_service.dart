import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:uuid/uuid.dart';
import '../models/entry.dart';

class EntryService {
  final _db = FirebaseFirestore.instance;

  EntryService() {
    _db.settings = const Settings(persistenceEnabled: true);
  }

  CollectionReference<Map<String, dynamic>> _col(String uid) =>
    _db.collection('users').doc(uid).collection('entries');

  Future<String> createOrUpdate(Entry e) async {
    final uid = FirebaseAuth.instance.currentUser!.uid;
    final id = e.id.isEmpty ? const Uuid().v4() : e.id;
    await _col(uid).doc(id).set(e.toMap(), SetOptions(merge: true));
    return id;
  }

  Stream<List<Entry>> watchByMonth(DateTime month) {
    final uid = FirebaseAuth.instance.currentUser!.uid;
    final start = DateTime(month.year, month.month, 1);
    final end = DateTime(month.year, month.month + 1, 1);
    return _col(uid)
        .where('date', isGreaterThanOrEqualTo: Timestamp.fromDate(start))
        .where('date', isLessThan: Timestamp.fromDate(end))
        .orderBy('date', descending: true)
        .snapshots()
        .map((s) => s.docs.map(Entry.fromDoc).toList());
  }

  Future<Entry?> getById(String id) async {
    final uid = FirebaseAuth.instance.currentUser!.uid;
    final doc = await _col(uid).doc(id).get();
    if (!doc.exists) return null;
    return Entry.fromDoc(doc);
  }

  Future<void> delete(String id) async {
    final uid = FirebaseAuth.instance.currentUser!.uid;
    await _col(uid).doc(id).delete();
  }

  Stream<List<Entry>> search(String q) {
    final uid = FirebaseAuth.instance.currentUser!.uid;
    return _col(uid).orderBy('updatedAt', descending: true).limit(100).snapshots()
      .map((s) => s.docs.map(Entry.fromDoc).where((e) =>
          e.title.toLowerCase().contains(q.toLowerCase()) ||
          e.contentMarkdown.toLowerCase().contains(q.toLowerCase()) ||
          e.tags.any((t) => t.toLowerCase().contains(q.toLowerCase()))
      ).toList());
  }
}
