import { Platform } from "react-native";

const TOKEN_KEY = "scouta_jwt";
const USER_KEY = "scouta_user";

// SecureStore doesn't work on web — use localStorage as fallback
let SecureStore: any = null;

async function getStore() {
  if (Platform.OS !== "web" && !SecureStore) {
    SecureStore = await import("expo-secure-store");
  }
  return SecureStore;
}

export async function saveToken(token: string): Promise<void> {
  const store = await getStore();
  if (store) {
    await store.setItemAsync(TOKEN_KEY, token);
  } else {
    localStorage.setItem(TOKEN_KEY, token);
  }
}

export async function getToken(): Promise<string | null> {
  const store = await getStore();
  if (store) {
    return store.getItemAsync(TOKEN_KEY);
  }
  return localStorage.getItem(TOKEN_KEY);
}

export async function saveUser(user: object): Promise<void> {
  const value = JSON.stringify(user);
  const store = await getStore();
  if (store) {
    await store.setItemAsync(USER_KEY, value);
  } else {
    localStorage.setItem(USER_KEY, value);
  }
}

export async function getUser(): Promise<any | null> {
  const store = await getStore();
  const raw = store
    ? await store.getItemAsync(USER_KEY)
    : localStorage.getItem(USER_KEY);
  if (!raw) return null;
  try {
    return JSON.parse(raw);
  } catch {
    return null;
  }
}

export async function clearAuth(): Promise<void> {
  const store = await getStore();
  if (store) {
    await store.deleteItemAsync(TOKEN_KEY);
    await store.deleteItemAsync(USER_KEY);
  } else {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
  }
}
