import { useState } from 'react';
import { Button, Text, TextInput, View } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { router } from 'expo-router';

import { MINI_INSTA_API_BASE } from '@/constants/miniInsta';
import { miniInstaRoutes } from '@/lib/miniInstaRoutes';

export default function LoginScreen() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const login = async () => {
    setError('');
    try {
      const res = await fetch(`${MINI_INSTA_API_BASE}/api/login/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password }),
      });
      const data = (await res.json()) as { token?: string; profile_id?: number; error?: string };
      if (data.token && data.profile_id != null) {
        await AsyncStorage.setItem('token', data.token);
        await AsyncStorage.setItem('profile_id', String(data.profile_id));
        router.replace(miniInstaRoutes.feed);
      } else {
        setError(data.error ?? (res.ok ? 'Login failed' : `HTTP ${res.status}`));
      }
    } catch {
      setError('Could not reach server (is Django running?)');
    }
  };

  return (
    <View style={{ padding: 20, gap: 12 }}>
      <TextInput
        placeholder="Username"
        autoCapitalize="none"
        value={username}
        onChangeText={setUsername}
        style={{ borderWidth: 1, padding: 8 }}
      />
      <TextInput
        placeholder="Password"
        secureTextEntry
        value={password}
        onChangeText={setPassword}
        style={{ borderWidth: 1, padding: 8 }}
      />
      {error ? <Text style={{ color: 'red' }}>{error}</Text> : null}
      <Button title="Login" onPress={login} />
    </View>
  );
}
