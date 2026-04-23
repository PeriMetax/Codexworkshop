"use client";

import { useState } from "react";

export default function RecordDetail({ params }: { params: { id: string } }) {
  const [finalTaxonomy, setFinalTaxonomy] = useState("");
  const [status, setStatus] = useState("");

  async function submit(action: "accept" | "reject" | "amend") {
    const res = await fetch(`${process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000/api/v1"}/records/${params.id}/review`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ reviewer_id: 1, action, final_taxonomy: finalTaxonomy, comments: "Reviewed in UI" }),
    });
    const data = await res.json();
    setStatus(JSON.stringify(data));
  }

  return (
    <div>
      <h2>Record Detail / Edit #{params.id}</h2>
      <input value={finalTaxonomy} onChange={(e) => setFinalTaxonomy(e.target.value)} placeholder="Final taxonomy" />
      <div style={{ display: "flex", gap: 8, marginTop: 8 }}>
        <button onClick={() => submit("accept")}>Accept</button>
        <button onClick={() => submit("amend")}>Amend</button>
        <button onClick={() => submit("reject")}>Reject</button>
      </div>
      <pre>{status}</pre>
    </div>
  );
}
