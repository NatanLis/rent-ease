export type UserRole = "tenant" | "owner" | "admin";

export class User {
  email: string;
  id: number;
  role: UserRole;
  status: string | null;
  location: string | null;
  first_name: string;
  last_name: string;
  username: string;
  avatar_url: string | null;
  profile_picture_id: number | null;
  is_active: boolean;
  created_at: string;
  updated_at: string | null;

  constructor(
    email: string,
    id: number,
    role: UserRole,
    first_name: string,
    last_name: string,
    username: string,
    status: string | null = null,
    location: string | null = null,
    avatar_url: string | null = null,
    profile_picture_id: number | null = null,
    is_active: boolean = true,
    created_at: string = '',
    updated_at: string | null = null
  ) {
    this.email = email;
    this.id = id;
    this.role = role;
    this.first_name = first_name;
    this.last_name = last_name;
    this.username = username;
    this.status = status;
    this.location = location;
    this.avatar_url = avatar_url;
    this.profile_picture_id = profile_picture_id;
    this.is_active = is_active;
    this.created_at = created_at;
    this.updated_at = updated_at;
  }

  static fromObject(obj: any): User {
    return new User(
      obj.email,
      obj.id,
      obj.role,
      obj.first_name || '',
      obj.last_name || '',
      obj.username || '',
      obj.status ?? null,
      obj.location ?? null,
      obj.avatar_url ?? null,
      obj.profile_picture_id ?? null,
      obj.is_active ?? true,
      obj.created_at || '',
      obj.updated_at ?? null
    );
  }

  get fullName(): string {
    return `${this.first_name} ${this.last_name}`.trim();
  }

  update(data: Partial<User>) {
    Object.assign(this, data);
  }

  isAdmin(): boolean {
    return this.role === "admin";
  }

  isOwner(): boolean {
    return this.role === "owner";
  }

  isTenant(): boolean {
    return this.role === "tenant";
  }

  toJSON(): Record<string, any> {
    return {
      email: this.email,
      id: this.id,
      role: this.role,
      first_name: this.first_name,
      last_name: this.last_name,
      username: this.username,
      status: this.status,
      location: this.location,
      avatar_url: this.avatar_url,
      profile_picture_id: this.profile_picture_id,
      is_active: this.is_active,
      created_at: this.created_at,
      updated_at: this.updated_at,
    };
  }
}
