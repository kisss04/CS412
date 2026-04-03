import { View, Text, Image } from 'react-native';
import { styles } from '../../assets/my_styles';

export default function IndexScreen() {
  return (
    <View style={styles.container}>
      <Text style={styles.titleText}>Home page</Text>
      <Text style={styles.bodyText}>
        hahah
      </Text>

      <Image
        source={require('../../assets/images/download.jpeg')}
        style={styles.image}
      />
    </View>
  );
}