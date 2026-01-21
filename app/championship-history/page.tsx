import Navigation from "@/components/Navigation";
import { getChampionshipsByYear, getAllChampions, getChampionshipLeaderboard, getBackToBackChampions } from "@/data/champions";

export default function ChampionshipHistory() {
  const championships = getChampionshipsByYear(true); // Get newest first
  const uniqueChampions = getAllChampions();
  const leaderboard = getChampionshipLeaderboard();
  const backToBackChampions = getBackToBackChampions();

  return (
    <div className="min-h-screen bg-gradient-to-br from-white to-gray-50">
      <Navigation currentPage="/championship-history" />
      
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <h1 className="text-4xl font-bold text-jbsBlue mb-8 text-center">
          Championship History
        </h1>
        
        {/* Top Stats Callouts */}
        <div className="mb-8 grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white rounded-lg shadow-lg p-6 text-center border-t-4 border-jbsBlue flex flex-col justify-center items-center">
            <div className="text-3xl font-bold text-jbsBlue mb-2">27</div>
            <div className="text-gray-600">Seasons</div>
          </div>
          
          <div className="bg-white rounded-lg shadow-lg p-6 text-center border-t-4 border-jbsGold flex flex-col justify-center items-center">
            <div className="text-3xl font-bold text-jbsGold mb-2">{uniqueChampions.length}</div>
            <div className="text-gray-600">Different Champions</div>
          </div>
          
          {backToBackChampions.length > 0 && (
            <div className="bg-white rounded-lg shadow-lg p-6 border-t-4 border-jbsBlue flex flex-col justify-center items-center text-center">
              <h3 className="text-lg font-semibold text-jbsBlue mb-3">Back-to-Back Champions</h3>
              <div className="space-y-2">
                {backToBackChampions.map((streak, index) => (
                  <div key={index} className="text-center">
                    <span className="font-semibold text-gray-900">{streak.manager}</span>
                    <span className="text-gray-600">: {streak.startYear}-{streak.endYear}</span>
                    {streak.count > 2 && (
                      <span className="text-jbsGold font-bold ml-1">({streak.count} in a row!)</span>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
          {/* All-Time Leaderboard - Left Side */}
          <div className="lg:col-span-3 bg-white rounded-lg shadow-lg overflow-hidden">
            <div className="px-4 py-3 bg-jbsBlue text-white">
              <h2 className="text-lg font-semibold">All-Time Leaderboard</h2>
              <p className="text-xs opacity-90">Championships</p>
            </div>
            <div className="p-4">
              <div className="space-y-2">
                {leaderboard.map((manager, index) => {
                  // Determine rank (handle ties)
                  const rank = index > 0 && leaderboard[index - 1].count === manager.count 
                    ? null 
                    : index + 1;
                  
                  return (
                    <div
                      key={manager.name}
                      className="flex items-center justify-between p-2 bg-gray-50 rounded hover:bg-gray-100 transition-colors"
                    >
                      <div className="flex items-center space-x-2 min-w-0 flex-1">
                        <div className="w-6 text-center flex-shrink-0">
                          {rank !== null ? (
                            <span className={`text-sm font-bold ${
                              rank === 1 ? "text-jbsGold" : 
                              rank === 2 ? "text-gray-400" : 
                              rank === 3 ? "text-amber-600" : 
                              "text-gray-500"
                            }`}>
                              {rank}
                            </span>
                          ) : (
                            <span className="text-gray-400 text-xs">—</span>
                          )}
                        </div>
                        <div className="flex items-center min-w-0">
                          {rank === 1 && (
                            <span className="text-jbsGold text-sm mr-1">👑</span>
                          )}
                          <span className="text-sm font-semibold text-gray-900 truncate">
                            {manager.name}
                          </span>
                        </div>
                      </div>
                      <div className="flex items-center space-x-1 flex-shrink-0 ml-2">
                        <span className="text-lg font-bold text-jbsBlue">
                          {manager.count}
                        </span>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>

          {/* Championship History Table - Right Side */}
          <div className="lg:col-span-9 bg-white rounded-lg shadow-lg overflow-hidden">
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-jbsBlue text-white">
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider">
                      Year
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider">
                      Champion
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider">
                      Playoff Runner-Up
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider">
                      Playoff Third Place
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider">
                      Regular Season Champion
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider">
                      Other Division Champ
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider">
                      Most Points
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {championships.map((champ) => (
                    <tr key={champ.year} className="hover:bg-gray-50">
                      <td className="px-4 py-4 whitespace-nowrap">
                        <span className="text-lg font-bold text-jbsBlue">
                          {champ.year}
                        </span>
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <span className="text-jbsGold text-xl mr-2">👑</span>
                          <span className="text-sm font-semibold text-gray-900">
                            {champ.champion}
                          </span>
                        </div>
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-700">
                        {champ.runnerUp || "—"}
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-600">
                        {champ.thirdPlace || "—"}
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-700">
                        {champ.regularSeasonChamp || "—"}
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-700">
                        {champ.otherDivisionChamp || "—"}
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-700">
                        {champ.regularSeasonMostPoints || "—"}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
