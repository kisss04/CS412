import type { Href } from 'expo-router';

/** Central paths until Expo typed routes pick up `app/mini_insta/*`. */
export const miniInstaRoutes = {
  login: '/mini_insta/login' as Href,
  feed: '/mini_insta/feed' as Href,
  newPost: '/mini_insta/new-post' as Href,
  profile: '/mini_insta/profile' as Href,
} as const;
