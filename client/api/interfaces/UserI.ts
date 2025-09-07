export interface UserI {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  role: string;
  status: string | null;
  location: string | null;
}