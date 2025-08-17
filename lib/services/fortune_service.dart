import 'dart:math';
import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:firebase_auth/firebase_auth.dart';
import '../models/fortune.dart';

class FortuneService {
  final _db = FirebaseFirestore.instance;

  CollectionReference<Map<String, dynamic>> _col(String uid) =>
    _db.collection('users').doc(uid).collection('fortunes');

  String _docId(DateTime d) =>
      '${d.year.toString().padLeft(4,'0')}-${d.month.toString().padLeft(2,'0')}-${d.day.toString().padLeft(2,'0')}';

  int _hash(String s) {
    var h = 0x811C9DC5;
    for (final c in s.codeUnits) {
      h ^= c;
      h = (h * 0x01000193) & 0xFFFFFFFF;
    }
    return h & 0x7FFFFFFF;
  }

  Fortune _generate(String uid, DateTime date, {String? birth}) {
    final id = _docId(date);
    final seed = '$uid|$id|${birth ?? ""}';
    final h = _hash(seed);
    final rnd = Random(h);

    final score = 40 + rnd.nextInt(61);
    const colors = ['Indigo','Blue','Teal','Green','Amber','Orange','Pink','Purple','Red','Cyan'];
    const items  = ['Notebook','Pen','Watch','Ring','Bookmark','Mug','Scarf','Keychain','Wallet','Earphones'];
    const tagsBank = [
      ['집중','생산성'], ['관계','커뮤니케이션'], ['행운','기회'], ['재정','절약'],
      ['건강','휴식'], ['학습','성장'], ['여행','이동'], ['정리','미니멀']
    ];
    final luckyColor = colors[rnd.nextInt(colors.length)];
    final luckyItem  = items[rnd.nextInt(items.length)];
    final tags       = tagsBank[rnd.nextInt(tagsBank.length)];
    final advicePool = [
      '중요한 결정을 오전에 처리하세요.',
      '연락이 끊긴 사람에게 먼저 안부를 전하면 기회가 옵니다.',
      '지출 계획을 점검하고 작은 절약부터 시작하세요.',
      '산책 20분으로 에너지를 회복하세요.',
      '작은 정리부터: 책상 위 5분만.',
      '오늘은 “듣기”가 설득보다 강합니다.',
      '배운 것을 짧게 기록으로 남기세요.',
    ];
    final advice = advicePool[rnd.nextInt(advicePool.length)];
    final summary = score >= 80
        ? '컨디션·기회 모두 좋은 날'
        : score >= 60 ? '안정적이고 무난한 흐름' : '속도를 늦추고 점검 추천';

    return Fortune(
      id: id,
      date: date,
      seed: seed,
      summary: summary,
      score: score,
      luckyColor: luckyColor,
      luckyItem: luckyItem,
      advice: advice,
      tags: tags,
    );
  }

  Future<Fortune> getOrCreateToday({DateTime? day, String? birth}) async {
    final uid = FirebaseAuth.instance.currentUser!.uid;
    final d = DateTime((day ?? DateTime.now()).year, (day ?? DateTime.now()).month, (day ?? DateTime.now()).day);
    final id = _docId(d);
    final doc = await _col(uid).doc(id).get();
    if (doc.exists) return Fortune.fromDoc(doc);
    final f = _generate(uid, d, birth: birth);
    await _col(uid).doc(id).set(f.toMap(), SetOptions(merge: true));
    return f;
  }

  Stream<List<Fortune>> watchMonth(DateTime month) {
    final uid = FirebaseAuth.instance.currentUser!.uid;
    final start = DateTime(month.year, month.month, 1);
    final end = DateTime(month.year, month.month + 1, 1);
    return _col(uid)
      .where('date', isGreaterThanOrEqualTo: Timestamp.fromDate(start))
      .where('date', isLessThan: Timestamp.fromDate(end))
      .orderBy('date', descending: true)
      .snapshots()
      .map((s) => s.docs.map(Fortune.fromDoc).toList());
  }

  Future<void> linkEntry(String fortuneId, String entryId) async {
    final uid = FirebaseAuth.instance.currentUser!.uid;
    await _col(uid).doc(fortuneId).update({'linkedEntryId': entryId});
  }
}
