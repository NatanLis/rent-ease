export interface UserI {
  id: number;
  email: string;
  role: string;
  status: string | null;
  location: string | null;
  first_name: string;
  last_name: string;
  username: string;
  avatar_url?: string | null;
  profile_picture_id?: number | null;
  is_active: boolean;
  created_at: string;
  updated_at?: string | null;
}
