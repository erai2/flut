import 'package:cloud_firestore/cloud_firestore.dart';

class Entry {
  final String id;
  final String userId;
  final DateTime date;
  final String title;
  final String contentMarkdown;
  final List<String> tags;
  final int mood; // 1~5
  final List<String> imageUrls;
  final DateTime createdAt;
  final DateTime updatedAt;

  Entry({
    required this.id,
    required this.userId,
    required this.date,
    required this.title,
    required this.contentMarkdown,
    required this.tags,
    required this.mood,
    required this.imageUrls,
    required this.createdAt,
    required this.updatedAt,
  });

  Map<String, dynamic> toMap() => {
    'userId': userId,
    'date': Timestamp.fromDate(date),
    'title': title,
    'contentMarkdown': contentMarkdown,
    'tags': tags,
    'mood': mood,
    'imageUrls': imageUrls,
    'createdAt': Timestamp.fromDate(createdAt),
    'updatedAt': Timestamp.fromDate(updatedAt),
  };

  factory Entry.fromDoc(DocumentSnapshot doc) {
    final d = doc.data() as Map<String, dynamic>;
    return Entry(
      id: doc.id,
      userId: d['userId'],
      date: (d['date'] as Timestamp).toDate(),
      title: d['title'] ?? '',
      contentMarkdown: d['contentMarkdown'] ?? '',
      tags: List<String>.from(d['tags'] ?? []),
      mood: d['mood'] ?? 3,
      imageUrls: List<String>.from(d['imageUrls'] ?? []),
      createdAt: (d['createdAt'] as Timestamp).toDate(),
      updatedAt: (d['updatedAt'] as Timestamp).toDate(),
    );
  }
}
