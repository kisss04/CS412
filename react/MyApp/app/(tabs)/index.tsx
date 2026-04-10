import { Link } from 'expo-router';
import { View, Text, Image } from 'react-native';
import { styles } from '../../assets/my_styles';
import { miniInstaRoutes } from '@/lib/miniInstaRoutes';

export default function IndexScreen() {
  return (
    <View style={styles.container}>
      <Text style={styles.titleText}>Home page</Text>
      <Text style={styles.bodyText}>
        hahah
      </Text>

      <Link href={miniInstaRoutes.login} style={{ marginVertical: 12, color: 'blue' }}>
        Open Mini Insta (login)
      </Link>

      <Image
        source={require('../../assets/images/download.jpeg')}
        style={styles.image}
      />
    </View>
  );
}