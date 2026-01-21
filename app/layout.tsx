import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "JBS FFL - John Burroughs School Fantasy Football League",
  description: "The John Burroughs School Fantasy Football League - Running since 1999",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">{children}</body>
    </html>
  );
}
