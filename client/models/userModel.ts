export type UserRole = "tenant" | "owner" | "admin";

export class User {
  email: string;
  first_name: string;
  last_name: string;
  id: number;
  role: UserRole;
  status: string | null;
  location: string | null;

  constructor(
    email: string,
    first_name: string,
    last_name: string,
    id: number,
    role: UserRole,
    status: string | null = null,
    location: string | null = null
  ) {
    this.email = email;
    this.first_name = first_name;
    this.last_name = last_name;
    this.id = id;
    this.role = role;
    this.status = status;
    this.location = location;
  }

  static fromObject(obj: any): User {
    return new User(
      obj.email,
      obj.first_name,
      obj.last_name,
      obj.id,
      obj.role,
      obj.status ?? null,
      obj.location ?? null
    );
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
      first_name: this.first_name,
      last_name: this.last_name,
      id: this.id,
      role: this.role,
      status: this.status,
      location: this.location,
    };
  }
}