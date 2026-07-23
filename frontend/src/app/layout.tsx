import type { Metadata } from 'next';
import { Inter, Geist } from 'next/font/google';
import './globals.css';
import { cn } from "@/lib/utils";

const geist = Geist({subsets:['latin'],variable:'--font-sans'});

const inter = Inter({ subsets: ['latin'], variable: '--font-inter' });

export const metadata: Metadata = {
  title: 'TruthLens AI — Real-Time Fact Verification',
  description:
    'TruthLens AI uses advanced AI and multi-source fact-checking to verify news and images in real time. Powered by Groq, Google Fact Check, and more.',
  openGraph: {
    title: 'TruthLens AI',
    description: 'Real-time AI-powered fact verification platform.',
    images: ['/og-image.png'],
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={cn("dark", "font-sans", geist.variable)}>
      <body className={`${inter.variable} font-sans antialiased bg-[#030712] text-white`}>
        {children}
      </body>
    </html>
  );
}
