import Navigation from "@/components/Navigation";
import { headToHeadRecords } from "@/data/headToHead";

interface ManagerRecord {
  opponent: string;
  wins: number;
  losses: number;
  ties?: number;
  record: string;
}

interface ManagerData {
  manager: string;
  records: ManagerRecord[];
  totalWins: number;
  totalLosses: number;
  totalTies: number;
  totalGames: number;
  winPercentage: number;
}

export default function HeadToHead() {
  // Ensure we have valid data
  const matchups = Array.isArray(headToHeadRecords) ? headToHeadRecords : [];

  if (matchups.length === 0) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-white to-gray-50">
        <Navigation currentPage="/head-to-head" />
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <h1 className="text-4xl font-bold text-jbsBlue mb-8 text-center">
            Head-to-Head Records
          </h1>
          <div className="bg-white rounded-lg shadow-lg p-8 text-center">
            <p className="text-gray-600">No head-to-head records available.</p>
          </div>
        </main>
      </div>
    );
  }

  // Transform flat array into manager-grouped structure
  const managerDataMap = new Map<string, ManagerData>();

  matchups.forEach((matchup) => {
    const { manager1, manager2, manager1Wins, manager2Wins } = matchup;
    // Ensure ties is a number, defaulting to 0
    const ties = typeof matchup.ties === 'number' ? matchup.ties : 0;

    // Process manager1's record against manager2
    if (!managerDataMap.has(manager1)) {
      managerDataMap.set(manager1, {
        manager: manager1,
        records: [],
        totalWins: 0,
        totalLosses: 0,
        totalTies: 0,
        totalGames: 0,
        winPercentage: 0,
      });
    }
    const mgr1Data = managerDataMap.get(manager1)!;
    mgr1Data.records.push({
      opponent: manager2,
      wins: manager1Wins,
      losses: manager2Wins,
      ties: ties,
      record: ties > 0 ? `${manager1Wins}-${manager2Wins}-${ties}` : `${manager1Wins}-${manager2Wins}`,
    });
    mgr1Data.totalWins += manager1Wins;
    mgr1Data.totalLosses += manager2Wins;
    mgr1Data.totalTies += ties;
    mgr1Data.totalGames += manager1Wins + manager2Wins + ties;

    // Process manager2's record against manager1
    if (!managerDataMap.has(manager2)) {
      managerDataMap.set(manager2, {
        manager: manager2,
        records: [],
        totalWins: 0,
        totalLosses: 0,
        totalTies: 0,
        totalGames: 0,
        winPercentage: 0,
      });
    }
    const mgr2Data = managerDataMap.get(manager2)!;
    mgr2Data.records.push({
      opponent: manager1,
      wins: manager2Wins,
      losses: manager1Wins,
      ties: ties,
      record: ties > 0 ? `${manager2Wins}-${manager1Wins}-${ties}` : `${manager2Wins}-${manager1Wins}`,
    });
    mgr2Data.totalWins += manager2Wins;
    mgr2Data.totalLosses += manager1Wins;
    mgr2Data.totalTies += ties;
    mgr2Data.totalGames += manager2Wins + manager1Wins + ties;
  });

  // Calculate win percentages and sort records
  const managerData: ManagerData[] = Array.from(managerDataMap.values()).map(
    (data) => {
      data.winPercentage =
        data.totalGames > 0
          ? (data.totalWins / data.totalGames) * 100
          : 0;
      // Sort records by total games (most played first)
      data.records.sort(
        (a, b) => b.wins + b.losses - (a.wins + a.losses)
      );
      return data;
    }
  );

  // Sort managers by win percentage (highest to lowest)
  managerData.sort((a, b) => b.winPercentage - a.winPercentage);

  return (
    <div className="min-h-screen bg-gradient-to-br from-white to-gray-50">
      <Navigation currentPage="/head-to-head" />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="mb-12 bg-gradient-to-r from-jbsBlue to-jbsGold rounded-lg shadow-xl p-8 text-white">
          <h1 className="text-4xl font-bold mb-4">Head-to-Head Records</h1>
          <p className="mb-4 text-lg">
            These records track every regular season matchup between managers
            since the league began using ESPN to host. Only regular season games
            are included in these statistics; playoff games are excluded.
          </p>
          <p className="text-sm opacity-90">
            Records are color-coded: green indicates a winning record, red
            indicates a losing record against that opponent.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {managerData.map((manager) => (
            <div
              key={manager.manager}
              className="bg-white rounded-lg shadow-lg overflow-hidden border-l-4 border-jbsBlue hover:shadow-xl transition-shadow"
            >
              {/* Manager Header */}
              <div className="px-6 py-4 bg-gradient-to-r from-jbsBlue to-blue-600 text-white">
                <div className="flex items-center justify-between">
                  <h2 className="text-2xl font-bold">{manager.manager}</h2>
                  <div className="text-right">
                    <div className="text-sm opacity-90">Overall Record</div>
                    <div className="text-lg font-semibold">
                      {manager.totalWins}-{manager.totalLosses}{manager.totalTies > 0 ? `-${manager.totalTies}` : ''}
                    </div>
                    <div className="text-xs opacity-75">
                      {manager.winPercentage.toFixed(1)}% win rate
                    </div>
                  </div>
                </div>
              </div>

              {/* Records Table */}
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Opponent
                      </th>
                      <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Record
                      </th>
                      <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Games
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {manager.records.map((record, index) => {
                      const isWinning = record.wins > record.losses;
                      const isLosing = record.wins < record.losses;
                      return (
                        <tr
                          key={index}
                          className={`hover:bg-gray-50 ${
                            isWinning
                              ? "bg-green-50"
                              : isLosing
                              ? "bg-red-50"
                              : ""
                          }`}
                        >
                          <td className="px-4 py-3 whitespace-nowrap text-sm font-medium text-jbsBlue">
                            {record.opponent}
                          </td>
                          <td className="px-4 py-3 whitespace-nowrap text-sm text-center">
                            <span
                              className={`font-semibold ${
                                isWinning
                                  ? "text-green-700"
                                  : isLosing
                                  ? "text-red-700"
                                  : "text-gray-900"
                              }`}
                            >
                              {record.wins}
                            </span>
                            <span className="mx-2 text-gray-500">-</span>
                            <span
                              className={`font-semibold ${
                                isLosing
                                  ? "text-green-700"
                                  : isWinning
                                  ? "text-red-700"
                                  : "text-gray-900"
                              }`}
                            >
                              {record.losses}
                            </span>
                            {typeof record.ties === 'number' && record.ties > 0 && (
                              <>
                                <span className="mx-2 text-gray-500">-</span>
                                <span className="font-semibold text-gray-700">
                                  {record.ties}
                                </span>
                              </>
                            )}
                          </td>
                          <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-600 text-right">
                            {record.wins + record.losses + (record.ties || 0)}
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </div>
          ))}
        </div>
      </main>
    </div>
  );
}
