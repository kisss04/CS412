import { useEffect, useState } from 'react';
import { View, Text, FlatList, StyleSheet } from 'react-native';

export default function JokesList() {
  const [jokes, setJokes] = useState<any[]>([]);

  useEffect(() => {
    fetch('http://10.193.105.20:8000/jokesapp/api/jokes')
      .then(res => res.json())
      .then(data => setJokes(data));
  }, []);

  return (
    <View style={styles.container}>
      <FlatList
        data={jokes}
        keyExtractor={(item) => item.id.toString()}
        renderItem={({ item }) => (
          <View style={styles.jokeItem}>
            <Text style={styles.jokeText}>{item.text}</Text>
            <Text style={styles.contributor}>— {item.contributor}</Text>
          </View>
        )}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 20 },
  jokeItem: { marginBottom: 20, borderBottomWidth: 1, borderColor: '#ccc', paddingBottom: 10 },
  jokeText: { fontSize: 16 },
  contributor: { fontSize: 12, color: 'gray' },
});