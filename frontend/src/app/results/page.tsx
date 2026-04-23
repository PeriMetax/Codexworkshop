import { fetchJson } from "@/lib/api";

export default async function ResultsPage() {
  const records = await fetchJson<any[]>("/records");

  return (
    <div>
      <h2>Validation Results</h2>
      <table border={1} cellPadding={6}>
        <thead>
          <tr>
            <th>ID</th><th>Platform</th><th>Raw</th><th>Status</th><th>Errors</th><th>Suggested</th><th>Confidence</th>
          </tr>
        </thead>
        <tbody>
          {records.map((r) => (
            <tr key={r.id}>
              <td>{r.id}</td><td>{r.source_platform}</td><td>{r.raw_taxonomy}</td>
              <td>{r.review_status}</td><td>{(r.error_types || []).join(", ")}</td>
              <td>{r.suggested_taxonomy}</td><td>{r.confidence_score}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
