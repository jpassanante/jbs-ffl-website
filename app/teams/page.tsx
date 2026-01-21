import Link from "next/link";

export default function Teams() {
  // Sample teams data - replace with your actual data
  const teams = [
    { id: 1, name: "Team Alpha", owner: "John Doe", wins: 10, losses: 2 },
    { id: 2, name: "Team Beta", owner: "Jane Smith", wins: 9, losses: 3 },
    { id: 3, name: "Team Gamma", owner: "Bob Johnson", wins: 8, losses: 4 },
    { id: 4, name: "Team Delta", owner: "Alice Williams", wins: 7, losses: 5 },
    { id: 5, name: "Team Epsilon", owner: "Charlie Brown", wins: 6, losses: 6 },
    { id: 6, name: "Team Zeta", owner: "Diana Prince", wins: 5, losses: 7 },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
      <nav className="bg-white dark:bg-gray-800 shadow-md">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <Link href="/" className="text-2xl font-bold text-indigo-600 dark:text-indigo-400">
                Fantasy Football League
              </Link>
            </div>
            <div className="flex items-center space-x-4">
              <Link
                href="/standings"
                className="text-gray-700 dark:text-gray-300 hover:text-indigo-600 dark:hover:text-indigo-400 px-3 py-2 rounded-md text-sm font-medium"
              >
                Standings
              </Link>
              <Link
                href="/teams"
                className="text-indigo-600 dark:text-indigo-400 px-3 py-2 rounded-md text-sm font-medium"
              >
                Teams
              </Link>
              <Link
                href="/schedule"
                className="text-gray-700 dark:text-gray-300 hover:text-indigo-600 dark:hover:text-indigo-400 px-3 py-2 rounded-md text-sm font-medium"
              >
                Schedule
              </Link>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-8">Teams</h1>
        
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {teams.map((team) => (
            <div
              key={team.id}
              className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 hover:shadow-xl transition-shadow"
            >
              <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-2">
                {team.name}
              </h2>
              <p className="text-gray-600 dark:text-gray-400 mb-4">Owner: {team.owner}</p>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-500 dark:text-gray-400">
                  Record: {team.wins}-{team.losses}
                </span>
                <span className="text-sm font-medium text-indigo-600 dark:text-indigo-400">
                  {((team.wins / (team.wins + team.losses)) * 100).toFixed(1)}% Win Rate
                </span>
              </div>
            </div>
          ))}
        </div>
      </main>
    </div>
  );
}
