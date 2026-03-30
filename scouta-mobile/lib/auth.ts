import * as SecureStore from "expo-secure-store";
import { Platform } from "react-native";

const TOKEN_KEY = "scouta_jwt";
const USER_KEY = "scouta_user";

const isWeb = Platform.OS === "web";

export async function saveToken(token: string): Promise<void> {
  if (isWeb) {
    localStorage.setItem(TOKEN_KEY, token);
  } else {
    await SecureStore.setItemAsync(TOKEN_KEY, token);
  }
}

export async function getToken(): Promise<string | null> {
  if (isWeb) {
    return localStorage.getItem(TOKEN_KEY);
  }
  return SecureStore.getItemAsync(TOKEN_KEY);
}

export async function saveUser(user: object): Promise<void> {
  const value = JSON.stringify(user);
  if (isWeb) {
    localStorage.setItem(USER_KEY, value);
  } else {
    await SecureStore.setItemAsync(USER_KEY, value);
  }
}

export async function getUser(): Promise<any | null> {
  const raw = isWeb
    ? localStorage.getItem(USER_KEY)
    : await SecureStore.getItemAsync(USER_KEY);
  if (!raw) return null;
  try {
    return JSON.parse(raw);
  } catch {
    return null;
  }
}

export async function clearAuth(): Promise<void> {
  if (isWeb) {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
  } else {
    await SecureStore.deleteItemAsync(TOKEN_KEY);
    await SecureStore.deleteItemAsync(USER_KEY);
  }
}
