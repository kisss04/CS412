import { ScrollView, Text, Image } from 'react-native';
import { styles } from '../../assets/my_styles';

export default function DetailScreen() {
  return (
    <ScrollView contentContainerStyle={styles.scrollContainer}>
      <Text style={styles.titleText}>Spongebob</Text>

      <Text style={styles.bodyText}>
        This is where he lives
      </Text>

      <Image
        source={{ uri: 'https://static.wikia.nocookie.net/nickelodeon/images/d/d1/SpongeBob_SquarePants%27_house.png' }}
        style={styles.image}
      />

      <Text style={styles.bodyText}>
        these are his friends.
      </Text>

      <Image
        source={{ uri: 'https://i.pinimg.com/originals/a2/f9/e4/a2f9e4c9958b5010ec68cdbe5dbb9bc9.jpg' }}
        style={styles.image}
      />
    </ScrollView>
  );
}