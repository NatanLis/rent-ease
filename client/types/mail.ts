// types/mail.ts
export interface Message {
    id: string;
    from: string;      // email
    to: string;        // email
    text?: string;
    html?: string;
    date: string;      // ISO
    isOutgoing: boolean;
    subject?: string;
  }
  
  export interface Mail {
    id: string;
    subject: string;
    unread?: boolean;
  
    // Helpful for list UIs (so 'from.name' is safe to read)
    from?: { name: string; email: string };
    to?: { name: string; email: string };
  
    preview?: string;
    date?: string;     // ISO
  
    participants?: string[];
    messages: Message[];
  }
  