import { Link } from 'react-router-dom'

export default function Home() {
  return (
    <div className="space-y-12">
      {/* 히어로 */}
      <section className="py-16 text-center">
        <h1 className="mb-4 text-4xl font-bold text-gray-900">
          AI Archive
        </h1>
        <p className="mb-8 text-lg text-gray-600">
          충북대학교 프로젝트 아카이브 — 자연어로 탐색하고, AI로 추천받으세요.
        </p>
        <div className="flex justify-center gap-4">
          <Link
            to="/projects"
            className="rounded-lg bg-primary-600 px-6 py-3 text-white hover:bg-primary-700"
          >
            프로젝트 탐색
          </Link>
          <Link
            to="/chat"
            className="rounded-lg border border-primary-600 px-6 py-3 text-primary-600 hover:bg-primary-50"
          >
            AI 탐색 시작
          </Link>
        </div>
      </section>

      {/* 최신 프로젝트 섹션 (placeholder) */}
      <section>
        <h2 className="mb-4 text-xl font-semibold text-gray-800">최신 프로젝트</h2>
        <p className="text-gray-500">API 연동 후 프로젝트 카드가 표시됩니다.</p>
      </section>
    </div>
  )
}
