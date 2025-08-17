import 'package:flutter/material.dart';
import 'utils/router.dart';
import 'utils/theme.dart';

class MyDiaryApp extends StatelessWidget {
  const MyDiaryApp({super.key});
  @override
  Widget build(BuildContext context) {
    return MaterialApp.router(
      title: '내 일기장',
      theme: AppTheme.light,
      routerConfig: appRouter,
      debugShowCheckedModeBanner: false,
    );
  }
}
