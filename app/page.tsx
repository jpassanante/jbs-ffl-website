import Link from "next/link";
import Image from "next/image";
import Navigation from "@/components/Navigation";

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-white to-gray-50">
      <Navigation currentPage="/" />
      
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="text-center mb-16">
          <h1 className="text-5xl md:text-6xl font-extrabold text-jbsBlue mb-4">
            JBS Fantasy Football League
          </h1>
          <p className="text-xl text-gray-700 mb-2">
            John Burroughs School Fantasy Football League
          </p>
          <p className="text-lg text-gray-600">
            Established 1999 • 27 Seasons • 10 Managers
          </p>
        </div>

        <div className="flex justify-center mb-12">
          <div className="relative w-full max-w-4xl">
            <Image
              src="/league-photo.jpg"
              alt="JBS Fantasy Football League"
              width={1200}
              height={800}
              className="rounded-lg shadow-xl object-cover w-full h-auto"
              unoptimized
            />
          </div>
        </div>

        <div className="grid grid-cols-1 gap-8 md:grid-cols-2 lg:grid-cols-5 mb-12">
          <Link
            href="/championship-history"
            className="bg-white rounded-lg shadow-lg p-6 hover:shadow-xl transition-all hover:scale-105 border-2 border-transparent hover:border-jbsGold"
          >
            <div className="text-center">
              <div className="text-5xl mb-4">👑</div>
              <h3 className="text-xl font-semibold text-jbsBlue mb-2">
                Championship History
              </h3>
              <p className="text-gray-600 text-sm">
                All 27 seasons of champions
              </p>
            </div>
          </Link>

          <Link
            href="/power-rankings"
            className="bg-white rounded-lg shadow-lg p-6 hover:shadow-xl transition-all hover:scale-105 border-2 border-transparent hover:border-jbsGold"
          >
            <div className="text-center">
              <div className="text-5xl mb-4">📈</div>
              <h3 className="text-xl font-semibold text-jbsBlue mb-2">
                Power Rankings
              </h3>
              <p className="text-gray-600 text-sm">
                Weekly power rankings by season
              </p>
            </div>
          </Link>

          <Link
            href="/all-time-records"
            className="bg-white rounded-lg shadow-lg p-6 hover:shadow-xl transition-all hover:scale-105 border-2 border-transparent hover:border-jbsGold"
          >
            <div className="text-center">
              <div className="text-5xl mb-4">📊</div>
              <h3 className="text-xl font-semibold text-jbsBlue mb-2">
                All-Time Records
              </h3>
              <p className="text-gray-600 text-sm">
                League records and statistics
              </p>
            </div>
          </Link>

          <Link
            href="/head-to-head"
            className="bg-white rounded-lg shadow-lg p-6 hover:shadow-xl transition-all hover:scale-105 border-2 border-transparent hover:border-jbsGold"
          >
            <div className="text-center">
              <div className="text-5xl mb-4">⚔️</div>
              <h3 className="text-xl font-semibold text-jbsBlue mb-2">
                Head-to-Head
              </h3>
              <p className="text-gray-600 text-sm">
                Manager vs Manager records
              </p>
            </div>
          </Link>

          <Link
            href="/trophy-room"
            className="bg-white rounded-lg shadow-lg p-6 hover:shadow-xl transition-all hover:scale-105 border-2 border-transparent hover:border-jbsGold"
          >
            <div className="text-center">
              <div className="text-5xl mb-4">🏆</div>
              <h3 className="text-xl font-semibold text-jbsBlue mb-2">
                Trophy Room
              </h3>
              <p className="text-gray-600 text-sm">
                View the championship trophy in 3D
              </p>
            </div>
          </Link>
        </div>

        <div className="bg-gradient-to-r from-jbsBlue to-jbsGold rounded-lg shadow-xl p-8 text-white">
          <h2 className="text-3xl font-bold mb-4">League Legacy</h2>
          <p className="text-lg mb-4">
            The JBS Fantasy Football League has been a tradition for the JBS class of 2003 since 1999. 
            Over 27 seasons, 10 dedicated managers have competed for the championship trophy, 
            creating lasting memories and friendly rivalries.
          </p>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-6">
            <div className="text-center">
              <div className="text-4xl font-bold">27</div>
              <div className="text-sm opacity-90">Seasons</div>
            </div>
            <div className="text-center">
              <div className="text-4xl font-bold">10</div>
              <div className="text-sm opacity-90">Managers</div>
            </div>
            <div className="text-center">
              <div className="text-4xl font-bold">1999</div>
              <div className="text-sm opacity-90">Established</div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
