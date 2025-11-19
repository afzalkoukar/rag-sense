// app/layout.tsx
import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "BookQ – Ask Your Book",
  description: "Upload a book and ask natural-language questions.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className={`${inter.className} bg-[#071026] text-white min-h-screen antialiased`}>
        <main>{children}</main>
      </body>
    </html>
  );
}
