import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../screens/home_screen.dart';
import '../screens/edit_entry_screen.dart';
import '../screens/calendar_screen.dart';
import '../screens/settings_screen.dart';
import '../screens/fortune_today_screen.dart';

final appRouter = GoRouter(
  routes: [
    GoRoute(path: '/', builder: (_, __) => const HomeScreen()),
    GoRoute(path: '/fortune', builder: (_, __) => const FortuneTodayScreen()),
    GoRoute(path: '/edit', builder: (_, st) => EditEntryScreen(id: null)),
    GoRoute(path: '/edit/:id', builder: (ctx, st) => EditEntryScreen(id: st.pathParameters['id'])),
    GoRoute(path: '/calendar', builder: (_, __) => const CalendarScreen()),
    GoRoute(path: '/settings', builder: (_, __) => const SettingsScreen()),
  ],
);
