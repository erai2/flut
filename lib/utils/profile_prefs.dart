import 'package:shared_preferences/shared_preferences.dart';

class ProfilePrefs {
  static const _kName = 'profile.name';
  static const _kBirth = 'profile.birth';
  static const _kNote = 'profile.note';

  static Future<void> save({String? name, String? birth, String? note}) async {
    final p = await SharedPreferences.getInstance();
    if (name != null) await p.setString(_kName, name);
    if (birth != null) await p.setString(_kBirth, birth);
    if (note != null) await p.setString(_kNote, note);
  }

  static Future<Map<String, String>> load() async {
    final p = await SharedPreferences.getInstance();
    return {
      'name': p.getString(_kName) ?? '',
      'birth': p.getString(_kBirth) ?? '',
      'note': p.getString(_kNote) ?? '',
    };
  }
}
