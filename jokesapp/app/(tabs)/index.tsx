import { useEffect, useState } from 'react';
import { View, Text, Image, Button } from 'react-native';
import { styles } from '../../assets/my_styles';

export default function TabOne() {
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