import { ReactNode } from "react";
import { Nav } from "@/components/Nav";

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html>
      <body style={{ fontFamily: "Arial, sans-serif", padding: 20 }}>
        <h1>Taxonomy Validator</h1>
        <Nav />
        {children}
      </body>
    </html>
  );
}
