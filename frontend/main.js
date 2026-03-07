const { useState } = React;

const API_BASE = "http://localhost:8000";

function BaseResumeCard({ resume, onUploaded }) {
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState("");

  async function handleChange(e) {
    const file = e.target.files?.[0];
    if (!file) return;
    setError("");
    setUploading(true);
    try {
      const formData = new FormData();
      formData.append("file", file);
      const res = await fetch(`${API_BASE}/api/resume/base`, {
        method: "POST",
        body: formData,
      });
      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.detail || "Failed to upload resume");
      }
      const data = await res.json();
      onUploaded(data);
    } catch (err) {
      setError(err.message || "Upload failed");
    } finally {
      setUploading(false);
    }
  }

  return (
    <div className="bg-slate-900 border border-slate-700 rounded-xl p-4 flex flex-col gap-3">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold">Base Resume</h2>
          <p className="text-sm text-slate-400">
            Upload a .docx resume that will be used as the source for alignment.
          </p>
        </div>
        <label className="inline-flex items-center px-3 py-2 rounded-lg bg-indigo-500 hover:bg-indigo-400 text-sm font-medium cursor-pointer">
          <span>{uploading ? "Uploading..." : "Upload .docx"}</span>
          <input
            type="file"
            accept=".docx"
            onChange={handleChange}
            className="hidden"
            disabled={uploading}
          />
        </label>
      </div>
      {resume && (
        <p className="text-xs text-slate-400">
          Latest: <span className="font-mono">{resume.file_path}</span>
        </p>
      )}
      {error && <p className="text-xs text-red-400">{error}</p>}
    </div>
  );
}

function JobUrlForm({ onAnalyzed }) {
  const [mode, setMode] = useState("url"); // 'url' or 'text'
  const [url, setUrl] = useState("");
  const [jdText, setJdText] = useState("");
  const [expanded, setExpanded] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(e) {
    e.preventDefault();
    if (mode === "url" && !url) return;
    if (mode === "text" && !jdText.trim()) return;
    setLoading(true);
    setError("");
    try {
      const payload =
        mode === "url"
          ? { url }
          : {
              jd_text: jdText,
            };
      const res = await fetch(`${API_BASE}/api/job/analyze`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.detail || "Failed to analyze job");
      }
      const data = await res.json();
      onAnalyzed(data);
    } catch (err) {
      setError(err.message || "Analysis failed");
    } finally {
      setLoading(false);
    }
  }

  const canSubmit =
    !loading &&
    ((mode === "url" && !!url) || (mode === "text" && !!jdText.trim()));

  return (
    <form
      onSubmit={handleSubmit}
      className="bg-slate-900 border border-slate-700 rounded-xl p-4 flex flex-col gap-3"
    >
      <div className="flex items-center justify-between gap-3">
        <div className="flex-1">
          <h2 className="text-lg font-semibold">Job Description</h2>
          <p className="text-sm text-slate-400">
            Paste a LinkedIn job URL or expand to paste the description
            directly.
          </p>
        </div>
        <button
          type="button"
          onClick={() => {
            setExpanded((v) => !v);
            setMode((prev) => (prev === "url" ? "text" : "url"));
          }}
          className="text-xs text-indigo-400 hover:text-indigo-300 underline"
        >
          {expanded ? "Use URL only" : "Paste description instead"}
        </button>
      </div>
      <div className="flex flex-col gap-3">
        <div className="flex flex-col sm:flex-row gap-3">
          <input
            type="url"
            placeholder="https://www.linkedin.com/jobs/view/..."
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            className="flex-1 rounded-lg bg-slate-950 border border-slate-700 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
        </div>
        {expanded && (
          <textarea
            placeholder="Paste the full job description here (optional alternative to URL)..."
            value={jdText}
            onChange={(e) => setJdText(e.target.value)}
            rows={6}
            className="rounded-lg bg-slate-950 border border-slate-700 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 resize-y"
          />
        )}
        <div className="flex justify-end">
          <button
            type="submit"
            disabled={!canSubmit}
            className="px-4 py-2 rounded-lg bg-emerald-500 hover:bg-emerald-400 disabled:opacity-50 text-sm font-medium"
          >
            {loading ? "Analyzing..." : "Analyze"}
          </button>
        </div>
      </div>
      {error && <p className="text-xs text-red-400">{error}</p>}
    </form>
  );
}

function AlignmentReview({ resume, job, alignment, onAligned }) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [template, setTemplate] = useState("classic");

  async function runAlignment() {
    if (!resume || !job) return;
    setLoading(true);
    setError("");
    try {
      const res = await fetch(`${API_BASE}/api/alignment/run`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          resume_id: resume.id,
          job_id: job.id,
          template,
        }),
      });
      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.detail || "Failed to run alignment");
      }
      const data = await res.json();
      onAligned(data);
    } catch (err) {
      setError(err.message || "Alignment failed");
    } finally {
      setLoading(false);
    }
  }

  function downloadDoc() {
    if (!alignment) return;
    const link = document.createElement("a");
    link.href = `${API_BASE}${alignment.download_url}`;
    link.target = "_blank";
    link.click();
  }

  return (
    <div className="bg-slate-900 border border-slate-700 rounded-xl p-4 flex flex-col gap-3">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold">Alignment Workflow</h2>
          <p className="text-sm text-slate-400">
            Align your resume to this job, choose a template, and preview the
            changes.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <label className="text-xs text-slate-400">Template</label>
          <select
            value={template}
            onChange={(e) => setTemplate(e.target.value)}
            className="rounded-md bg-slate-950 border border-slate-700 px-2 py-1 text-xs focus:outline-none focus:ring-1 focus:ring-indigo-500"
          >
            <option value="classic">Classic</option>
            <option value="modern">Modern</option>
            <option value="compact">Compact</option>
          </select>
        </div>
        <button
          onClick={runAlignment}
          disabled={loading || !resume || !job}
          className="px-4 py-2 rounded-lg bg-sky-500 hover:bg-sky-400 disabled:opacity-50 text-sm font-medium"
        >
          {loading ? "Aligning..." : "Run Alignment"}
        </button>
      </div>
      {!resume && (
        <p className="text-xs text-amber-400">
          Upload a base resume before running alignment.
        </p>
      )}
      {!job && (
        <p className="text-xs text-amber-400">
          Analyze a job URL before running alignment.
        </p>
      )}
      {alignment && (
        <>
          <div className="text-sm text-slate-200">
            <p className="font-semibold mb-1">Hidden Matches Summary</p>
            <p className="text-slate-300">{alignment.hidden_matches_summary}</p>
          </div>
          <div className="text-xs text-slate-400 bg-slate-950 border border-slate-800 rounded-lg p-3 max-h-48 overflow-auto whitespace-pre-wrap">
            {alignment.aligned_resume_preview}
          </div>
          <div className="flex justify-end">
            <button
              onClick={downloadDoc}
              className="px-3 py-2 rounded-lg bg-indigo-500 hover:bg-indigo-400 text-xs font-medium"
            >
              Download Aligned Resume (.docx)
            </button>
          </div>
        </>
      )}
      {error && <p className="text-xs text-red-400">{error}</p>}
    </div>
  );
}

function OutreachPanel({ alignment }) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [outreach, setOutreach] = useState(null);

  async function generate() {
    if (!alignment) return;
    setLoading(true);
    setError("");
    try {
      const res = await fetch(`${API_BASE}/api/outreach/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ alignment_id: alignment.id }),
      });
      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.detail || "Failed to generate outreach");
      }
      const data = await res.json();
      setOutreach(data);
    } catch (err) {
      setError(err.message || "Outreach generation failed");
    } finally {
      setLoading(false);
    }
  }

  function copyToClipboard(text) {
    if (!text) return;
    navigator.clipboard?.writeText(text);
  }

  return (
    <div className="bg-slate-900 border border-slate-700 rounded-xl p-4 flex flex-col gap-3">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold">Outreach Suite</h2>
          <p className="text-sm text-slate-400">
            Generate a cover letter, cold email, and LinkedIn DM.
          </p>
        </div>
        <button
          onClick={generate}
          disabled={loading || !alignment}
          className="px-4 py-2 rounded-lg bg-emerald-500 hover:bg-emerald-400 disabled:opacity-50 text-sm font-medium"
        >
          {loading ? "Generating..." : "Generate Outreach"}
        </button>
      </div>
      {!alignment && (
        <p className="text-xs text-amber-400">
          Run alignment first to enable outreach generation.
        </p>
      )}
      {outreach && (
        <div className="grid gap-3 md:grid-cols-3 text-xs">
          <div className="flex flex-col gap-2">
            <div className="flex items-center justify-between">
              <span className="font-semibold">Cover Letter</span>
              <button
                onClick={() => copyToClipboard(outreach.cover_letter)}
                className="text-[10px] text-indigo-400 hover:text-indigo-300"
              >
                Copy
              </button>
            </div>
            <pre className="bg-slate-950 border border-slate-800 rounded-lg p-2 whitespace-pre-wrap max-h-64 overflow-auto">
              {outreach.cover_letter}
            </pre>
          </div>
          <div className="flex flex-col gap-2">
            <div className="flex items-center justify-between">
              <span className="font-semibold">Email</span>
              <button
                onClick={() => copyToClipboard(outreach.email_template)}
                className="text-[10px] text-indigo-400 hover:text-indigo-300"
              >
                Copy
              </button>
            </div>
            <pre className="bg-slate-950 border border-slate-800 rounded-lg p-2 whitespace-pre-wrap max-h-64 overflow-auto">
              {outreach.email_template}
            </pre>
          </div>
          <div className="flex flex-col gap-2">
            <div className="flex items-center justify-between">
              <span className="font-semibold">LinkedIn DM</span>
              <button
                onClick={() => copyToClipboard(outreach.linkedin_dm)}
                className="text-[10px] text-indigo-400 hover:text-indigo-300"
              >
                Copy
              </button>
            </div>
            <pre className="bg-slate-950 border border-slate-800 rounded-lg p-2 whitespace-pre-wrap max-h-64 overflow-auto">
              {outreach.linkedin_dm}
            </pre>
          </div>
        </div>
      )}
      {error && <p className="text-xs text-red-400">{error}</p>}
    </div>
  );
}

function App() {
  const [resume, setResume] = useState(null);
  const [job, setJob] = useState(null);
  const [alignment, setAlignment] = useState(null);

  return (
    <div className="min-h-screen">
      <header className="border-b border-slate-800 bg-slate-950/80 backdrop-blur">
        <div className="max-w-5xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="h-8 w-8 rounded-full bg-indigo-500 flex items-center justify-center text-sm font-bold">
              CC
            </span>
            <div>
              <h1 className="text-lg font-semibold">Career Co-Pilot</h1>
              <p className="text-xs text-slate-400">
                AI Resume & Outreach Architect
              </p>
            </div>
          </div>
        </div>
      </header>
      <main className="max-w-5xl mx-auto px-4 py-6 flex flex-col gap-4">
        <div className="grid gap-4 md:grid-cols-2">
          <BaseResumeCard resume={resume} onUploaded={setResume} />
          <JobUrlForm onAnalyzed={setJob} />
        </div>
        <AlignmentReview
          resume={resume}
          job={job}
          alignment={alignment}
          onAligned={setAlignment}
        />
        <OutreachPanel alignment={alignment} />
      </main>
    </div>
  );
}

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(<App />);

