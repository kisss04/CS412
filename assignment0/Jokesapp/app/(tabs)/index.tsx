import { useEffect, useState } from 'react';
import { View, Text, Image, Button, StyleSheet } from 'react-native';

export default function TabOneScreen() {
  const [joke, setJoke] = useState<any>(null);
  const [picture, setPicture] = useState<any>(null);

  const fetchRandom = async () => {
    try {
      const jokeRes = await fetch('http://10.193.105.20:8000/jokesapp/api/random_joke');
      const jokeData = await jokeRes.json();
      setJoke(jokeData);

      const picRes = await fetch('http://10.193.105.20:8000/jokesapp/api/random_picture');
      const picData = await picRes.json();
      setPicture(picData);
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => { fetchRandom(); }, []);

  return (
    <View style={styles.container}>
      {joke && <Text style={styles.joke}>{joke.text}</Text>}
      {picture && <Image source={{ uri: picture.image_url }} style={styles.image} />}
      <Button title="New Joke!" onPress={fetchRandom} />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, alignItems: 'center', justifyContent: 'center', padding: 20 },
  joke: { fontSize: 18, textAlign: 'center', marginBottom: 20 },
  image: { width: 300, height: 200, marginBottom: 20 },
});
