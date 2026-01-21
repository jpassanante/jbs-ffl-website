import Link from "next/link";

export default function Schedule() {
  // Sample schedule data - replace with your actual data
  const weeks = [
    {
      week: 1,
      matchups: [
        { team1: "Team Alpha", team2: "Team Beta", score1: 120, score2: 95 },
        { team1: "Team Gamma", team2: "Team Delta", score1: 110, score2: 105 },
        { team1: "Team Epsilon", team2: "Team Zeta", score1: 98, score2: 102 },
      ],
    },
    {
      week: 2,
      matchups: [
        { team1: "Team Alpha", team2: "Team Gamma", score1: null, score2: null },
        { team1: "Team Beta", team2: "Team Delta", score1: null, score2: null },
        { team1: "Team Epsilon", team2: "Team Zeta", score1: null, score2: null },
      ],
    },
    {
      week: 3,
      matchups: [
        { team1: "Team Alpha", team2: "Team Delta", score1: null, score2: null },
        { team1: "Team Beta", team2: "Team Epsilon", score1: null, score2: null },
        { team1: "Team Gamma", team2: "Team Zeta", score1: null, score2: null },
      ],
    },
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
                className="text-gray-700 dark:text-gray-300 hover:text-indigo-600 dark:hover:text-indigo-400 px-3 py-2 rounded-md text-sm font-medium"
              >
                Teams
              </Link>
              <Link
                href="/schedule"
                className="text-indigo-600 dark:text-indigo-400 px-3 py-2 rounded-md text-sm font-medium"
              >
                Schedule
              </Link>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-8">Schedule</h1>
        
        <div className="space-y-8">
          {weeks.map((weekData) => (
            <div key={weekData.week} className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
              <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-4">
                Week {weekData.week}
              </h2>
              <div className="space-y-4">
                {weekData.matchups.map((matchup, idx) => (
                  <div
                    key={idx}
                    className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700 rounded-lg"
                  >
                    <div className="flex-1 text-right">
                      <span className="text-lg font-medium text-gray-900 dark:text-white">
                        {matchup.team1}
                      </span>
                      {matchup.score1 !== null && (
                        <span className="ml-2 text-lg font-bold text-indigo-600 dark:text-indigo-400">
                          {matchup.score1}
                        </span>
                      )}
                    </div>
                    <div className="px-4 text-gray-500 dark:text-gray-400">vs</div>
                    <div className="flex-1 text-left">
                      {matchup.score2 !== null && (
                        <span className="mr-2 text-lg font-bold text-indigo-600 dark:text-indigo-400">
                          {matchup.score2}
                        </span>
                      )}
                      <span className="text-lg font-medium text-gray-900 dark:text-white">
                        {matchup.team2}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </main>
    </div>
  );
}
