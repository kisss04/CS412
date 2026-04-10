import { useCallback, useEffect, useState } from 'react';
import {
  ActivityIndicator,
  Button,
  FlatList,
  Image,
  RefreshControl,
  Text,
  View,
} from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { router } from 'expo-router';

import { DJANGO_ORIGIN } from '@/constants/miniInsta';
import { miniInstaFetch } from '@/lib/miniInstaApi';
import { miniInstaRoutes } from '@/lib/miniInstaRoutes';

type Profile = {
  id: number;
  username: string;
  display_name: string;
  bio_text?: string;
};

type ApiPost = {
  id: number;
  caption?: string;
  primary_image?: string | null;
};

function imageUri(raw?: string | null): string | undefined {
  if (!raw) return undefined;
  if (raw.startsWith('http://') || raw.startsWith('https://')) return raw;
  const base = DJANGO_ORIGIN.replace(/\/$/, '');
  const path = raw.startsWith('/') ? raw : `/${raw}`;
  return `${base}${path}`;
}

export default function ProfileScreen() {
  const [profile, setProfile] = useState<Profile | null>(null);
  const [posts, setPosts] = useState<ApiPost[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState('');

  const load = useCallback(async () => {
    setError('');
    const profileId = await AsyncStorage.getItem('profile_id');
    if (!profileId) {
      router.replace(miniInstaRoutes.login);
      return;
    }
    const [pRes, postsRes] = await Promise.all([
      miniInstaFetch(`/api/profiles/${profileId}/`),
      miniInstaFetch(`/api/profiles/${profileId}/posts/`),
    ]);
    if (!pRes.ok) {
      setError(`Profile failed (${pRes.status})`);
      setProfile(null);
      setPosts([]);
      return;
    }
    if (!postsRes.ok) {
      setError(`Posts failed (${postsRes.status})`);
    }
    const pData = await pRes.json();
    setProfile(pData);
    const postsData = postsRes.ok ? await postsRes.json() : [];
    setPosts(Array.isArray(postsData) ? postsData : []);
  }, []);

  useEffect(() => {
    (async () => {
      setLoading(true);
      await load();
      setLoading(false);
    })();
  }, [load]);

  const onRefresh = async () => {
    setRefreshing(true);
    await load();
    setRefreshing(false);
  };

  const logout = async () => {
    await Promise.all([
      AsyncStorage.removeItem('token'),
      AsyncStorage.removeItem('profile_id'),
    ]);
    router.replace(miniInstaRoutes.login);
  };

  if (loading) {
    return (
      <View style={{ flex: 1, justifyContent: 'center' }}>
        <ActivityIndicator size="large" />
      </View>
    );
  }

  return (
    <FlatList
      data={posts}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
      keyExtractor={(item) => String(item.id)}
      ListHeaderComponent={
        <View style={{ paddingBottom: 8 }}>
          <View style={{ padding: 16, gap: 8 }}>
            <Button title="Feed" onPress={() => router.push(miniInstaRoutes.feed)} />
            <Button title="Log out" onPress={logout} color="#c00" />
          </View>
          {error ? <Text style={{ color: 'crimson', paddingHorizontal: 16 }}>{error}</Text> : null}
          {profile ? (
            <View style={{ paddingHorizontal: 16, gap: 4 }}>
              <Text style={{ fontSize: 22, fontWeight: '600' }}>{profile.display_name}</Text>
              <Text style={{ opacity: 0.7 }}>@{profile.username}</Text>
              {profile.bio_text ? <Text>{profile.bio_text}</Text> : null}
            </View>
          ) : null}
          <Text style={{ padding: 16, fontWeight: '600' }}>Your posts</Text>
        </View>
      }
      renderItem={({ item }) => {
        const uri = imageUri(item.primary_image);
        return (
          <View style={{ marginBottom: 16, paddingHorizontal: 12 }}>
            {uri ? (
              <Image source={{ uri }} style={{ width: '100%', height: 280, resizeMode: 'cover' }} />
            ) : null}
            <Text>{item.caption}</Text>
          </View>
        );
      }}
      ListEmptyComponent={
        <Text style={{ paddingHorizontal: 16 }}>
          No posts yet. Create one from the Feed screen.
        </Text>
      }
    />
  );
}
