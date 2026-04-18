import './globals.css';

export const metadata = {
  title: 'GrowMF Chatbot',
  description: 'Intelligent Mutual Fund Information Assistant',
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <head>
        <meta charSet="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
      </head>
      <body>{children}</body>
    </html>
  );
}
