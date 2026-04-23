"use client";

import { useState } from "react";

export default function UploadPage() {
  const [message, setMessage] = useState<string>("");

  async function onSubmit(formData: FormData) {
    const res = await fetch(`${process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000/api/v1"}/ingest`, {
      method: "POST",
      body: formData,
    });
    const data = await res.json();
    setMessage(JSON.stringify(data));
  }

  return (
    <div>
      <h2>Upload / Ingest</h2>
      <form action={onSubmit}>
        <div>
          <label>Campaign taxonomy file: </label>
          <input type="file" name="dataset_file" required />
        </div>
        <div>
          <label>Mapping file: </label>
          <input type="file" name="mapping_file" required />
        </div>
        <button type="submit">Ingest</button>
      </form>
      <pre>{message}</pre>
    </div>
  );
}
