import Navbar from "./Navbar";
import Footer from "./Footer";

export default function DashboardShell({ children }) {
  return (
    <>
      <Navbar />
      <main className="main-content">
        <div className="container">{children}</div>
      </main>
      <Footer />
    </>
  );
}
