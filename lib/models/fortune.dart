import 'package:cloud_firestore/cloud_firestore.dart';

class Fortune {
  final String id; // yyyy-MM-dd
  final DateTime date;
  final String seed;
  final String summary;
  final int score; // 1~100
  final String luckyColor;
  final String luckyItem;
  final String advice;
  final List<String> tags;
  final String? linkedEntryId;

  Fortune({
    required this.id,
    required this.date,
    required this.seed,
    required this.summary,
    required this.score,
    required this.luckyColor,
    required this.luckyItem,
    required this.advice,
    required this.tags,
    this.linkedEntryId,
  });

  Map<String, dynamic> toMap() => {
    'date': Timestamp.fromDate(date),
    'seed': seed,
    'summary': summary,
    'score': score,
    'luckyColor': luckyColor,
    'luckyItem': luckyItem,
    'advice': advice,
    'tags': tags,
    'linkedEntryId': linkedEntryId,
  };

  factory Fortune.fromDoc(DocumentSnapshot doc) {
    final d = doc.data() as Map<String, dynamic>;
    return Fortune(
      id: doc.id,
      date: (d['date'] as Timestamp).toDate(),
      seed: (d['seed'] ?? '') as String,
      summary: (d['summary'] ?? '') as String,
      score: (d['score'] ?? 50) as int,
      luckyColor: (d['luckyColor'] ?? 'Indigo') as String,
      luckyItem: (d['luckyItem'] ?? 'Notebook') as String,
      advice: (d['advice'] ?? '') as String,
      tags: List<String>.from(d['tags'] ?? const []),
      linkedEntryId: d['linkedEntryId'],
    );
  }
}
