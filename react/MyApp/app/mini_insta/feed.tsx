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

export default function FeedScreen() {
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
    const res = await miniInstaFetch(`/api/profiles/${profileId}/feed/`);
    if (!res.ok) {
      setError(`Feed failed (${res.status})`);
      setPosts([]);
      return;
    }
    const data = await res.json();
    setPosts(Array.isArray(data) ? data : []);
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

  if (loading) {
    return (
      <View style={{ flex: 1, justifyContent: 'center' }}>
        <ActivityIndicator size="large" />
      </View>
    );
  }

  return (
    <View style={{ flex: 1 }}>
      <View style={{ padding: 12, gap: 8 }}>
        <Button title="New post" onPress={() => router.push(miniInstaRoutes.newPost)} />
        <Button title="My profile" onPress={() => router.push(miniInstaRoutes.profile)} />
      </View>
      {error ? <Text style={{ color: 'crimson', paddingHorizontal: 16 }}>{error}</Text> : null}
      <FlatList
        data={posts}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
        keyExtractor={(item) => String(item.id)}
        renderItem={({ item }) => {
          const uri = imageUri(item.primary_image);
          return (
            <View style={{ marginBottom: 16, paddingHorizontal: 12 }}>
              {uri ? (
                <Image source={{ uri }} style={{ width: '100%', height: 300, resizeMode: 'cover' }} />
              ) : null}
              <Text>{item.caption}</Text>
            </View>
          );
        }}
        ListEmptyComponent={
          <Text style={{ padding: 16 }}>
            No posts in your feed yet. Follow other profiles on the web app, or ask friends to post.
          </Text>
        }
      />
    </View>
  );
}
