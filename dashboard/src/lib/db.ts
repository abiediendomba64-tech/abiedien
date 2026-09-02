// Compatibility adapter for legacy dashboard code.
// It deliberately does NOT connect to Supabase directly from the browser.
// Operational data must come from the authenticated backend API.
import type { User } from '../types';

const API_BASE_URL = (import.meta.env.VITE_DASHBOARD_API_URL ?? '').replace(/\/$/, '');

export async function dbGetUsers(): Promise<User[]> {
  if (!API_BASE_URL) {
    throw new Error('Dashboard API is not configured; using current dashboard data.');
  }
  const response = await fetch(`${API_BASE_URL}/api/users`, {
    method: 'GET',
    headers: { Accept: 'application/json' },
  });
  if (!response.ok) throw new Error(`Dashboard API returned ${response.status}.`);
  const data = await response.json();
  return Array.isArray(data) ? (data as User[]) : Array.isArray(data?.users) ? (data.users as User[]) : [];
}
