import { useState } from 'react';
import { Alert, Button, Image, Text, TextInput, View } from 'react-native';
import * as ImagePicker from 'expo-image-picker';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { router } from 'expo-router';

import { MINI_INSTA_API_BASE } from '@/constants/miniInsta';

export default function NewPostScreen() {
  const [image, setImage] = useState<ImagePicker.ImagePickerAsset | null>(null);
  const [caption, setCaption] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const pickImage = async () => {
    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ['images'],
    });
    if (!result.canceled && result.assets[0]) {
      setImage(result.assets[0]);
    }
  };

  const submit = async () => {
    if (!image?.uri) {
      Alert.alert('Pick an image first');
      return;
    }
    setSubmitting(true);
    try {
      const token = await AsyncStorage.getItem('token');
      const profileId = await AsyncStorage.getItem('profile_id');
      const form = new FormData();
      form.append('profile', profileId ?? '');
      form.append('caption', caption);
      form.append('image', {
        uri: image.uri,
        name: 'post.jpg',
        type: 'image/jpeg',
      } as unknown as Blob);

      const res = await fetch(`${MINI_INSTA_API_BASE}/api/posts/`, {
        method: 'POST',
        headers: token ? { Authorization: `Token ${token}` } : {},
        body: form,
      });
      const bodyText = await res.text();
      if (!res.ok) {
        Alert.alert('Could not create post', bodyText.slice(0, 200));
        return;
      }
      router.back();
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <View style={{ padding: 20, gap: 12 }}>
      <Button title="Pick image" onPress={pickImage} disabled={submitting} />
      {image ? <Image source={{ uri: image.uri }} style={{ width: 200, height: 200 }} /> : null}
      <TextInput
        placeholder="Caption"
        value={caption}
        onChangeText={setCaption}
        style={{ borderWidth: 1, padding: 8 }}
        editable={!submitting}
      />
      <Button title={submitting ? 'Posting…' : 'Post'} onPress={submit} disabled={submitting} />
    </View>
  );
}
