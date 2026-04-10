import { View, Text, Image } from 'react-native';
import { styles } from '../../assets/my_styles';

export default function AboutScreen() {
  return (
    <View style={styles.container}>
      <Text style={styles.titleText}>About Me</Text>

      <Text style={styles.bodyText}>
        I am spongebob.
      </Text>

      <Image
        source={require('../../assets/images/download.jpeg')}
        style={styles.image}
      />
    </View>
  );
}