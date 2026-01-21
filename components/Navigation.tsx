import Link from "next/link";

export default function Navigation({ currentPage }: { currentPage?: string }) {
  const navItems = [
    { href: "/", label: "Home" },
    { href: "/championship-history", label: "Championship History" },
    { href: "/power-rankings", label: "Power Rankings" },
    { href: "/all-time-records", label: "All-Time Records" },
    { href: "/head-to-head", label: "Head-to-Head" },
    { href: "/trophy-room", label: "Trophy Room" },
  ];

  return (
    <nav className="bg-jbsBlue shadow-lg">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center">
            <Link href="/" className="text-2xl font-bold text-jbsGold hover:text-white transition-colors">
              JBS FFL
            </Link>
            <span className="ml-3 text-sm text-white/80">Since 1999</span>
          </div>
          <div className="flex items-center space-x-1">
            {navItems.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                  currentPage === item.href
                    ? "bg-jbsGold text-jbsBlue"
                    : "text-white hover:bg-white/20"
                }`}
              >
                {item.label}
              </Link>
            ))}
          </div>
        </div>
      </div>
    </nav>
  );
}
