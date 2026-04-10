import { Stack } from 'expo-router';

export default function MiniInstaLayout() {
  return (
    <Stack>
      <Stack.Screen name="login" options={{ title: 'Mini Insta — Login' }} />
      <Stack.Screen name="feed" options={{ title: 'Feed' }} />
      <Stack.Screen name="new-post" options={{ title: 'New Post' }} />
      <Stack.Screen name="profile" options={{ title: 'Profile' }} />
    </Stack>
  );
}
