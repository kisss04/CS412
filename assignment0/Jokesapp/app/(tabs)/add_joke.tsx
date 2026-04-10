import { useState } from 'react';
import { View, Text, TextInput, Button, StyleSheet } from 'react-native';

export default function AddJoke() {
  const [jokeText, setJokeText] = useState('');
  const [name, setName] = useState('');

  const submitJoke = () => {
    fetch('http://10.193.105.20:8000/jokesapp/api/jokes', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text: jokeText, contributor: name }),
    })
    .then(res => res.json())
    .then(data => console.log(data));
  };

  return (
    <View style={styles.container}>
      <Text style={styles.label}>Your Joke:</Text>
      <TextInput style={styles.input} value={jokeText} onChangeText={setJokeText} placeholder="Enter your joke" />
      <Text style={styles.label}>Your Name:</Text>
      <TextInput style={styles.input} value={name} onChangeText={setName} placeholder="Enter your name" />
      <Button title="Submit Joke" onPress={submitJoke} />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 20 },
  label: { fontSize: 16, marginBottom: 5 },
  input: { borderWidth: 1, borderColor: '#ccc', padding: 10, marginBottom: 15, borderRadius: 5 },
});
