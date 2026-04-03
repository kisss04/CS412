import { Tabs } from 'expo-router';

export default function TabLayout() {
  return (
    <Tabs>
      <Tabs.Screen name="index" options={{ title: 'Home' }} />
      <Tabs.Screen name="jokes_list" options={{ title: 'All Jokes' }} />
      <Tabs.Screen name="add_joke" options={{ title: 'Add Joke' }} />
    </Tabs>
  );
}
