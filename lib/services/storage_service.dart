import 'dart:io';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:firebase_storage/firebase_storage.dart';

class StorageService {
  final _st = FirebaseStorage.instance;

  Future<String> uploadImage(File file) async {
    final uid = FirebaseAuth.instance.currentUser!.uid;
    final name = DateTime.now().millisecondsSinceEpoch.toString();
    final ref = _st.ref().child('users/$uid/images/$name.jpg');
    final task = await ref.putFile(file);
    return await task.ref.getDownloadURL();
  }
}
