"use client";
import { useState } from "react";

export default function SyncPage() {
  const [recordIds, setRecordIds] = useState("1");
  const [dryRun, setDryRun] = useState(true);
  const [output, setOutput] = useState("");

  async function runSync() {
    const ids = recordIds.split(",").map((v) => Number(v.trim())).filter(Boolean);
    const res = await fetch(`${process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000/api/v1"}/sync`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ platform: "meta", dry_run: dryRun, record_ids: ids }),
    });
    setOutput(JSON.stringify(await res.json()));
  }

  return (
    <div>
      <h2>Sync Status</h2>
      <input value={recordIds} onChange={(e) => setRecordIds(e.target.value)} />
      <label>
        <input type="checkbox" checked={dryRun} onChange={(e) => setDryRun(e.target.checked)} /> Dry run
      </label>
      <button onClick={runSync}>Start Sync</button>
      <pre>{output}</pre>
    </div>
  );
}
