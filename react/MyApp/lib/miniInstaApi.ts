import AsyncStorage from '@react-native-async-storage/async-storage';

import { MINI_INSTA_API_BASE } from '@/constants/miniInsta';

export async function miniInstaFetch(path: string, options: RequestInit = {}) {
  const token = await AsyncStorage.getItem('token');
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...(options.headers || {}),
  };
  if (token) {
    (headers as Record<string, string>)['Authorization'] = `Token ${token}`;
  }
  return fetch(`${MINI_INSTA_API_BASE}${path}`, {
    ...options,
    headers,
  });
}
