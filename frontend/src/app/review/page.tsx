import Link from "next/link";
import { fetchJson } from "@/lib/api";

export default async function ReviewPage() {
  const records = await fetchJson<any[]>("/records?status=pending_review");
  return (
    <div>
      <h2>Review Queue</h2>
      <p>Rows requiring human review: {records.length}</p>
      <ul>
        {records.map((r) => (
          <li key={r.id}><Link href={`/record/${r.id}`}>Record {r.id}</Link> - {(r.error_types || []).join(", ")}</li>
        ))}
      </ul>
    </div>
  );
}
