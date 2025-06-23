/// Provides social/friend state and logic for the Pulse Fitness app.
///
/// Handles loading friends, friend requests, and sending/accepting/rejecting requests.

import 'package:flutter/foundation.dart';
import 'package:pulse_fitness/services/api_service.dart';

/// Manages social features such as friends and friend requests.
class SocialProvider with ChangeNotifier {
  List<Map<String, dynamic>> _friends = [];
  List<Map<String, dynamic>> _friendRequests = [];
  bool _isLoading = false;

  /// List of current friends.
  List<Map<String, dynamic>> get friends => _friends;
  /// List of pending friend requests.
  List<Map<String, dynamic>> get friendRequests => _friendRequests;
  /// Whether social state is loading.
  bool get isLoading => _isLoading;

  /// Loads the current user's friends from the backend.
  Future<void> loadFriends() async {
    try {
      _isLoading = true;
      notifyListeners();

      _friends = await ApiService.getFriends();
    } catch (e) {
      print('Error loading friends: $e');
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  /// Loads the current user's pending friend requests from the backend.
  Future<void> loadFriendRequests() async {
    try {
      _isLoading = true;
      notifyListeners();

      _friendRequests = await ApiService.getFriendRequests();
    } catch (e) {
      print('Error loading friend requests: $e');
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  /// Sends a friend request to the given username.
  Future<bool> sendFriendRequest(String username) async {
    try {
      _isLoading = true;
      notifyListeners();

      await ApiService.sendFriendRequest(username);
      return true;
    } catch (e) {
      print('Error sending friend request: $e');
      return false;
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  /// Accepts a friend request by friendship ID.
  Future<bool> acceptFriendRequest(int friendshipId) async {
    try {
      _isLoading = true;
      notifyListeners();

      await ApiService.acceptFriendRequest(friendshipId);

      // Remove from requests and add to friends
      _friendRequests.removeWhere((request) => request['id'] == friendshipId);
      await loadFriends(); // Refresh friends list

      return true;
    } catch (e) {
      print('Error accepting friend request: $e');
      return false;
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  /// Rejects a friend request by friendship ID.
  Future<bool> rejectFriendRequest(int friendshipId) async {
    try {
      _isLoading = true;
      notifyListeners();

      await ApiService.rejectFriendRequest(friendshipId);

      // Remove from requests
      _friendRequests.removeWhere((request) => request['id'] == friendshipId);

      return true;
    } catch (e) {
      print('Error rejecting friend request: $e');
      return false;
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }
}
