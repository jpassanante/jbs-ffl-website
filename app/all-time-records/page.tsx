import Navigation from "@/components/Navigation";
import { allTimeRecords } from "@/data/allTimeRecords";

export default function AllTimeRecords() {
  const records = allTimeRecords;

  return (
    <div className="min-h-screen bg-gradient-to-br from-white to-gray-50">
      <Navigation currentPage="/all-time-records" />
      
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="mb-12 bg-gradient-to-r from-jbsBlue to-jbsGold rounded-lg shadow-xl p-8 text-white">
          <h1 className="text-4xl font-bold mb-4">All-Time Records</h1>
          <p className="mb-4 text-lg">
            These records represent the greatest achievements in JBS FFL history. 
            From dominant seasons to incredible single-game performances, these 
            managers have left their mark on the league.
          </p>
          <p className="mb-2 text-base font-semibold">
            All statistics reflect regular season games only (playoffs excluded).
          </p>
          <p className="text-sm opacity-90">
            As of January 2026
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {records.map((record, index) => (
            <div
              key={index}
              className="bg-white rounded-lg shadow-lg p-6 border-l-4 border-jbsGold hover:shadow-xl transition-shadow"
            >
              <h3 className="text-lg font-semibold text-jbsBlue mb-4">
                {record.category}
              </h3>
              
              {/* Top 5 list display */}
              <div className="space-y-3">
                {record.top5.map((entry: any) => (
                  <div
                    key={entry.rank}
                    className={`flex items-center justify-between p-3 rounded-lg ${
                      entry.rank === 1
                        ? "bg-gradient-to-r from-jbsGold/20 to-jbsGold/10 border-2 border-jbsGold"
                        : "bg-gray-50 border border-gray-200"
                    }`}
                  >
                    <div className="flex items-center gap-3">
                      <span
                        className={`text-lg font-bold ${
                          entry.rank === 1 ? "text-jbsGold" : "text-gray-400"
                        }`}
                      >
                        #{entry.rank}
                      </span>
                      <div>
                        <div className="font-semibold text-jbsBlue">
                          {entry.holder}
                        </div>
                        <div className="text-xs text-gray-500">
                          {entry.details}
                        </div>
                      </div>
                    </div>
                    <div className="text-lg font-bold text-jbsGold">
                      {entry.record}
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
