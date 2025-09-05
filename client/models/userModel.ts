export type UserRole = "tenant" | "owner" | "admin";

export class User {
  email: string;
  id: number;
  role: UserRole;
  status: string | null;
  location: string | null;
  firstName?: string;
  lastName?: string;
  avatar?: {
    src: string;
  };
  createdAt?: string;

  constructor(
    email: string,
    id: number,
    role: UserRole,
    status: string | null = null,
    location: string | null = null,
    firstName?: string,
    lastName?: string,
    avatar?: {
      src: string;
    },
    createdAt?: string
  ) {
    this.email = email;
    this.id = id;
    this.role = role;
    this.status = status;
    this.location = location;
    this.firstName = firstName;
    this.lastName = lastName;
    this.avatar = avatar;
    this.createdAt = createdAt;
  }

  static fromObject(obj: any): User {
    return new User(
      obj.email,
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
      id: this.id,
      role: this.role,
      status: this.status,
      location: this.location,
    };
  }
}
