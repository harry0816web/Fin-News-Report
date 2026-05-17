import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import Link from "next/link";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "台灣財經日報",
  description: "每日台灣財經新聞 AI 摘要",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="zh-Hant">
      <body className={`${geistSans.variable} ${geistMono.variable} antialiased bg-gray-50 min-h-screen`}>
        <header className="bg-white border-b border-gray-200 sticky top-0 z-10">
          <div className="max-w-4xl mx-auto px-4 py-3 flex items-center justify-between">
            <nav className="flex items-center gap-4">
              <Link href="/" className="font-bold text-gray-900 hover:text-blue-600">
                📊 台灣財經日報
              </Link>
              <Link href="/history" className="text-sm text-gray-500 hover:text-gray-900">
                歷史
              </Link>
            </nav>
            <Link
              href="/subscribe"
              className="text-sm bg-blue-600 text-white px-3 py-1.5 rounded-lg hover:bg-blue-700 transition-colors"
            >
              訂閱 Email
            </Link>
          </div>
        </header>
        <main className="max-w-4xl mx-auto px-4 py-6">{children}</main>
        <footer className="border-t border-gray-200 mt-12 py-6 text-center text-sm text-gray-400">
          台灣財經日報 — 每天早上 09:00 更新
        </footer>
      </body>
    </html>
  );
}
